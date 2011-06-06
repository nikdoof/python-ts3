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

import time
import telnetlib
import logging

from defines import *

__version__ = "0.1"
__license__ = "BSD 3-Clause"
__copyright__ = "Copyright 2011, Andrew Williams"
__author__ = "Andrew Williams, Krzysztof Jagiello"

class ConnectionError(Exception):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__():
        return 'Error connecting to host %s port %s.' % (self.ip, self.port,)

class NoConnection(Exception):
    def __str__():
        return 'No connection established.' % (self.ip, self.port,)

class InvalidArguments(ValueError):
    """
    Raised when a abstracted function has received invalid arguments
    """

ts3_escape = { "\\": r'\\',
               '/': r"\/",
               ' ': r'\s',
               '|': r'\p',
               "\a": r'\a',
               "\b": r'\b',
               "\f": r'\f',
               "\n": r'\n',
               "\r": r'\r',
               "\t": r'\t',
               "\v": r'\v' }

class TS3Response():
    def __init__(self, response, data):
        self.response = TS3Proto.parse_command(response)
        self.data = TS3Proto.parse_command(data)

        if isinstance(self.data, dict):
            if self.data:
                self.data = [self.data]
            else:
                self.data = []
    
    @property
    def is_successful(self):
        return self.response['keys']['msg'] == 'ok'

class TS3Proto():

    @property
    def logger(self):
        if not hasattr(self, _logger):
            self._logger = logging.getLogger(__name__)
        return self._logger

    def connect(self, ip, port, timeout=5):
        try:
            self._telnet = telnetlib.Telnet(ip, port)
        except telnetlib.socket.error:
            raise ConnectionError(ip, port)
        
        self._timeout = timeout
        self._connected = False
        
        data = self._telnet.read_until("\n\r", self._timeout)
        
        if data.endswith("TS3\n\r"):
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
        self._telnet.write("%s\n\r" % commandstr)

        data = ""
        response = self._telnet.read_until("\n\r", self._timeout)

        if not response.startswith("error"):
            # what we just got was extra data
            data = response
            response = self._telnet.read_until("\n\r", self._timeout)
                
        return TS3Response(response, data)
    
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
    def parse_command(commandstr):
        """
        Parses a TS3 command string into command/keys/opts tuple

        @param commandstr: Command string
        @type commandstr: string
        """
        if commandstr.strip() == "":
            return {}
        
        if len(commandstr.split('|')) > 1:
            vals = []
            for cmd in commandstr.split('|'):
                vals.append(TS3Proto.parse_command(cmd))
            return vals

        cmdlist = commandstr.strip().split(' ')
        command = None
        keys = {}
        opts = []

        for key in cmdlist:
            v = key.strip().split('=')
            if len(v) > 1:
                # Key
                if len > 2:
                    # Fix the stupidities in TS3 escaping
                    v = [v[0], '='.join(v[1:])]
                key, value = v
                keys[key] = TS3Proto._unescape_str(value)
            elif v[0][0] == '-':
                # Option
                opts.append(v[0][1:])
            else:
                command = v[0]

        d = {'keys': keys, 'opts': opts}
        if command:
            d['command'] = command
        return d

    @staticmethod
    def _escape_str(value):
        """
        Escape a value into a TS3 compatible string

        @param value: Value
        @type value: string/int

        """

        if isinstance(value, int):
            return str(value)
        
        for i, j in ts3_escape.iteritems():
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
        
        for i, j in ts3_escape.iteritems():
            value = value.replace(j, i)
        
        return value


class TS3Server(TS3Proto):
    def __init__(self, ip, port, id=0):
        """
        Abstraction class for TS3 Servers

        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int

        """
        if self.connect(ip, port) and id > 0:
            self.use(id)

    @property
    def logger(self):
        if not hasattr(self, _logger):
            self._logger = logging.getLogger(__name__)
        return self._logger

    def login(self, username, password):
        """
        Login to the TS3 Server

        @param username: Username
        @type username: str
        @param password: Password
        @type password: str
        """
        
        response = self.send_command('login', keys={'client_login_name': username, 'client_login_password': password })
        return response.is_successful

    def serverlist(self):
        """
        Get a list of all Virtual Servers on the connected TS3 instance
        """
        return self.send_command('serverlist')

    def gm(self, msg):
        """
        Send a global message to the current Virtual Server

        @param msg: Message
        @type ip: str
        """
        response = self.send_command('gm', keys={'msg': msg})
        return response.is_successful

    def use(self, id):
        """
        Use a particular Virtual Server instance

        @param id: Virtual Server ID
        @type id: int
        """
        response = self.send_command('use', keys={'sid': id})
        return response.is_successful

    def clientkick(self, clid=None, cldbid=None, type=REASON_KICK_SERVER, message=None):
        """
        Kicks a user identified by either clid or cldbid
        """

        client = None
        if cldbid:
            response = self.send_command('clientlist')
            for cl in response.data:
                if int(cl['keys']['client_database_id']) == cldbid:
                    client = cl['keys']['clid']
                    self.logger.debug("clientkick - identified user from clid (%s = %s)" % (cldbid, client))
                    break
            client = 0
        elif clid:
            client = clid
        else:
            raise InvalidArguments('No clid or cldbid provided')

        if type == REASON_KICK_CHANNEL:
            if not message:
                message = ''
            else:
                # Kick message can only be 40 characters
                message = message[:40]

        if client:
            self.logger.debug("clientkick - Kicking clid %s" % client)
            response = self.send_command('clientkick', keys={'clid': client, 'reasonid': type, 'reasonmsg': message})
            return response.is_successful

        return false
