#!/usr/bin/python

MSG_DISCONNECT, MSG_IGNORE, MSG_UNIMPLEMENTED, MSG_DEBUG, MSG_SERVICE_REQUEST, \
	MSG_SERVICE_ACCEPT = range(1, 7)
MSG_KEXINIT, MSG_NEWKEYS = range(20, 22)
MSG_USERAUTH_REQUEST, MSG_USERAUTH_FAILURE, MSG_USERAUTH_SUCCESS, \
        MSG_USERAUTH_BANNER = range(50, 54)
MSG_USERAUTH_PK_OK = 60
MSG_CHANNEL_OPEN, MSG_CHANNEL_OPEN_SUCCESS, MSG_CHANNEL_OPEN_FAILURE, \
	MSG_CHANNEL_WINDOW_ADJUST, MSG_CHANNEL_DATA, MSG_CHANNEL_EXTENDED_DATA, \
	MSG_CHANNEL_EOF, MSG_CHANNEL_CLOSE, MSG_CHANNEL_REQUEST, \
	MSG_CHANNEL_SUCCESS, MSG_CHANNEL_FAILURE = range(90, 101)


import sys, os, string, threading, socket, logging, struct
from message import Message
from channel import Channel
from secsh import SSHException
from util import format_binary, safe_string, inflate_long, deflate_long
from rsakey import RSAKey
from dsskey import DSSKey
from kex_group1 import KexGroup1
from kex_gex import KexGex

# these come from PyCrypt
#     http://www.amk.ca/python/writing/pycrypt/
# i believe this on the standards track.
from Crypto.Util.randpool import PersistentRandomPool
from Crypto.Cipher import Blowfish, AES, DES3
from Crypto.Hash import SHA, MD5, HMAC
from Crypto.PublicKey import RSA

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


# channel request failed reasons:
CONNECTION_FAILED_CODE = {
    1: 'Administratively prohibited',
    2: 'Connect failed',
    3: 'Unknown channel type',
    4: 'Resource shortage'
}


# keep a crypto-strong PRNG nearby
randpool = PersistentRandomPool(os.getenv('HOME') + '/.randpool')
randpool.randomize()


class Transport(threading.Thread):
    '''
    An SSH Transport attaches to a stream (usually a socket), negotiates an
    encrypted session, authenticates, and then creates stream tunnels, called
    "channels", across the session.  Multiple channels can be multiplexed
    across a single session (and often are, in the case of port forwardings).

    Transport expects to receive a "socket-like object" to talk to the SSH
    server.  This means it has a method "settimeout" which sets a timeout for
    read/write calls, and a method "send()" to write bytes and "recv()" to
    read bytes.  "recv" returns from 1 to n bytes, or 0 if the stream has been
    closed.  EOFError may also be raised on a closed stream.  (A return value
    of 0 is converted to an EOFError internally.)  "send(s)" writes from 1 to
    len(s) bytes, and returns the number of bytes written, or returns 0 if the
    stream has been closed.  As with instream, EOFError may be raised instead
    of returning 0.

    FIXME: Describe events here.
    '''

    PROTO_ID = '2.0'
    CLIENT_ID = 'pyssh_1.1'

    preferred_ciphers = [ 'aes128-cbc', 'blowfish-cbc', 'aes256-cbc', '3des-cbc' ]
    preferred_macs = [ 'hmac-sha1', 'hmac-md5', 'hmac-sha1-96', 'hmac-md5-96' ]
    preferred_keys = [ 'ssh-rsa', 'ssh-dss' ]
    preferred_kex = [ 'diffie-hellman-group1-sha1', 'diffie-hellman-group-exchange-sha1' ]

    cipher_info = {
        'blowfish-cbc': { 'class': Blowfish, 'mode': Blowfish.MODE_CBC, 'block-size': 8, 'key-size': 16 },
        'aes128-cbc': { 'class': AES, 'mode': AES.MODE_CBC, 'block-size': 16, 'key-size': 16 },
        'aes256-cbc': { 'class': AES, 'mode': AES.MODE_CBC, 'block-size': 16, 'key-size': 32 },
        '3des-cbc': { 'class': DES3, 'mode': DES3.MODE_CBC, 'block-size': 8, 'key-size': 24 },
        }

    mac_info = {
        'hmac-sha1': { 'class': SHA, 'size': 20 },
        'hmac-sha1-96': { 'class': SHA, 'size': 12 },
        'hmac-md5': { 'class': MD5, 'size': 16 },
        'hmac-md5-96': { 'class': MD5, 'size': 12 },
        }

    kex_info = {
        'diffie-hellman-group1-sha1': KexGroup1,
        'diffie-hellman-group-exchange-sha1': KexGex,
        }

    def __init__(self, sock, event=None):
        threading.Thread.__init__(self)
        self.randpool = randpool
        self.sock = sock
        self.sock.settimeout(0.1)
        self.client_version = 'SSH-' + self.PROTO_ID + '-' + self.CLIENT_ID
        self.server_version = ''
        self.block_size_out = self.block_size_in = 8
        self.client_mac_len = self.server_mac_len = 0
        self.engine_in = self.engine_out = None
        self.client_cipher = self.server_cipher = ''
        self.sequence_number_in = self.sequence_number_out = 0L
        self.client_kex_init = self.server_kex_init = None
        self.expected_packet = 0
        self.active = 0
        self.initial_kex_done = 0
        self.write_lock = threading.Lock()	# lock around outbound writes (packet computation)
        self.lock = threading.Lock()		# synchronization (always higher level than write_lock)
        self.completion_event = event
        self.auth_event = None
        self.authenticated = 0
        self.channels = { }			# (id -> Channel)
        self.channel_events = { }		# (id -> Event)
        self.channel_counter = 1
        self.logger = logging.getLogger('secsh.transport')
        self.window_size = 65536
        self.max_packet_size = 2048
        self.ultra_debug = 0
        self.session_id = None
        self.start()

    def __repr__(self):
        if not self.active:
            return '<secsh.Transport (unconnected)>'
        out = '<sesch.Transport'
        #if self.server_version != '':
        #    out += ' (server version "%s")' % self.server_version
        if self.client_cipher != '':
            out += ' (cipher %s)' % self.client_cipher
        if self.authenticated:
            if len(self.channels) == 1:
                out += ' (active; 1 open channel)'
            else:
                out += ' (active; %d open channels)' % len(self.channels)
        elif self.initial_kex_done:
            out += ' (connected; awaiting auth)'
        else:
            out += ' (connecting)'
        out += '>'
        return out

    def log(self, level, msg):
        if type(msg) == type([]):
            for m in msg:
                self.logger.log(level, m)
        else:
            self.logger.log(level, msg)

    def close(self):
        self.active = 0
        self.engine_in = self.engine_out = None
        self.sequence_number_in = self.sequence_number_out = 0L
        for chan in self.channels.values():
            chan.unlink()

    def get_host_key(self):
        'returns (type, key) where type is like "ssh-rsa" and key is an opaque string'
        if (not self.active) or (not self.initial_kex_done):
            raise SSHException('No existing session')
        key_msg = Message(self.host_key)
        key_type = key_msg.get_string()
        return key_type, self.host_key

    def request_auth(self):
        m = Message()
        m.add_byte(chr(MSG_SERVICE_REQUEST))
        m.add_string('ssh-userauth')
        self.send_message(m)

    def auth_key(self, username, key, event):
        if (not self.active) or (not self.initial_kex_done):
            # we should never try to send the password unless we're on a secure link
            raise SSHException('No existing session')
        try:
            self.lock.acquire()
            self.auth_event = event
            self.auth_method = 'publickey'
            self.username = username
            self.private_key = key
            self.request_auth()
        finally:
            self.lock.release()

    def auth_password(self, username, password, event):
        'authenticate using a password; event is triggered on success or fail'
        if (not self.active) or (not self.initial_kex_done):
            # we should never try to send the password unless we're on a secure link
            raise SSHException('No existing session')
        try:
            self.lock.acquire()
            self.auth_event = event
            self.auth_method = 'password'
            self.username = username
            self.password = password
            self.request_auth()
        finally:
            self.lock.release()

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated and self.active

    def open_session(self):
        return self.open_channel('session')

    def open_channel(self, kind):
        chan = None
        try:
            self.lock.acquire()
            chanid = self.channel_counter
            self.channel_counter += 1
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_OPEN))
            m.add_string(kind)
            m.add_int(chanid)
            m.add_int(self.window_size)
            m.add_int(self.max_packet_size)
            self.channels[chanid] = chan = Channel(chanid, self)
            self.channel_events[chanid] = event = threading.Event()
            chan.set_window(self.window_size, self.max_packet_size)
            self.send_message(m)
        finally:
            self.lock.release()
        while 1:
            event.wait(0.1);
            if not self.active:
                return None
            if event.isSet():
                break
        try:
            self.lock.acquire()
            if not self.channels.has_key(chanid):
                chan = None
        finally:
            self.lock.release()
        return chan

    def unlink_channel(self, chanid):
        try:
            self.lock.acquire()
            if self.channels.has_key(chanid):
                del self.channels[chanid]
        finally:
            self.lock.release()

    def read_all(self, n):
        out = ''
        while n > 0:
            try:
                x = self.sock.recv(n)
                if len(x) == 0:
                    raise EOFError()
                out += x
                n -= len(x)
            except socket.timeout:
                if not self.active:
                    raise EOFError()
        return out

    def write_all(self, out):
        while len(out) > 0:
            n = self.sock.send(out)
            if n <= 0:
                raise EOFError()
            if n == len(out):
                return
            out = out[n:]
        return

    def build_packet(self, payload):
        # pad up at least 4 bytes, to nearest block-size (usually 8)
        bsize = self.block_size_out
        padding = 3 + bsize - ((len(payload) + 8) % bsize)
        packet = struct.pack('>I', len(payload) + padding + 1)
        packet += chr(padding)
        packet += payload
        packet += randpool.get_bytes(padding)
        return packet

    def send_message(self, data):
        # encrypt this sucka
        packet = self.build_packet(str(data))
        if self.ultra_debug:
            self.log(DEBUG, format_binary(packet, 'OUT: '))
        if self.engine_out != None:
            out = self.engine_out.encrypt(packet)
        else:
            out = packet
        # + mac
        try:
            self.write_lock.acquire()
            if self.engine_out != None:
                payload = struct.pack('>I', self.sequence_number_out) + packet
                out += HMAC.HMAC(self.mac_key_out, payload, self.client_mac_engine).digest()[:self.client_mac_len]
            self.sequence_number_out += 1L
            self.sequence_number_out %= 0x100000000L
            self.write_all(out)
        finally:
            self.write_lock.release()

    def read_message(self):
        "only one thread will ever be in this function"
        header = self.read_all(self.block_size_in)
        if self.engine_in != None:
            header = self.engine_in.decrypt(header)
        if self.ultra_debug:
            self.log(DEBUG, format_binary(header, 'IN: '));
        packet_size = struct.unpack('>I', header[:4])[0]
        # leftover contains decrypted bytes from the first block (after the length field)
        leftover = header[4:]
        if (packet_size - len(leftover)) % self.block_size_in != 0:
            raise SSHException('Invalid packet blocking')
        buffer = self.read_all(packet_size + self.server_mac_len - len(leftover))
        packet = buffer[:packet_size - len(leftover)]
        post_packet = buffer[packet_size - len(leftover):]
        if self.engine_in != None:
            packet = self.engine_in.decrypt(packet)
        if self.ultra_debug:
            self.log(DEBUG, format_binary(packet, 'IN: '));
        packet = leftover + packet
        if self.server_mac_len > 0:
            mac = post_packet[:self.server_mac_len]
            mac_payload = struct.pack('>II', self.sequence_number_in, packet_size) + packet
            my_mac = HMAC.HMAC(self.mac_key_in, mac_payload, self.server_mac_engine).digest()[:self.server_mac_len]
            if my_mac != mac:
                raise SSHException('Mismatched MAC')
        padding = ord(packet[0])
        payload = packet[1:packet_size - padding + 1]
        randpool.add_event(packet[packet_size - padding + 1])
        #self.log(DEBUG, 'Got payload (%d bytes, %d padding)' % (packet_size, padding))
        msg = Message(payload[1:])
        msg.seqno = self.sequence_number_in
        self.sequence_number_in = (self.sequence_number_in + 1) & 0xffffffffL
        return ord(payload[0]), msg

    def set_K_H(self, k, h):
        "used by a kex object to set the K (root key) and H (exchange hash)"
        self.K = k
        self.H = h
        if self.session_id == None:
            self.session_id = h

    def verify_key(self, host_key, sig):
        if self.host_key_type == 'ssh-rsa':
            key = RSAKey(Message(host_key))
        elif self.host_key_type == 'ssh-dss':
            key = DSSKey(Message(host_key))
        else:
            key = None
        if (key == None) or not key.valid:
            raise SSHException('Unknown host key type')
        if not key.verify_ssh_sig(self.H, Message(sig)):
            raise SSHException('Signature verification (%s) failed.  Boo.  Robey should debug this.' % self.host_key_type)
        self.host_key = host_key

    def compute_key(self, id, nbytes):
        "id is 'A' - 'F' for the various keys used by ssh"
        m = Message()
        m.add_mpint(self.K)
        m.add_bytes(self.H)
        m.add_byte(id)
        m.add_bytes(self.session_id)
        out = sofar = SHA.new(str(m)).digest()
        while len(out) < nbytes:
            m = Message()
            m.add_mpint(self.K)
            m.add_bytes(self.H)
            m.add_bytes(sofar)
            hash = SHA.new(str(m)).digest()
            out += hash
            sofar += hash
        return out[:nbytes]

    def get_cipher(self, name, key, iv):
        if not self.cipher_info.has_key(name):
            raise SSHException('Unknown client cipher ' + name)
        return self.cipher_info[name]['class'].new(key, self.cipher_info[name]['mode'], iv)

    def run(self):
        self.active = 1
        # SSH-1.99-OpenSSH_2.9p2
        self.write_all(self.client_version + '\r\n')
        try:
            self.check_banner()
            self.send_kex_init()

            ptype, m = self.read_message()
            while ptype == MSG_IGNORE:
                ptype, m = self.read_message()
            if ptype == MSG_DISCONNECT:
                self.parse_disconnect(m)
                raise SSHException('Disconnected')
            if ptype != MSG_KEXINIT:
                raise SSHException('Expected kex-init, got %d' % ptype)
            self.negotiate_keys(m)

            while self.active:
                ptype, m = self.read_message()
                if ptype == MSG_IGNORE:
                    continue
                elif ptype == MSG_DISCONNECT:
                    self.parse_disconnect(m)
                    self.active = 0
                    break
                elif ptype == MSG_DEBUG:
                    self.parse_debug(m)
                    continue
                if self.expected_packet != 0:
                    if ptype != self.expected_packet:
                        raise SSHException('Expecting packet %d, got %d' % (self.expected_packet, ptype))
                    self.expected_packet = 0
                    if (ptype >= 30) and (ptype <= 39):
                        self.kex_engine.parse_next(ptype, m)
                        continue
                
                if ptype == MSG_NEWKEYS:
                    self.parse_newkeys(m)
                elif ptype == MSG_SERVICE_ACCEPT:
                    self.parse_service_accept(m)
                elif ptype == MSG_USERAUTH_SUCCESS:
                    self.parse_userauth_success(m)
                elif ptype == MSG_USERAUTH_FAILURE:
                    self.parse_userauth_failure(m)
                elif ptype == MSG_USERAUTH_BANNER:
                    self.parse_userauth_banner(m)
                elif ptype == MSG_CHANNEL_OPEN_SUCCESS:
                    self.parse_channel_open_success(m)
                elif ptype == MSG_CHANNEL_OPEN_FAILURE:
                    self.parse_channel_open_failure(m)
                elif ptype == MSG_CHANNEL_SUCCESS:
                    self.parse_channel_request_success(m)
                elif ptype == MSG_CHANNEL_FAILURE:
                    self.parse_channel_request_failure(m)
                elif ptype == MSG_CHANNEL_DATA:
                    self.parse_channel_data(m)
                elif ptype == MSG_CHANNEL_WINDOW_ADJUST:
                    self.parse_channel_window_adjust(m)
                elif ptype == MSG_CHANNEL_REQUEST:
                    self.parse_channel_request(m)
                elif ptype == MSG_CHANNEL_EOF:
                    self.parse_channel_eof(m)
                elif ptype == MSG_CHANNEL_CLOSE:
                    self.parse_channel_close(m)
                elif ptype == MSG_CHANNEL_OPEN:
                    self.parse_channel_open(m)
                elif ptype == MSG_KEXINIT:
                    self.negotiate_keys(m)
                else:
                    self.log(WARNING, 'Oops, unhandled type %d' % ptype)
                    msg = Message()
                    msg.add_byte(chr(MSG_UNIMPLEMENTED))
                    msg.add_int(m.seqno)
                    self.send_message(m)
        except SSHException, e:
            self.log(DEBUG, 'Exception: ' + str(e))
        except EOFError, e:
            self.log(DEBUG, 'EOF')
        if self.active:
            self.active = 0
            if self.completion_event != None:
                self.completion_event.set()
            if self.auth_event != None:
                self.auth_event.set()
            for e in self.channel_events.values():
                e.set()
        self.sock.close()

    ###  protocol stages

    def renegotiate_keys(self):
        self.completion_event = threading.Event()
        self.send_kex_init()
        while 1:
            self.completion_event.wait(0.1);
            if not self.active:
                return 0
            if self.completion_event.isSet():
                break
        return 1

    def negotiate_keys(self, m):
        "throws SSHException on anything unusual"
        if self.client_kex_init == None:
            # server wants to renegotiate
            self.send_kex_init()
        self.parse_kex_init(m)
        self.kex_engine.start_kex()

    def check_banner(self):
        # this is slow, but we only have to do it once
        for i in range(5):
            buffer = ''
            while not '\n' in buffer:
                buffer += self.read_all(1)
            buffer = buffer[:-1]
            if buffer[:4] == 'SSH-':
                break
            self.log(DEBUG, 'Banner: ' + buffer)
        if buffer[:4] != 'SSH-':
            raise SSHException('Indecipherable protocol version "' + buffer + '"')
        # save this server version string for later
        self.server_version = buffer
        # pull off any attached comment
        comment = ''
        i = string.find(buffer, ' ')
        if i >= 0:
            comment = buffer[i+1:]
            buffer = buffer[:i]
        # parse out version string and make sure it matches
        _unused, version, client = string.split(buffer, '-')
        if version != '1.99' and version != '2.0':
            raise SSHException('Incompatible version (%s instead of 2.0)' % (version,))
        self.log(INFO, 'Connected (version %s, client %s)' % (version, client))

    def send_kex_init(self):
        # send a really wimpy kex-init packet that says we're a bare-bones ssh client
        m = Message()
        m.add_byte(chr(MSG_KEXINIT))
        m.add_bytes(randpool.get_bytes(16))
        m.add(','.join(self.preferred_kex))
        m.add(','.join(self.preferred_keys))
        m.add(','.join(self.preferred_ciphers))
        m.add(','.join(self.preferred_ciphers))
        m.add(','.join(self.preferred_macs))
        m.add(','.join(self.preferred_macs))
        m.add('none')
        m.add('none')
        m.add('')
        m.add('')
        m.add_boolean(0)
        m.add_int(0)
        # save a copy for later (needed to compute a hash)
        self.client_kex_init = str(m)
        self.send_message(m)

    def parse_kex_init(self, m):
        cookie = m.get_bytes(16)
        kex_algo_list = m.get_list()
        server_key_algo_list = m.get_list()
        client_encrypt_algo_list = m.get_list()
        server_encrypt_algo_list = m.get_list()
        client_mac_algo_list = m.get_list()
        server_mac_algo_list = m.get_list()
        client_compress_algo_list = m.get_list()
        server_compress_algo_list = m.get_list()
        client_lang_list = m.get_list()
        server_lang_list = m.get_list()
        kex_follows = m.get_boolean()
        unused = m.get_int()

        # we are very picky because we support so little
        if (not('none' in client_compress_algo_list) or
            not('none' in server_compress_algo_list)):
            raise SSHException('Incompatible ssh server.')

        agreed_kex = filter(kex_algo_list.__contains__, self.preferred_kex)
        if len(agreed_kex) == 0:
            raise SSHException('Incompatible ssh server (no acceptable kex algorithm)')
        self.kex_engine = self.kex_info[agreed_kex[0]](self)

        agreed_keys = filter(server_key_algo_list.__contains__, self.preferred_keys)
        if len(agreed_keys) == 0:
            raise SSHException('Incompatible ssh server (no acceptable host key)')
        self.host_key_type = agreed_keys[0]
        
        agreed_client_ciphers = filter(client_encrypt_algo_list.__contains__,
                                       self.preferred_ciphers)
        agreed_server_ciphers = filter(client_encrypt_algo_list.__contains__,
                                       self.preferred_ciphers)
        if (len(agreed_client_ciphers) == 0) or (len(agreed_server_ciphers) == 0):
            raise SSHException('Incompatible ssh server (no acceptable ciphers)')
        self.client_cipher = agreed_client_ciphers[0]
        self.server_cipher = agreed_server_ciphers[0]

        agreed_client_macs = filter(client_mac_algo_list.__contains__, self.preferred_macs)
        agreed_server_macs = filter(server_mac_algo_list.__contains__, self.preferred_macs)
        if (len(agreed_client_macs) == 0) or (len(agreed_server_macs) == 0):
            raise SSHException('Incompatible ssh server (no acceptable macs)')
        self.client_mac = agreed_client_macs[0]
        self.server_mac = agreed_server_macs[0]
        
        self.log(DEBUG, 'kex algos:' + str(kex_algo_list) + ' server key:' + str(server_key_algo_list) + \
                 ' client encrypt:' + str(client_encrypt_algo_list) + \
                 ' server encrypt:' + str(server_encrypt_algo_list) + \
                 ' client mac:' + str(client_mac_algo_list) + \
                 ' server mac:' + str(server_mac_algo_list) + \
                 ' client compress:' + str(client_compress_algo_list) + \
                 ' server compress:' + str(server_compress_algo_list) + \
                 ' client lang:' + str(client_lang_list) + \
                 ' server lang:' + str(server_lang_list) + \
                 ' kex follows?' + str(kex_follows))
        # save for computing hash later...
        # now wait!  openssh has a bug (and others might too) where there are
        # actually some extra bytes (one NUL byte in openssh's case) added to
        # the end of the packet but not parsed.  turns out we need to throw
        # away those bytes because they aren't part of the hash.
        self.server_kex_init = chr(MSG_KEXINIT) + m.get_so_far()

    def activate_inbound(self):
        "switch on newly negotiated encryption parameters for inbound traffic"
        self.block_size_in = self.cipher_info[self.server_cipher]['block-size']
        IV_in = self.compute_key('B', self.block_size_in)
        key_in = self.compute_key('D', self.cipher_info[self.server_cipher]['key-size'])
        self.engine_in = self.get_cipher(self.server_cipher, key_in, IV_in)
        self.server_mac_len = self.mac_info[self.server_mac]['size']
        self.server_mac_engine = self.mac_info[self.server_mac]['class']
        # initial mac keys are done in the hash's natural size (not the potentially truncated
        # transmission size)
        self.mac_key_in = self.compute_key('F', self.server_mac_engine.digest_size)

    def activate_outbound(self):
        "switch on newly negotiated encryption parameters for outbound traffic"
        m = Message()
        m.add_byte(chr(MSG_NEWKEYS))
        self.send_message(m)
        self.block_size_out = self.cipher_info[self.client_cipher]['block-size']
        IV_out = self.compute_key('A', self.block_size_out)
        key_out = self.compute_key('C', self.cipher_info[self.client_cipher]['key-size'])
        self.engine_out = self.get_cipher(self.client_cipher, key_out, IV_out)
        self.client_mac_len = self.mac_info[self.client_mac]['size']
        self.client_mac_engine = self.mac_info[self.client_mac]['class']
        # initial mac keys are done in the hash's natural size (not the potentially truncated
        # transmission size)
        self.mac_key_out = self.compute_key('E', self.client_mac_engine.digest_size)

    def parse_newkeys(self, m):
        self.log(DEBUG, 'Switch to new keys ...')
        self.activate_inbound()
        # can also free a bunch of stuff here
        self.client_kex_init = self.server_kex_init = None
        self.e = self.f = self.K = self.x = None
        if not self.initial_kex_done:
            # this was the first key exchange
            self.initial_kex_done = 1
        # send an event?
        if self.completion_event != None:
            self.completion_event.set()
        return

    def parse_disconnect(self, m):
        code = m.get_int()
        desc = m.get_string()
        self.log(INFO, 'Disconnect (code %d): %s' % (code, desc))

    def parse_service_accept(self, m):
        service = m.get_string()
        if service == 'ssh-userauth':
            self.log(DEBUG, 'userauth is OK')
            m = Message()
            m.add_byte(chr(MSG_USERAUTH_REQUEST))
            m.add_string(self.username)
            m.add_string('ssh-connection')
            m.add_string(self.auth_method)
            if self.auth_method == 'password':
                m.add_boolean(0)
                m.add_string(self.password)
            elif self.auth_method == 'publickey':
                m.add_boolean(1)
                m.add_string(self.private_key.get_name())
                m.add_string(str(self.private_key))
                m.add_string(self.private_key.sign_ssh_session(self.randpool, self.H, self.username))
            else:
                raise SSHException('Unknown auth method "%s"' % self.auth_method)
            self.send_message(m)
        else:
            self.log(DEBUG, 'Service request "%s" accepted (?)' % service)

    def parse_userauth_success(self, m):
        self.log(INFO, 'Authentication successful!')
        self.authenticated = 1
        if self.auth_event != None:
            self.auth_event.set()

    def parse_userauth_failure(self, m):
        authlist = m.get_list()
        partial = m.get_boolean()
        if partial:
            self.log(INFO, 'Authentication continues...')
            self.log(DEBUG, 'Methods: ' + str(partial))
            # FIXME - do something
            pass
        self.log(INFO, 'Authentication failed.')
        self.authenticated = 0
        self.close()
        if self.auth_event != None:
            self.auth_event.set()

    def parse_userauth_banner(self, m):
        banner = m.get_string()
        lang = m.get_string()
        self.log(INFO, 'Auth banner: ' + banner)
        # who cares.

    def parse_channel_open_success(self, m):
        chanid = m.get_int()
        server_chanid = m.get_int()
        server_window_size = m.get_int()
        server_max_packet_size = m.get_int()
        if not self.channels.has_key(chanid):
            self.log(WARNING, 'Success for unrequested channel! [??]')
            return
        try:
            self.lock.acquire()
            chan = self.channels[chanid]
            chan.set_server_channel(server_chanid, server_window_size, server_max_packet_size)
            self.log(INFO, 'Secsh channel %d opened.' % chanid)
            if self.channel_events.has_key(chanid):
                self.channel_events[chanid].set()
                del self.channel_events[chanid]
        finally:
            self.lock.release()
        return

    def parse_channel_open_failure(self, m):
        chanid = m.get_int()
        reason = m.get_int()
        reason_str = m.get_string()
        lang = m.get_string()
        if CONNECTION_FAILED_CODE.has_key(reason):
            reason_text = CONNECTION_FAILED_CODE[reason]
        else:
            reason_text = '(unknown code)'
        self.log(INFO, 'Secsh channel %d open FAILED: %s: %s' % (chanid, reason_str, reason_text))
        try:
            self.lock.aquire()
            if self.channels.has_key(chanid):
                del self.channels[chanid]
                if self.channel_events.has_key(chanid):
                    self.channel_events[chanid].set()
                    del self.channel_events[chanid]
        finally:
            self.lock_release()
        return

    def parse_channel_request_success(self, m):
        chanid = m.get_int()
        self.log(DEBUG, 'Sesch channel %d request ok' % chanid)
        return

    def parse_channel_request_failure(self, m):
        chanid = m.get_int()
        self.log(WARNING, 'Secsh channel %d request failed' % chanid)
        if self.channels.has_key(chanid):
            self.channels[chanid].request_failed()

    def parse_channel_data(self, m):
        chanid = m.get_int()
        if self.channels.has_key(chanid):
            self.channels[chanid].feed(m.get_string())

    def parse_channel_window_adjust(self, m):
        chanid = m.get_int()
        bytes = m.get_int()
        if self.channels.has_key(chanid):
            self.channels[chanid].window_adjust(bytes)

    def parse_channel_request(self, m):
        chanid = m.get_int()
        if self.channels.has_key(chanid):
            self.channels[chanid].handle_request(m)

    def parse_channel_eof(self, m):
        chanid = m.get_int()
        if self.channels.has_key(chanid):
            self.channels[chanid].handle_eof()

    def parse_channel_close(self, m):
        chanid = m.get_int()
        if self.channels.has_key(chanid):
            self.channels[chanid].handle_close()

    def parse_channel_open(self, m):
        kind = m.get_string()
        self.log(DEBUG, 'Rejecting "%s" channel request from server.' % kind)
        chanid = m.get_int()
        msg = Message()
        msg.add_byte(chr(MSG_CHANNEL_OPEN_FAILURE))
        msg.add_int(chanid)
        msg.add_int(1)
        msg.add_string('Client connections are not allowed.')
        msg.add_string('en')
        self.send_message(msg)

    def parse_debug(self, m):
        always_display = m.get_boolean()
        msg = m.get_string()
        lang = m.get_string()
        self.log(DEBUG, 'Debug msg: ' + safe_string(msg))
