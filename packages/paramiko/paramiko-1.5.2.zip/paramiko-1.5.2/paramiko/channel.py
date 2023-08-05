# Copyright (C) 2003-2005 Robey Pointer <robey@lag.net>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

"""
Abstraction for an SSH2 channel.
"""

import sys
import time
import threading
import socket
import os

from paramiko.common import *
from paramiko import util
from paramiko.message import Message
from paramiko.ssh_exception import SSHException
from paramiko.file import BufferedFile
from paramiko import pipe


class Channel (object):
    """
    A secure tunnel across an SSH L{Transport}.  A Channel is meant to behave
    like a socket, and has an API that should be indistinguishable from the
    python socket API.

    Because SSH2 has a windowing kind of flow control, if you stop reading data
    from a Channel and its buffer fills up, the server will be unable to send
    you any more data until you read some of it.  (This won't affect other
    channels on the same transport -- all channels on a single transport are
    flow-controlled independently.)  Similarly, if the server isn't reading
    data you send, calls to L{send} may block, unless you set a timeout.  This
    is exactly like a normal network socket, so it shouldn't be too surprising.
    """

    # lower bound on the max packet size we'll accept from the remote host
    MIN_PACKET_SIZE = 1024

    def __init__(self, chanid):
        """
        Create a new channel.  The channel is not associated with any
        particular session or L{Transport} until the Transport attaches it.
        Normally you would only call this method from the constructor of a
        subclass of L{Channel}.

        @param chanid: the ID of this channel, as passed by an existing
            L{Transport}.
        @type chanid: int
        """
        self.chanid = chanid
        self.remote_chanid = 0
        self.transport = None
        self.active = False
        self.eof_received = 0
        self.eof_sent = 0
        self.in_buffer = ''
        self.in_stderr_buffer = ''
        self.timeout = None
        self.closed = False
        self.ultra_debug = False
        self.lock = threading.Lock()
        self.in_buffer_cv = threading.Condition(self.lock)
        self.in_stderr_buffer_cv = threading.Condition(self.lock)
        self.out_buffer_cv = threading.Condition(self.lock)
        self.in_window_size = 0
        self.out_window_size = 0
        self.in_max_packet_size = 0
        self.out_max_packet_size = 0
        self.in_window_threshold = 0
        self.in_window_sofar = 0
        self.status_event = threading.Event()
        self.name = str(chanid)
        self.logger = util.get_logger('paramiko.chan.' + str(chanid))
        self.pipe = None
        self.event = threading.Event()
        self.combine_stderr = False
        self.exit_status = -1
    
    def __del__(self):
        self.close()
        
    def __repr__(self):
        """
        Return a string representation of this object, for debugging.

        @rtype: str
        """
        out = '<paramiko.Channel %d' % self.chanid
        if self.closed:
            out += ' (closed)'
        elif self.active:
            if self.eof_received:
                out += ' (EOF received)'
            if self.eof_sent:
                out += ' (EOF sent)'
            out += ' (open) window=%d' % (self.out_window_size)
            if len(self.in_buffer) > 0:
                out += ' in-buffer=%d' % (len(self.in_buffer),)
        out += ' -> ' + repr(self.transport)
        out += '>'
        return out

    def get_pty(self, term='vt100', width=80, height=24):
        """
        Request a pseudo-terminal from the server.  This is usually used right
        after creating a client channel, to ask the server to provide some
        basic terminal semantics for a shell invoked with L{invoke_shell}.
        It isn't necessary (or desirable) to call this method if you're going
        to exectue a single command with L{exec_command}.

        @param term: the terminal type to emulate (for example, C{'vt100'}).
        @type term: str
        @param width: width (in characters) of the terminal screen
        @type width: int
        @param height: height (in characters) of the terminal screen
        @type height: int
        @return: C{True} if the operation succeeded; C{False} if not.
        @rtype: bool
        """
        if self.closed or self.eof_received or self.eof_sent or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('pty-req')
        m.add_boolean(True)
        m.add_string(term)
        m.add_int(width)
        m.add_int(height)
        # pixel height, width (usually useless)
        m.add_int(0).add_int(0)
        m.add_string('')
        self.event.clear()
        self.transport._send_user_message(m)
        while True:
            self.event.wait(0.1)
            if self.closed:
                return False
            if self.event.isSet():
                return True

    def invoke_shell(self):
        """
        Request an interactive shell session on this channel.  If the server
        allows it, the channel will then be directly connected to the stdin,
        stdout, and stderr of the shell.
        
        Normally you would call L{get_pty} before this, in which case the
        shell will operate through the pty, and the channel will be connected
        to the stdin and stdout of the pty.
        
        When the shell exits, the channel will be closed and can't be reused.
        You must open a new channel if you wish to open another shell.
        
        @return: C{True} if the operation succeeded; C{False} if not.
        @rtype: bool
        """
        if self.closed or self.eof_received or self.eof_sent or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('shell')
        m.add_boolean(1)
        self.event.clear()
        self.transport._send_user_message(m)
        while True:
            self.event.wait(0.1)
            if self.closed:
                return False
            if self.event.isSet():
                return True

    def exec_command(self, command):
        """
        Execute a command on the server.  If the server allows it, the channel
        will then be directly connected to the stdin, stdout, and stderr of
        the command being executed.
        
        When the command finishes executing, the channel will be closed and
        can't be reused.  You must open a new channel if you wish to execute
        another command.

        @param command: a shell command to execute.
        @type command: str
        @return: C{True} if the operation succeeded; C{False} if not.
        @rtype: bool
        """
        if self.closed or self.eof_received or self.eof_sent or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('exec')
        m.add_boolean(1)
        m.add_string(command)
        self.event.clear()
        self.transport._send_user_message(m)
        while True:
            self.event.wait(0.1)
            if self.closed:
                return False
            if self.event.isSet():
                return True

    def invoke_subsystem(self, subsystem):
        """
        Request a subsystem on the server (for example, C{sftp}).  If the
        server allows it, the channel will then be directly connected to the
        requested subsystem.
        
        When the subsystem finishes, the channel will be closed and can't be
        reused.

        @param subsystem: name of the subsystem being requested.
        @type subsystem: str
        @return: C{True} if the operation succeeded; C{False} if not.
        @rtype: bool
        """
        if self.closed or self.eof_received or self.eof_sent or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('subsystem')
        m.add_boolean(1)
        m.add_string(subsystem)
        self.event.clear()
        self.transport._send_user_message(m)
        while True:
            self.event.wait(0.1)
            if self.closed:
                return False
            if self.event.isSet():
                return True

    def resize_pty(self, width=80, height=24):
        """
        Resize the pseudo-terminal.  This can be used to change the width and
        height of the terminal emulation created in a previous L{get_pty} call.

        @param width: new width (in characters) of the terminal screen
        @type width: int
        @param height: new height (in characters) of the terminal screen
        @type height: int
        @return: C{True} if the operation succeeded; C{False} if not.
        @rtype: bool
        """
        if self.closed or self.eof_received or self.eof_sent or not self.active:
            raise SSHException('Channel is not open')
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('window-change')
        m.add_boolean(1)
        m.add_int(width)
        m.add_int(height)
        m.add_int(0).add_int(0)
        self.event.clear()
        self.transport._send_user_message(m)
        while True:
            self.event.wait(0.1)
            if self.closed:
                return False
            if self.event.isSet():
                return True

    def recv_exit_status(self):
        """
        Return the exit status from the process on the server.  This is
        mostly useful for retrieving the reults of an L{exec_command}.
        If the command hasn't finished yet, this method will wait until
        it does, or until the channel is closed.  If no exit status is
        provided by the server, -1 is returned.
        
        @return: the exit code of the process on the server.
        @rtype: int
        
        @since: 1.2
        """
        while True:
            if self.closed or self.status_event.isSet():
                return self.exit_status
            self.status_event.wait(0.1)

    def send_exit_status(self, status):
        """
        Send the exit status of an executed command to the client.  (This
        really only makes sense in server mode.)  Many clients expect to
        get some sort of status code back from an executed command after
        it completes.
        
        @param status: the exit code of the process
        @type status: int
        
        @since: 1.2
        """
        # in many cases, the channel will not still be open here.
        # that's fine.
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_REQUEST))
        m.add_int(self.remote_chanid)
        m.add_string('exit-status')
        m.add_boolean(0)
        m.add_int(status)
        self.transport._send_user_message(m)
        
    def get_transport(self):
        """
        Return the L{Transport} associated with this channel.

        @return: the L{Transport} that was used to create this channel.
        @rtype: L{Transport}
        """
        return self.transport

    def set_name(self, name):
        """
        Set a name for this channel.  Currently it's only used to set the name
        of the log level used for debugging.  The name can be fetched with the
        L{get_name} method.

        @param name: new channel name.
        @type name: str
        """
        self.name = name
        self.logger = util.get_logger(self.transport.get_log_channel() + '.' + self.name)

    def get_name(self):
        """
        Get the name of this channel that was previously set by L{set_name}.

        @return: the name of this channel.
        @rtype: str
        """
        return self.name

    def get_id(self):
        """
        Return the ID # for this channel.  The channel ID is unique across
        a L{Transport} and usually a small number.  It's also the number
        passed to L{ServerInterface.check_channel_request} when determining
        whether to accept a channel request in server mode.

        @return: the ID of this channel.
        @rtype: int

        @since: ivysaur
        """
        return self.chanid
    
    def set_combine_stderr(self, combine):
        """
        Set whether stderr should be combined into stdout on this channel.
        The default is C{False}, but in some cases it may be convenient to
        have both streams combined.
        
        If this is C{False}, and L{exec_command} is called (or C{invoke_shell}
        with no pty), output to stderr will not show up through the L{recv}
        and L{recv_ready} calls.  You will have to use L{recv_stderr} and
        L{recv_stderr_ready} to get stderr output.
        
        If this is C{True}, data will never show up via L{recv_stderr} or
        L{recv_stderr_ready}.
        
        @param combine: C{True} if stderr output should be combined into
            stdout on this channel.
        @type combine: bool
        @return: previous setting.
        @rtype: bool
        
        @since: 1.1
        """
        data = ''
        self.lock.acquire()
        try:
            old = self.combine_stderr
            self.combine_stderr = combine
            if combine and not old:
                # copy old stderr buffer into primary buffer
                data = self.in_stderr_buffer
                self.in_stderr_buffer = ''
        finally:
            self.lock.release()
        if len(data) > 0:
            self._feed(data)
        return old

    
    ###  socket API


    def settimeout(self, timeout):
        """
        Set a timeout on blocking read/write operations.  The C{timeout}
        argument can be a nonnegative float expressing seconds, or C{None}.  If
        a float is given, subsequent channel read/write operations will raise
        a timeout exception if the timeout period value has elapsed before the
        operation has completed.  Setting a timeout of C{None} disables
        timeouts on socket operations.

        C{chan.settimeout(0.0)} is equivalent to C{chan.setblocking(0)};
        C{chan.settimeout(None)} is equivalent to C{chan.setblocking(1)}.

        @param timeout: seconds to wait for a pending read/write operation
        before raising C{socket.timeout}, or C{None} for no timeout.
        @type timeout: float
        """
        self.timeout = timeout

    def gettimeout(self):
        """
        Returns the timeout in seconds (as a float) associated with socket
        operations, or C{None} if no timeout is set.  This reflects the last
        call to L{setblocking} or L{settimeout}.

        @return: timeout in seconds, or C{None}.
        @rtype: float
        """
        return self.timeout

    def setblocking(self, blocking):
        """
        Set blocking or non-blocking mode of the channel: if C{blocking} is 0,
        the channel is set to non-blocking mode; otherwise it's set to blocking
        mode.  Initially all channels are in blocking mode.

        In non-blocking mode, if a L{recv} call doesn't find any data, or if a
        L{send} call can't immediately dispose of the data, an error exception
        is raised.  In blocking mode, the calls block until they can proceed.

        C{chan.setblocking(0)} is equivalent to C{chan.settimeout(0)};
        C{chan.setblocking(1)} is equivalent to C{chan.settimeout(None)}.

        @param blocking: 0 to set non-blocking mode; non-0 to set blocking
        mode.
        @type blocking: int
        """
        if blocking:
            self.settimeout(None)
        else:
            self.settimeout(0.0)

    def close(self):
        """
        Close the channel.  All future read/write operations on the channel
        will fail.  The remote end will receive no more data (after queued data
        is flushed).  Channels are automatically closed when their L{Transport}
        is closed or when they are garbage collected.
        """
        self.lock.acquire()
        try:
            if not self.active or self.closed:
                return
            msgs = self._close_internal()

            # only close the pipe when the user explicitly closes the channel.
            # otherwise they will get unpleasant surprises.
            if self.pipe is not None:
                self.pipe.close()
                self.pipe = None
        finally:
            self.lock.release()
        for m in msgs:
            if m is not None:
                self.transport._send_user_message(m)

    def recv_ready(self):
        """
        Returns true if data is buffered and ready to be read from this
        channel.  A C{False} result does not mean that the channel has closed;
        it means you may need to wait before more data arrives.
        
        @return: C{True} if a L{recv} call on this channel would immediately
            return at least one byte; C{False} otherwise.
        @rtype: boolean
        """
        self.lock.acquire()
        try:
            if len(self.in_buffer) == 0:
                return False
            return True
        finally:
            self.lock.release()

    def recv(self, nbytes):
        """
        Receive data from the channel.  The return value is a string
        representing the data received.  The maximum amount of data to be
        received at once is specified by C{nbytes}.  If a string of length zero
        is returned, the channel stream has closed.

        @param nbytes: maximum number of bytes to read.
        @type nbytes: int
        @return: data.
        @rtype: str
        
        @raise socket.timeout: if no data is ready before the timeout set by
            L{settimeout}.
        """
        out = ''
        self.lock.acquire()
        try:
            if len(self.in_buffer) == 0:
                if self.closed or self.eof_received:
                    return out
                # should we block?
                if self.timeout == 0.0:
                    raise socket.timeout()
                # loop here in case we get woken up but a different thread has grabbed everything in the buffer
                timeout = self.timeout
                while (len(self.in_buffer) == 0) and not self.closed and not self.eof_received:
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
                if self.pipe is not None:
                    # clear the pipe, since no more data is buffered
                    self.pipe.clear()
            else:
                out = self.in_buffer[:nbytes]
                self.in_buffer = self.in_buffer[nbytes:]
            ack = self._check_add_window(len(out))
        finally:
            self.lock.release()

        # no need to hold the channel lock when sending this
        if ack > 0:
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_WINDOW_ADJUST))
            m.add_int(self.remote_chanid)
            m.add_int(ack)
            self.transport._send_user_message(m)

        return out

    def recv_stderr_ready(self):
        """
        Returns true if data is buffered and ready to be read from this
        channel's stderr stream.  Only channels using L{exec_command} or
        L{invoke_shell} without a pty will ever have data on the stderr
        stream.
        
        @return: C{True} if a L{recv_stderr} call on this channel would
            immediately return at least one byte; C{False} otherwise.
        @rtype: boolean
        
        @since: 1.1
        """
        self.lock.acquire()
        try:
            if len(self.in_stderr_buffer) == 0:
                return False
            return True
        finally:
            self.lock.release()

    def recv_stderr(self, nbytes):
        """
        Receive data from the channel's stderr stream.  Only channels using
        L{exec_command} or L{invoke_shell} without a pty will ever have data
        on the stderr stream.  The return value is a string representing the
        data received.  The maximum amount of data to be received at once is
        specified by C{nbytes}.  If a string of length zero is returned, the
        channel stream has closed.

        @param nbytes: maximum number of bytes to read.
        @type nbytes: int
        @return: data.
        @rtype: str
        
        @raise socket.timeout: if no data is ready before the timeout set by
            L{settimeout}.
        
        @since: 1.1
        """
        out = ''
        self.lock.acquire()
        try:
            if len(self.in_stderr_buffer) == 0:
                if self.closed or self.eof_received:
                    return out
                # should we block?
                if self.timeout == 0.0:
                    raise socket.timeout()
                # loop here in case we get woken up but a different thread has grabbed everything in the buffer
                timeout = self.timeout
                while (len(self.in_stderr_buffer) == 0) and not self.closed and not self.eof_received:
                    then = time.time()
                    self.in_stderr_buffer_cv.wait(timeout)
                    if timeout != None:
                        timeout -= time.time() - then
                        if timeout <= 0.0:
                            raise socket.timeout()
            # something in the buffer and we have the lock
            if len(self.in_stderr_buffer) <= nbytes:
                out = self.in_stderr_buffer
                self.in_stderr_buffer = ''
            else:
                out = self.in_stderr_buffer[:nbytes]
                self.in_stderr_buffer = self.in_stderr_buffer[nbytes:]
            self._check_add_window(len(out))
        finally:
            self.lock.release()
        return out

    def send(self, s):
        """
        Send data to the channel.  Returns the number of bytes sent, or 0 if
        the channel stream is closed.  Applications are responsible for
        checking that all data has been sent: if only some of the data was
        transmitted, the application needs to attempt delivery of the remaining
        data.

        @param s: data to send.
        @type s: str
        @return: number of bytes actually sent.
        @rtype: int

        @raise socket.timeout: if no data could be sent before the timeout set
            by L{settimeout}.
        """
        size = len(s)
        self.lock.acquire()
        try:
            size = self._wait_for_send_window(size)
            if size == 0:
                # eof or similar
                return 0
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_DATA))
            m.add_int(self.remote_chanid)
            m.add_string(s[:size])
            self.transport._send_user_message(m)
        finally:
            self.lock.release()
        return size

    def send_stderr(self, s):
        """
        Send data to the channel on the "stderr" stream.  This is normally
        only used by servers to send output from shell commands -- clients
        won't use this.  Returns the number of bytes sent, or 0 if the channel
        stream is closed.  Applications are responsible for checking that all
        data has been sent: if only some of the data was transmitted, the
        application needs to attempt delivery of the remaining data.
        
        @param s: data to send.
        @type s: str
        @return: number of bytes actually sent.
        @rtype: int
        
        @raise socket.timeout: if no data could be sent before the timeout set
            by L{settimeout}.
        
        @since: 1.1
        """
        size = len(s)
        self.lock.acquire()
        try:
            size = self._wait_for_send_window(size)
            if size == 0:
                # eof or similar
                return 0
            m = Message()
            m.add_byte(chr(MSG_CHANNEL_EXTENDED_DATA))
            m.add_int(self.remote_chanid)
            m.add_int(1)
            m.add_string(s[:size])
            self.transport._send_user_message(m)
        finally:
            self.lock.release()
        return size

    def sendall(self, s):
        """
        Send data to the channel, without allowing partial results.  Unlike
        L{send}, this method continues to send data from the given string until
        either all data has been sent or an error occurs.  Nothing is returned.

        @param s: data to send.
        @type s: str

        @raise socket.timeout: if sending stalled for longer than the timeout
            set by L{settimeout}.
        @raise socket.error: if an error occured before the entire string was
            sent.
        
        @note: If the channel is closed while only part of the data hase been
            sent, there is no way to determine how much data (if any) was sent.
            This is irritating, but identically follows python's API.
        """
        while s:
            if self.closed:
                # this doesn't seem useful, but it is the documented behavior of Socket
                raise socket.error('Socket is closed')
            sent = self.send(s)
            s = s[sent:]
        return None

    def sendall_stderr(self, s):
        """
        Send data to the channel's "stderr" stream, without allowing partial
        results.  Unlike L{send_stderr}, this method continues to send data
        from the given string until all data has been sent or an error occurs.
        Nothing is returned.
        
        @param s: data to send to the client as "stderr" output.
        @type s: str
        
        @raise socket.timeout: if sending stalled for longer than the timeout
            set by L{settimeout}.
        @raise socket.error: if an error occured before the entire string was
            sent.
            
        @since: 1.1
        """
        while s:
            if self.closed:
                raise socket.error('Socket is closed')
            sent = self.send_stderr(s)
            s = s[sent:]
        return None

    def makefile(self, *params):
        """
        Return a file-like object associated with this channel.  The optional
        C{mode} and C{bufsize} arguments are interpreted the same way as by
        the built-in C{file()} function in python.

        @return: object which can be used for python file I/O.
        @rtype: L{ChannelFile}
        """
        return ChannelFile(*([self] + list(params)))

    def makefile_stderr(self, *params):
        """
        Return a file-like object associated with this channel's stderr
        stream.   Only channels using L{exec_command} or L{invoke_shell}
        without a pty will ever have data on the stderr stream.
        
        The optional C{mode} and C{bufsize} arguments are interpreted the
        same way as by the built-in C{file()} function in python.  For a
        client, it only makes sense to open this file for reading.  For a
        server, it only makes sense to open this file for writing.
        
        @return: object which can be used for python file I/O.
        @rtype: L{ChannelFile}

        @since: 1.1
        """
        return ChannelStderrFile(*([self] + list(params)))
        
    def fileno(self):
        """
        Returns an OS-level file descriptor which can be used for polling, but
        but I{not} for reading or writing).  This is primaily to allow python's
        C{select} module to work.

        The first time C{fileno} is called on a channel, a pipe is created to
        simulate real OS-level file descriptor (FD) behavior.  Because of this,
        two OS-level FDs are created, which will use up FDs faster than normal.
        You won't notice this effect unless you open hundreds or thousands of
        channels simultaneously, but it's still notable.

        @return: an OS-level file descriptor
        @rtype: int
        
        @warning: This method causes channel reads to be slightly less
            efficient.
        """
        self.lock.acquire()
        try:
            if self.pipe is not None:
                return self.pipe.fileno()
            # create the pipe and feed in any existing data
            self.pipe = pipe.make_pipe()
            if len(self.in_buffer) > 0:
                self.pipe.set()
            return self.pipe.fileno()
        finally:
            self.lock.release()

    def shutdown(self, how):
        """
        Shut down one or both halves of the connection.  If C{how} is 0,
        further receives are disallowed.  If C{how} is 1, further sends
        are disallowed.  If C{how} is 2, further sends and receives are
        disallowed.  This closes the stream in one or both directions.

        @param how: 0 (stop receiving), 1 (stop sending), or 2 (stop
            receiving and sending).
        @type how: int
        """
        if (how == 0) or (how == 2):
            # feign "read" shutdown
            self.eof_received = 1
        if (how == 1) or (how == 2):
            self.lock.acquire()
            try:
                m = self._send_eof()
            finally:
                self.lock.release()
            if m is not None:
                self.transport._send_user_message(m)
    
    def shutdown_read(self):
        """
        Shutdown the receiving side of this socket, closing the stream in
        the incoming direction.  After this call, future reads on this
        channel will fail instantly.  This is a convenience method, equivalent
        to C{shutdown(0)}, for people who don't make it a habit to
        memorize unix constants from the 1970s.
        
        @since: 1.2
        """
        self.shutdown(0)
    
    def shutdown_write(self):
        """
        Shutdown the sending side of this socket, closing the stream in
        the outgoing direction.  After this call, future writes on this
        channel will fail instantly.  This is a convenience method, equivalent
        to C{shutdown(1)}, for people who don't make it a habit to
        memorize unix constants from the 1970s.
        
        @since: 1.2
        """
        self.shutdown(1)


    ###  calls from Transport


    def _set_transport(self, transport):
        self.transport = transport
        self.logger = util.get_logger(self.transport.get_log_channel() + '.' + self.name)

    def _set_window(self, window_size, max_packet_size):
        self.in_window_size = window_size
        self.in_max_packet_size = max_packet_size
        # threshold of bytes we receive before we bother to send a window update
        self.in_window_threshold = window_size // 10
        self.in_window_sofar = 0
        self._log(DEBUG, 'Max packet in: %d bytes' % max_packet_size)
        
    def _set_remote_channel(self, chanid, window_size, max_packet_size):
        self.remote_chanid = chanid
        self.out_window_size = window_size
        self.out_max_packet_size = max(max_packet_size, self.MIN_PACKET_SIZE)
        self.active = 1
        self._log(DEBUG, 'Max packet out: %d bytes' % max_packet_size)

    def _request_success(self, m):
        self._log(DEBUG, 'Sesch channel %d request ok' % self.chanid)
        self.event.set()
        return

    def _request_failed(self, m):
        self.lock.acquire()
        try:
            msgs = self._close_internal()
        finally:
            self.lock.release()
        for m in msgs:
            if m is not None:
                self.transport._send_user_message(m)

    def _feed(self, m):
        if type(m) is str:
            # passed from _feed_extended
            s = m
        else:
            s = m.get_string()
        self.lock.acquire()
        try:
            if self.ultra_debug:
                self._log(DEBUG, 'fed %d bytes' % len(s))
            if self.pipe is not None:
                self.pipe.set()
            self.in_buffer += s
	    self.in_buffer_cv.notifyAll()
        finally:
            self.lock.release()

    def _feed_extended(self, m):
        code = m.get_int()
        s = m.get_string()
        if code != 1:
            self._log(ERROR, 'unknown extended_data type %d; discarding' % code)
            return
        if self.combine_stderr:
            return self._feed(s)
        self.lock.acquire()
        try:
            if self.ultra_debug:
                self._log(DEBUG, 'fed %d stderr bytes' % len(s))
            self.in_stderr_buffer += s
            self.in_stderr_buffer_cv.notifyAll()
        finally:
            self.lock.release()
        
    def _window_adjust(self, m):
        nbytes = m.get_int()
        self.lock.acquire()
        try:
            if self.ultra_debug:
                self._log(DEBUG, 'window up %d' % nbytes)
            self.out_window_size += nbytes
            self.out_buffer_cv.notifyAll()
        finally:
            self.lock.release()

    def _handle_request(self, m):
        key = m.get_string()
        want_reply = m.get_boolean()
        server = self.transport.server_object
        ok = False
        if key == 'exit-status':
            self.exit_status = m.get_int()
            self.status_event.set()
            ok = True
        elif key == 'xon-xoff':
            # ignore
            ok = True
        elif key == 'pty-req':
            term = m.get_string()
            width = m.get_int()
            height = m.get_int()
            pixelwidth = m.get_int()
            pixelheight = m.get_int()
            modes = m.get_string()
            if server is None:
                ok = False
            else:
                ok = server.check_channel_pty_request(self, term, width, height, pixelwidth,
                                                      pixelheight, modes)
        elif key == 'shell':
            if server is None:
                ok = False
            else:
                ok = server.check_channel_shell_request(self)
        elif key == 'exec':
            cmd = m.get_string()
            if server is None:
                ok = False
            else:
                ok = server.check_channel_exec_request(self, cmd)
        elif key == 'subsystem':
            name = m.get_string()
            if server is None:
                ok = False
            else:
                ok = server.check_channel_subsystem_request(self, name)
        elif key == 'window-change':
            width = m.get_int()
            height = m.get_int()
            pixelwidth = m.get_int()
            pixelheight = m.get_int()
            if server is None:
                ok = False
            else:
                ok = server.check_channel_window_change_request(self, width, height, pixelwidth,
                                                                pixelheight)
        else:
            self._log(DEBUG, 'Unhandled channel request "%s"' % key)
            ok = False
        if want_reply:
            m = Message()
            if ok:
                m.add_byte(chr(MSG_CHANNEL_SUCCESS))
            else:
                m.add_byte(chr(MSG_CHANNEL_FAILURE))
            m.add_int(self.remote_chanid)
            self.transport._send_user_message(m)

    def _handle_eof(self, m):
        self.lock.acquire()
        try:
            if not self.eof_received:
                self.eof_received = True
                self.in_buffer_cv.notifyAll()
                self.in_stderr_buffer_cv.notifyAll()
                if self.pipe is not None:
                    self.pipe.set_forever()
        finally:
            self.lock.release()
        self._log(DEBUG, 'EOF received')

    def _handle_close(self, m):
        self.lock.acquire()
        try:
            msgs = self._close_internal()
            self.transport._unlink_channel(self.chanid)
        finally:
            self.lock.release()
        for m in msgs:
            if m is not None:
                self.transport._send_user_message(m)


    ###  internals...


    def _log(self, level, msg):
        self.logger.log(level, msg)

    def _set_closed(self):
        # you are holding the lock.
        self.closed = True
        self.in_buffer_cv.notifyAll()
        self.in_stderr_buffer_cv.notifyAll()
        self.out_buffer_cv.notifyAll()
        if self.pipe is not None:
            self.pipe.set_forever()

    def _send_eof(self):
        # you are holding the lock.
        if self.eof_sent:
            return None
        m = Message()
        m.add_byte(chr(MSG_CHANNEL_EOF))
        m.add_int(self.remote_chanid)
        self.eof_sent = True
        self._log(DEBUG, 'EOF sent')
        return m

    def _close_internal(self):
        # you are holding the lock.
        if not self.active or self.closed:
            return None, None
        m1 = self._send_eof()
        m2 = Message()
        m2.add_byte(chr(MSG_CHANNEL_CLOSE))
        m2.add_int(self.remote_chanid)
        self._set_closed()
        # can't unlink from the Transport yet -- the remote side may still
        # try to send meta-data (exit-status, etc)
        return m1, m2

    def _unlink(self):
        # server connection could die before we become active: still signal the close!
        if self.closed:
            return
        self.lock.acquire()
        try:
            self._set_closed()
            self.transport._unlink_channel(self.chanid)
        finally:
            self.lock.release()

    def _check_add_window(self, n):
        # already holding the lock!
        if self.closed or self.eof_received or not self.active:
            return 0
        if self.ultra_debug:
            self._log(DEBUG, 'addwindow %d' % n)
        self.in_window_sofar += n
        if self.in_window_sofar <= self.in_window_threshold:
            return 0
        if self.ultra_debug:
            self._log(DEBUG, 'addwindow send %d' % self.in_window_sofar)
        out = self.in_window_sofar
        self.in_window_sofar = 0
        return out

    def _wait_for_send_window(self, size):
        """
        (You are already holding the lock.)
        Wait for the send window to open up, and allocate up to C{size} bytes
        for transmission.  If no space opens up before the timeout, a timeout
        exception is raised.  Returns the number of bytes available to send
        (may be less than requested).
        """
        # you are already holding the lock
        if self.closed or self.eof_sent:
            return 0
        if self.out_window_size == 0:
            # should we block?
            if self.timeout == 0.0:
                raise socket.timeout()
            # loop here in case we get woken up but a different thread has filled the buffer
            timeout = self.timeout
            while self.out_window_size == 0:
                if self.closed or self.eof_sent:
                    return 0
                then = time.time()
                self.out_buffer_cv.wait(timeout)
                if timeout != None:
                    timeout -= time.time() - then
                    if timeout <= 0.0:
                        raise socket.timeout()
        # we have some window to squeeze into
        if self.closed or self.eof_sent:
            return 0
        if self.out_window_size < size:
            size = self.out_window_size
        if self.out_max_packet_size - 64 < size:
            size = self.out_max_packet_size - 64
        self.out_window_size -= size
        if self.ultra_debug:
            self._log(DEBUG, 'window down to %d' % self.out_window_size)
        return size
        

class ChannelFile (BufferedFile):
    """
    A file-like wrapper around L{Channel}.  A ChannelFile is created by calling
    L{Channel.makefile}.

    @bug: To correctly emulate the file object created from a socket's
        C{makefile} method, a L{Channel} and its C{ChannelFile} should be able
        to be closed or garbage-collected independently.  Currently, closing
        the C{ChannelFile} does nothing but flush the buffer.
    """

    def __init__(self, channel, mode = 'r', bufsize = -1):
        self.channel = channel
        BufferedFile.__init__(self)
        self._set_mode(mode, bufsize)

    def __repr__(self):
        """
        Returns a string representation of this object, for debugging.

        @rtype: str
        """
        return '<paramiko.ChannelFile from ' + repr(self.channel) + '>'

    def _read(self, size):
        return self.channel.recv(size)

    def _write(self, data):
        self.channel.sendall(data)
        return len(data)
    
    seek = BufferedFile.seek


class ChannelStderrFile (ChannelFile):
    def __init__(self, channel, mode = 'r', bufsize = -1):
        ChannelFile.__init__(self, channel, mode, bufsize)

    def _read(self, size):
        return self.channel.recv_stderr(size)
    
    def _write(self, data):
        self.channel.sendall_stderr(data)
        return len(data)


# vim: set shiftwidth=4 expandtab :
