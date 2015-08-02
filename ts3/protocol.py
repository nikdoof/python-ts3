# Python TS3 Library (python-ts3)
#
# Copyright (c) 2011, Andrew Williams
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging
import telnetlib
from threading import Lock


class ConnectionError(Exception):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__(self):
        return 'Error connecting to host %s port %s.' % (self.ip, self.port)


class NoConnectionError(Exception):
    def __str__(self):
        return 'No connection established.'


class InvalidArguments(ValueError):
    """
    Raised when a abstracted function has received invalid arguments
    """


ts3_escape = [
     (chr(92), r'\\'),   # \
     (chr(47), r"\/"),   # /
     (chr(32), r'\s'),   # Space
     (chr(124), r'\p'),  # |
     (chr(7), r'\a'),    # Bell
     (chr(8), r'\b'),    # Backspace
     (chr(12), r'\f'),   # Form Feed
     (chr(10), r'\n'),   # Newline
     (chr(13), r'\r'),   # Carriage Return
     (chr(9), r'\t'),    # Horizontal Tab
     (chr(11), r'\v'),   # Vertical tab
]


class TS3Response():
    def __init__(self, response, data):
        self.response = TS3Proto.parse_response(response)
        self.data = TS3Proto.parse_data(data)

        if isinstance(self.data, dict):
            if self.data:
                self.data = [self.data]
            else:
                self.data = []

    @property
    def is_successful(self):
        return self.response['msg'] == 'ok'


class TS3Proto():

    def __init__(self):
        self.io_lock = Lock()
        self._connected = False
        self._timeout = 0
        self._telnet = None
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self):
        return self._logger

    def connect(self, ip, port=10011, timeout=5):
        with self.io_lock:
            try:
                self._telnet = telnetlib.Telnet(ip, port)
            except telnetlib.socket.error:
                raise ConnectionError(ip, port)

            self._timeout = timeout
            self._connected = False

            data = self._telnet.read_until(b"\n\r", self._timeout)

        if data.endswith(b"TS3\n\r"):
            self._connected = True

        return self._connected

    def disconnect(self):
        self.check_connection()

        self.send_command("quit")
        self._telnet.close()

        self._connected = False

    def send_command(self, command, keys=None, opts=None):
        self.check_connection()

        commandstr = self.construct_command(command, keys=keys, opts=opts)
        self.logger.debug("send_command - %s" % commandstr)

        with self.io_lock:
            self._telnet.write(commandstr.encode('utf-8') + b"\n\r")

            data = b''
            response = self._telnet.read_until(b"\n\r", self._timeout)

        if not response.startswith(b"error"):
            # what we just got was extra data
            data = response
            response = self._telnet.read_until(b"\n\r", self._timeout)

        return TS3Response(response.decode('utf-8'), data.decode('utf-8'))

    def check_connection(self):
        if not self.is_connected:
            raise NoConnectionError

    def is_connected(self):
        return self._connected

    def construct_command(self, command, keys=None, opts=None):
        """
        Constructs a TS3 formatted command string

        Keys can have a single nested list to construct a nested parameter

        @param command: Command list
        @type command: string
        @param keys: Key/Value pairs
        @type keys: dict
        @param opts: Options
        @type opts: list
        """

        cstr = [command]

        # Add the keys and values, escape as needed
        if keys:
            for key in keys:
                if isinstance(keys[key], list):
                    ncstr = []
                    for nest in keys[key]:
                        ncstr.append("%s=%s" % (key, self._escape_str(nest)))
                    cstr.append("|".join(ncstr))
                else:
                    cstr.append("%s=%s" % (key, self._escape_str(keys[key])))

        # Add in options
        if opts:
            for opt in opts:
                cstr.append("-%s" % opt)

        return " ".join(cstr)

    @staticmethod
    def parse_response(response):
        """
        Parses a TS3 command string into command/keys/opts tuple

        @param response: Command string
        @type response: string
        """

        # responses always begins with "error " so we may just skip it
        return TS3Proto.parse_data(response[6:])

    @staticmethod
    def parse_data(data):
        """
        Parses data string consisting of key=value

        @param data: data string
        @type data: string
        """
        data = data.strip()

        multipart = data.split('|')

        if len(multipart) > 1:
            values = []

            for part in multipart:
                values.append(TS3Proto.parse_data(part))
            return values

        chunks = data.split(' ')
        parsed_data = {}

        for chunk in chunks:
            chunk = chunk.strip().split('=')

            if len(chunk) > 1:
                if len(chunk) > 2:
                    # value can contain '=' which may confuse our parser
                    chunk = [chunk[0], '='.join(chunk[1:])]

                key, value = chunk
                parsed_data[key] = TS3Proto._unescape_str(value)
            else:
                # TS3 Query Server may sometimes return a key without any value
                # and we default its value to None
                parsed_data[chunk[0]] = None

        return parsed_data

    @staticmethod
    def _escape_str(value):
        """
        Escape a value into a TS3 compatible string

        @param value: Value
        @type value: string/int

        """

        if isinstance(value, int):
            return str(value)

        for i, j in ts3_escape:
            value = value.replace(i, j)

        return value

    @staticmethod
    def _unescape_str(value):
        """
        Unescape a TS3 compatible string into a normal string

        @param value: Value
        @type value: string/int

        """

        if isinstance(value, int):
            return str(value)

        for i, j in ts3_escape:
            value = value.replace(j, i)

        return value
