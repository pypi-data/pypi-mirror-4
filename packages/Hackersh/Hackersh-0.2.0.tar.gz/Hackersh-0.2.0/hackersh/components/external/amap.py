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

# Local imports

import hackersh.objects


# Metadata

__author__ = "Itzik Kotler <xorninja@gmail.com>"
__version__ = "0.1.1"


# Implementation

class Amap(hackersh.objects.ExternalComponentFileOutput):

    class AmapCSVOutputHandler(hackersh.objects.CSVOutputHandler):

        def startDocument(self):

            self._entry_or_entries = []

        # i.e. test.old:21:tcp:open::ftp:220 ProFTPD 1.3.4a Server (Debian) [ffff127.0.0.1]\r\n500 GET not understood\r\n500 Invalid command try being more creative\r\n:"220 ProFTPD 1.3.4a Server (Debian) [::ffff:127.0.0.1]\r\n500 GET not understood\r\n500 Invalid command: try being more creative\r\n"

        def startRow(self, row):

            try:

                # IP_ADDRESS:PORT:PROTOCOL:PORT_STATUS:SSL:IDENTIFICATION:PRINTABLE_BANNER:FULL_BANNER

                (ip_addr, port, proto, port_status, ssl, identification) = row[:6]

                self._entry_or_entries.extend([{'PROTO': proto.upper(), 'PORT': str(int(port)), 'SERVICE': identification.upper()}])

            except Exception:

                pass

        def endRow(self):

            pass

        def endDocument(self):

            for entry in self._entry_or_entries:

                self._output.append(hackersh.objects.RemoteSessionContext(self._context, **entry))

            if not self._output:

                self._output.append(self._context)

        # CSV Parsing Parameter

        delimiter = ':'

    # Consts

    DEFAULT_FILENAME = "amap"

    DEFAULT_OUTPUT_OPTIONS = "-m -o"

    DEFAULT_FILTER = \
        "(context['IPV4_ADDRESS'] or context['HOSTNAME']) and context['PROTO'] == 'TCP'"

    DEFAULT_QUERY = \
        "(context['IPV4_ADDRESS'] or context['HOSTNAME']) + ' ' + context['PORT']"
