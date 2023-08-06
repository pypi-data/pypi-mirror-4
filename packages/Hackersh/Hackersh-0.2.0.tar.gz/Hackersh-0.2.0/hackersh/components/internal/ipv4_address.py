# Copyright (C) 2013 Itzik Kotler
#
# This file is part of Hackersh.
#
# Hackersh is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# Hackersh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hackersh; see the file COPYING.  If not,
# see <http://www.gnu.org/licenses/>.

import socket


# Local imports

import hackersh.objects


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class IPv4_Address(hackersh.objects.RootComponent):

    def run(self, argv, context):

        _context = False

        try:

            socket.inet_aton(argv[0])

            _context = hackersh.objects.RemoteSessionContext(IPV4_ADDRESS=argv[0])

        except socket.error, e:

            self.logger.debug('Caught exception %s' % str(e))

            # i.e. illegal IP address string passed to inet_aton

            pass

        return _context
