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
import hackersh.components.internal.ipv4_address


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.0"


# Implementation

class Nslookup(hackersh.objects.RootComponent):

    def run(self, argv, context):

        _context = False

        try:

            # i.e. '127.0.0.1'

            if isinstance(argv[0], basestring):

                _context = hackersh.components.internal.ipv4_address.IPv4_Address().run([socket.gethostbyname(argv[0])], {})

            # i.e. RemoteSessionContext(HOSTNAME='localhost', ...)

            else:

                __context = hackersh.objects.RemoteSessionContext(argv[0])

                _context = hackersh.components.internal.ipv4_address.IPv4_Address().run([socket.gethostbyname(__context['HOSTNAME'])], {})

                _context.update(__context)

                # Turn HOSTNAME into a shadowed key

                __context['_HOSTNAME'] = __context['HOSTNAME']

                del __context['HOSTNAME']

        except socket.error as e:

            # i.e. socket.gaierror: [Errno -5] No address associated with hostname

            self.logger.debug('Caught exception %s' % str(e))

            pass

        return _context
