#!/usr/bin/python

# Copyright (C) 2003-2004 Robey Pointer <robey@lag.net>
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

import struct, socket
from common import *
import util
from channel import Channel
from message import Message

CMD_INIT, CMD_VERSION, CMD_OPEN, CMD_CLOSE, CMD_READ, CMD_WRITE, CMD_LSTAT, CMD_FSTAT, \
           CMD_SETSTAT, CMD_FSETSTAT, CMD_OPENDIR, CMD_READDIR, CMD_REMOVE, CMD_MKDIR, \
           CMD_RMDIR, CMD_REALPATH, CMD_STAT, CMD_RENAME, CMD_READLINK, CMD_SYMLINK \
           = range(1, 21)
CMD_STATUS, CMD_HANDLE, CMD_DATA, CMD_NAME, CMD_ATTRS = range(101, 106)
CMD_EXTENDED, CMD_EXTENDED_REPLY = range(200, 202)

FX_OK = 0
FX_EOF, FX_NO_SUCH_FILE, FX_PERMISSION_DENIED, FX_FAILURE, FX_BAD_MESSAGE, \
         FX_NO_CONNECTION, FX_CONNECTION_LOST, FX_OP_UNSUPPORTED = range(1, 9)

FX_DESC = [ 'Success',
            'End of file',
            'No such file',
            'Permission denied',
            'Failure',
            'Bad message',
            'No connection',
            'Connection lost',
            'Operation unsupported' ]

FXF_READ = 0x1
FXF_WRITE = 0x2
FXF_APPEND = 0x4
FXF_CREATE = 0x8
FXF_TRUNC = 0x10
FXF_EXCL = 0x20

_VERSION = 3


class SFTPError (Exception):
    pass


class BaseSFTP (object):
    def __init__(self):
        self.logger = logging.getLogger('paramiko.sftp')


    ###  internals...


    def _send_version(self):
        self._send_packet(CMD_INIT, struct.pack('>I', _VERSION))
        t, data = self._read_packet()
        if t != CMD_VERSION:
            raise SFTPError('Incompatible sftp protocol')
        version = struct.unpack('>I', data[:4])[0]
        #        if version != _VERSION:
        #            raise SFTPError('Incompatible sftp protocol')
        return version

    def _send_server_version(self):
        self._send_packet(CMD_VERSION, struct.pack('>I', _VERSION))
        t, data = self._read_packet()
        if t != CMD_INIT:
            raise SFTPError('Incompatible sftp protocol')
        version = struct.unpack('>I', data[:4])[0]
        return version
        
    def _log(self, level, msg):
        if type(msg) == type([]):
            for m in msg:
                self.logger.log(level, m)
        else:
            self.logger.log(level, msg)

    def _write_all(self, out):
        while len(out) > 0:
            n = self.sock.send(out)
            if n <= 0:
                raise EOFError()
            if n == len(out):
                return
            out = out[n:]
        return

    def _read_all(self, n):
        out = ''
        while n > 0:
            x = self.sock.recv(n)
            if len(x) == 0:
                raise EOFError()
            out += x
            n -= len(x)
        return out

    def _send_packet(self, t, packet):
        out = struct.pack('>I', len(packet) + 1) + chr(t) + packet
        if self.ultra_debug:
            self._log(DEBUG, util.format_binary(out, 'OUT: '))
        self._write_all(out)

    def _read_packet(self):
        size = struct.unpack('>I', self._read_all(4))[0]
        data = self._read_all(size)
        if self.ultra_debug:
            self._log(DEBUG, util.format_binary(data, 'IN: '));
        if size > 0:
            return ord(data[0]), data[1:]
        return 0, ''
