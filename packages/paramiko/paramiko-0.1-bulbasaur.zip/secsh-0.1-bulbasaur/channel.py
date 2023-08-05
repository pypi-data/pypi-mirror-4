from message import Message
from secsh import SSHException
from transport import MSG_CHANNEL_REQUEST, MSG_CHANNEL_CLOSE, MSG_CHANNEL_WINDOW_ADJUST, MSG_CHANNEL_DATA, \
	MSG_CHANNEL_EOF

import time, threading, logging, socket, os
from logging import DEBUG


# this is ugly, and won't work on windows
def set_nonblocking(fd):
    import fcntl
    fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)


class Channel:
    """
    Abstraction for a secsh channel.
    """
    
    def __init__(self, chanid, transport):
        self.chanid = chanid
        self.transport = transport
        self.active = 0
        self.eof = 0
        self.in_buffer = ''
        self.timeout = None
        self.closed = 0
        self.lock = threading.Lock()
        self.in_buffer_cv = threading.Condition(self.lock)
        self.out_buffer_cv = threading.Condition(self.lock)
        self.name = str(chanid)
        self.logger = logging.getLogger('secsh.chan.' + str(chanid))
        self.pipe_rfd = self.pipe_wfd = None

    def __repr__(self):
        out = '<secsh.Channel %d' % self.chanid
        if self.closed:
            out += ' (closed)'
        elif self.active:
            if self.eof:
                out += ' (EOF)'
            out += ' (open) window=%d' % (self.out_window_size)
            if len(self.in_buffer) > 0:
                out += ' in-buffer=%d' % (len(self.in_buffer),)
        out += ' -> ' + repr(self.transport)
        out += '>'
        return out

    def log(self, level, msg):
        self.logger.log(level, msg)

    def set_window(self, window_size, max_packet_size):
        self.in_window_size = window_size
        self.in_max_packet_size = max_packet_size
        # threshold of bytes we receive before we bother to send a window update
        self.in_window_threshold = window_size // 10
        self.in_window_sofar = 0
        
    def set_server_channel(self, chanid, window_size, max_packet_size):
        self.server_chanid = chanid
        self.out_window_size = window_size
        self.out_max_packet_size = max_packet_size
        self.active = 1

    def request_failed(self):
        self.close()

    def feed(self, s):
        try:
            self.lock.acquire()
            self.log(DEBUG, 'fed %d bytes' % len(s))
            if self.pipe_wfd != None:
                self.feed_pipe(s)
            else:
                self.in_buffer += s
                self.in_buffer_cv.notifyAll()
            self.log(DEBUG, '(out from feed)')
        finally:
            self.lock.release()

    def window_adjust(self, nbytes):
        try:
            self.lock.acquire()
            self.log(DEBUG, 'window up %d' % nbytes)
            self.out_window_size += nbytes
            self.out_buffer_cv.notifyAll()
        finally:
            self.lock.release()

    def handle_request(self, m):
        key = m.get_string()
        if key == 'exit-status':
            self.exit_status = m.get_int()
            return
        elif key == 'xon-xoff':
            # ignore
            return
        else:
            self.log(DEBUG, 'Unhandled channel request "%s"' % key)

    def handle_eof(self):
        self.eof = 1
        try:
            self.lock.acquire()
            self.in_buffer_cv.notifyAll()
            if self.pipe_wfd != None:
                os.close(self.pipe_wfd)
		self.pipe_wfd = None
        finally:
            self.lock.release()

    def handle_close(self):
        self.close()
        try:
            self.lock.acquire()
            self.in_buffer_cv.notifyAll()
            self.out_buffer_cv.notifyAll()
            if self.pipe_wfd != None:
                os.close(self.pipe_wfd)
		self.pipe_wfd = None
        finally:
            self.lock.release()


    # API for external use

    def get_pty(self, term='vt100', width=80, height=24):
        if self.closed or self.eof or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.server_chanid)
        m.add_string('pty-req')
        m.add_boolean(0)
        m.add_string(term)
        m.add_int(width)
        m.add_int(height)
        # pixel height, width (usually useless)
        m.add_int(0).add_int(0)
        m.add_string('')
        self.transport.send_message(m)

    def invoke_shell(self):
        if self.closed or self.eof or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.server_chanid)
        m.add_string('shell')
        m.add_boolean(1)
        self.transport.send_message(m)

    def invoke_subsystem(self, subsystem):
        if self.closed or self.eof or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.server_chanid)
        m.add_string('subsystem')
        m.add_boolean(1)
        self.transport.send_message(m)

    def resize_pty(self, width=80, height=24):
        if self.closed or self.eof or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.server_chanid)
        m.add_string('window-change')
        m.add_boolean(0)
        m.add_int(width)
        m.add_int(height)
        m.add_int(0).add_int(0)
        self.transport.send_message(m)

    def get_transport(self):
        return self.transport

    def set_name(self, name):
        self.name = name
        self.logger = logging.getLogger('secsh.chan.' + name)

    def get_name(self):
        return self.name
    

    # socket equivalency methods...

    def settimeout(self, timeout):
        self.timeout = timeout

    def gettimeout(self):
        return self.timeout

    def setblocking(self, blocking):
        if blocking:
            self.settimeout(None)
        else:
            self.settimeout(0.0)

    def close(self):
        if self.closed or not self.active:
            return
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_EOF))
        m.add_int(self.server_chanid)
        self.transport.send_message(m)
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_CLOSE))
        m.add_int(self.server_chanid)
        self.transport.send_message(m)
        self.closed = 1
        self.transport.unlink_channel(self.chanid)

    def recv_ready(self):
        "doesn't work if you've called fileno()"
        try:
            self.lock.acquire()
            if len(self.in_buffer) == 0:
                return 0
            return 1
        finally:
            self.lock.release()

    def recv(self, nbytes):
        out = ''
        try:
            self.lock.acquire()
            if self.pipe_rfd != None:
                # use the pipe
                return self.read_pipe(nbytes)
            if len(self.in_buffer) == 0:
                if self.closed or self.eof:
                    return out
                # should we block?
                if self.timeout == 0.0:
                    raise socket.timeout()
                # loop here in case we get woken up but a different thread has grabbed everything in the buffer
                timeout = self.timeout
                while len(self.in_buffer) == 0:
                    then = time.time()
                    self.in_buffer_cv.wait(timeout)
                    if timeout != None:
                        timeout -= time.time() - then
                        if timeout <= 0.0:
                            raise socket.timeout()
            # something in the buffer and we have the lock
            if len(self.in_buffer) <= nbytes:
                out = self.in_buffer
                self.in_buffer = ''
            else:
                out = self.in_buffer[:nbytes]
                self.in_buffer = self.in_buffer[nbytes:]
            self.check_add_window(len(out))
        finally:
            self.lock.release()
        return out

    def send(self, s):
        size = 0
        if self.closed:
            return size
        try:
            self.lock.acquire()
            if self.out_window_size == 0:
                # should we block?
                if self.timeout == 0.0:
                    raise socket.timeout()
                # loop here in case we get woken up but a different thread has filled the buffer
                timeout = self.timeout
                while self.out_window_size == 0:
                    then = time.time()
                    self.out_buffer_cv.wait(timeout)
                    if timeout != None:
                        timeout -= time.time() - then
                        if timeout <= 0.0:
                            raise socket.timeout()
            # we have some window to squeeze into
            if self.closed:
                return 0
            size = len(s)
            if self.out_window_size < size:
                size = self.out_window_size
            if self.out_max_packet_size < size:
                size = self.out_max_packet_size
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_DATA))
            m.add_int(self.server_chanid)
            m.add_string(s[:size])
            self.transport.send_message(m)
            self.out_window_size -= size
        finally:
            self.lock.release()
        return size

    def fileno(self):
        """
        returns an OS-level fd which can be used for polling and reading (but
        NOT for writing).  this is primarily to allow python's \"select\" module
        to work.  the first time this function is called, a pipe is created to
        simulate real OS-level fd behavior.  because of this, two actual fds are
        created: one to return and one to feed.  this may be inefficient if you
        plan to use many fds.

        the channel's receive window will be updated as data comes in, not as
        you read it, so if you fail to poll the channel often enough, it may
        block ALL channels across the transport.
        """
        try:
            self.lock.acquire()
            if self.pipe_rfd != None:
                return self.pipe_rfd
            # create the pipe and feed in any existing data
            self.pipe_rfd, self.pipe_wfd = os.pipe()
            set_nonblocking(self.pipe_wfd)
            set_nonblocking(self.pipe_rfd)
            if len(self.in_buffer) > 0:
                x = self.in_buffer
                self.in_buffer = ''
                self.feed_pipe(x)
            return self.pipe_rfd
        finally:
            self.lock.release()


    # internal use...

    def feed_pipe(self, data):
        "you are already holding the lock"
        if len(self.in_buffer) > 0:
            self.in_buffer += data
            return
        try:
            n = os.write(self.pipe_wfd, data)
            if n < len(data):
                # at least on linux, this will never happen, as the writes are
                # considered atomic... but just in case.
                self.in_buffer = data[n:]
            self.check_add_window(n)
            return
        except OSError, e:
            pass
        if len(data) > 1:
            # try writing just one byte then
            x = data[0]
            data = data[1:]
            try:
                os.write(self.pipe_wfd, x)
                self.in_buffer = data
                self.check_add_window(1)
                return
            except OSError, e:
                pass
        # pipe is very full
        self.in_buffer = data

    def read_pipe(self, nbytes):
        "you are already holding the lock"
        try:
            x = os.read(self.pipe_rfd, nbytes)
            if len(x) > 0:
                self.push_pipe(len(x))
                return x
        except OSError, e:
            pass
        # nothing in the pipe
        if self.closed or self.eof:
            return ''
        # should we block?
        if self.timeout == 0.0:
            raise socket.timeout()
        # loop here in case we get woken up but a different thread has grabbed everything in the buffer
        timeout = self.timeout
        while 1:
            then = time.time()
            self.in_buffer_cv.wait(timeout)
            if timeout != None:
                timeout -= time.time() - then
                if timeout <= 0.0:
                    raise socket.timeout()
            try:
                x = os.read(self.pipe_rfd, nbytes)
                if len(x) > 0:
                    self.push_pipe(len(x))
                    return x
            except OSError, e:
                pass
        pass

    def push_pipe(self, nbytes):
        # successfully read N bytes from the pipe, now re-feed the pipe if necessary
        # (assumption: the pipe can hold as many bytes as were read out)
        if len(self.in_buffer) == 0:
            return
        if len(self.in_buffer) <= nbytes:
            os.write(self.pipe_wfd, self.in_buffer)
            self.in_buffer = ''
            return
        x = self.in_buffer[:nbytes]
        self.in_buffer = self.in_buffer[nbytes:]
        os.write(self.pipd_wfd, x)

    def unlink(self):
        if self.closed or not self.active:
            return
        self.closed = 1
        self.transport.unlink_channel(self.chanid)

    def check_add_window(self, n):
        # already holding the lock!
        if self.closed or self.eof or not self.active:
            return
        self.log(DEBUG, 'addwindow %d' % n)
        self.in_window_sofar += n
        if self.in_window_sofar > self.in_window_threshold:
            self.log(DEBUG, 'addwindow send %d' % self.in_window_sofar)
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_WINDOW_ADJUST))
            m.add_int(self.server_chanid)
            m.add_int(self.in_window_sofar)
            self.transport.send_message(m)
            self.in_window_sofar = 0
