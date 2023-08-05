#!/usr/bin/python

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
do the unit tests!
"""

import sys, os, unittest
from optparse import OptionParser
import paramiko

sys.path.append('tests/')

from test_message import MessageTest
from test_file import BufferedFileTest
from test_pkey import KeyTest
from test_kex import KexTest
from test_transport import TransportTest
from test_sftp import SFTPTest

default_host = 'localhost'
default_user = os.environ.get('USER', 'nobody')
default_keyfile = os.path.join(os.environ.get('HOME', '/'), '.ssh/id_rsa')
default_passwd = None

parser = OptionParser('usage: %prog [options]')
parser.add_option('--no-pkey', action='store_false', dest='use_pkey', default=True,
                  help='skip RSA/DSS private key tests (which can take a while)')
parser.add_option('--no-transport', action='store_false', dest='use_transport', default=True,
                  help='skip transport tests (which can take a while)')
parser.add_option('--no-sftp', action='store_false', dest='use_sftp', default=True,
                  help='skip SFTP client/server tests, which can be slow')
parser.add_option('--no-big-file', action='store_false', dest='use_big_file', default=True,
                  help='skip big file SFTP tests, which are slow as molasses')
parser.add_option('-R', action='store_false', dest='use_loopback_sftp', default=True,
                  help='perform SFTP tests against a remote server (by default, SFTP tests ' +
                  'are done through a loopback socket)')
parser.add_option('-H', '--sftp-host', dest='hostname', type='string', default=default_host,
                  metavar='<host>',
                  help='[with -R] host for remote sftp tests (default: %s)' % default_host)
parser.add_option('-U', '--sftp-user', dest='username', type='string', default=default_user,
                  metavar='<username>',
                  help='[with -R] username for remote sftp tests (default: %s)' % default_user)
parser.add_option('-K', '--sftp-key', dest='keyfile', type='string', default=default_keyfile,
                  metavar='<keyfile>',
                  help='[with -R] location of private key for remote sftp tests (default: %s)' %
                  default_keyfile)
parser.add_option('-P', '--sftp-passwd', dest='password', type='string', default=default_passwd,
                  metavar='<password>',
                  help='[with -R] (optional) password to unlock the private key for remote sftp tests')

options, args = parser.parse_args()
if len(args) > 0:
    parser.error('unknown argument(s)')

if options.use_sftp:
    if options.use_loopback_sftp:
        SFTPTest.init_loopback()
    else:
        SFTPTest.init(options.hostname, options.username, options.keyfile, options.password)
    if not options.use_big_file:
        SFTPTest.set_big_file_test(False)

# setup logging
paramiko.util.log_to_file('test.log')
    
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(MessageTest))
suite.addTest(unittest.makeSuite(BufferedFileTest))
if options.use_pkey:
    suite.addTest(unittest.makeSuite(KeyTest))
suite.addTest(unittest.makeSuite(KexTest))
if options.use_transport:
    suite.addTest(unittest.makeSuite(TransportTest))
if options.use_sftp:
    suite.addTest(unittest.makeSuite(SFTPTest))
unittest.TextTestRunner(verbosity=2).run(suite)
