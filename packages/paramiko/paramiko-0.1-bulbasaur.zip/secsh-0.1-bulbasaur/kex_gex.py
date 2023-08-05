#!/usr/bin/python

# variant on group1 (see kex_group1.py) where the prime "p" and generator "g"
# are provided by the server.  a bit more work is required on our side (and a
# LOT more on the server side).

from message import Message, inflate_long, deflate_long
from secsh import SSHException
from transport import MSG_NEWKEYS
from Crypto.Hash import SHA
from logging import DEBUG

MSG_KEXDH_GEX_GROUP, MSG_KEXDH_GEX_INIT, MSG_KEXDH_GEX_REPLY, MSG_KEXDH_GEX_REQUEST = range(31, 35)


class KexGex(object):

    name = 'diffie-hellman-group-exchange-sha1'
    min_bits = 1024
    max_bits = 8192
    preferred_bits = 2048

    def __init__(self, transport):
        self.transport = transport

    def start_kex(self):
        # request a bit range: we accept (min_bits) to (max_bits), but prefer
        # (preferred_bits).  according to the spec, we shouldn't pull the
        # minimum up above 1024.
        m = Message()
        m.add_byte(chr(MSG_KEXDH_GEX_REQUEST))
        m.add_int(self.min_bits)
        m.add_int(self.preferred_bits)
        m.add_int(self.max_bits)
        self.transport.send_message(m)
        self.transport.expected_packet = MSG_KEXDH_GEX_GROUP

    def parse_next(self, ptype, m):
        if ptype == MSG_KEXDH_GEX_GROUP:
            return self.parse_kexdh_gex_group(m)
        elif ptype == MSG_KEXDH_GEX_REPLY:
            return self.parse_kexdh_gex_reply(m)
        raise SSHException('KexGex asked to handle packet type %d' % ptype)

    def bit_length(n):
        norm = deflate_long(n, 0)
        hbyte = ord(norm[0])
        bitlen = len(norm) * 8
        while not (hbyte & 0x80):
            hbyte <<= 1
            bitlen -= 1
        return bitlen
    bit_length = staticmethod(bit_length)

    def generate_x_e(self):
        # generate an "x" (1 < x < (p-1)/2).
        q = (self.p - 1) // 2
        qnorm = deflate_long(q, 0)
        qhbyte = ord(qnorm[0])
        bytes = len(qnorm)
        qmask = 0xff
        while not (qhbyte & 0x80):
            qhbyte <<= 1
            qmask >>= 1
        while 1:
            self.transport.randpool.stir()
            x_bytes = self.transport.randpool.get_bytes(bytes)
            x_bytes = chr(ord(x_bytes[0]) & qmask) + x_bytes[1:]
            x = inflate_long(x_bytes, 1)
            if (x > 1) and (x < q):
                break
        self.x = x
        # now compute e = g^x mod p
        self.e = pow(self.g, self.x, self.p)

    def parse_kexdh_gex_group(self, m):
        self.p = m.get_mpint()
        self.g = m.get_mpint()
        # reject if p's bit length < 1024 or > 8192
        bitlen = self.bit_length(self.p)
        if (bitlen < 1024) or (bitlen > 8192):
            raise SSHException('Server-generated gex p (don\'t ask) is out of range (%d bits)' % bitlen)
        self.transport.log(DEBUG, 'Got server p (%d bits)' % bitlen)
        # generate an 'e' and send it
        self.generate_x_e()
        m = Message()
        m.add_byte(chr(MSG_KEXDH_GEX_INIT))
        m.add_mpint(self.e)
        self.transport.send_message(m)
        self.transport.expected_packet = MSG_KEXDH_GEX_REPLY

    def parse_kexdh_gex_reply(self, m):
        host_key = m.get_string()
        self.f = m.get_mpint()
        sig = m.get_string()
        if (self.f < 1) or (self.f > self.p):
            raise SSHException('Server-generated gex f (don\'t ask) is out of range')
        K = pow(self.f, self.x, self.p)
        # okay, build up the hash H of (V_C || V_S || I_C || I_S || K_S || min || n || max || p || g || e || f || K)
        hm = Message().add(self.transport.client_version).add(self.transport.server_version)
        hm.add(self.transport.client_kex_init).add(self.transport.server_kex_init).add(host_key)
        hm.add_int(self.min_bits)
        hm.add_int(self.preferred_bits)
        hm.add_int(self.max_bits)
        hm.add_mpint(self.p)
        hm.add_mpint(self.g)
        hm.add(self.e).add(self.f).add(K)
        self.transport.set_K_H(K, SHA.new(str(hm)).digest())
        self.transport.verify_key(host_key, sig)
        self.transport.activate_outbound()
        self.transport.expected_packet = MSG_NEWKEYS

    
