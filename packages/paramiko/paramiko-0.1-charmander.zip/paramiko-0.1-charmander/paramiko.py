#!/usr/bin/python

import sys

if (sys.version_info[0] < 2) or ((sys.version_info[0] == 2) and (sys.version_info[1] < 3)):
    raise RuntimeError('You need python 2.3 for this module.')

class SSHException(Exception):
    pass


from auth_transport import Transport
from channel import Channel
from rsakey import RSAKey
from dsskey import DSSKey


__author__ = "Robey Pointer <robey@lag.net>"
__date__ = "10 Nov 2003"
__version__ = "0.1-charmander"
__credits__ = "Huzzah!"

