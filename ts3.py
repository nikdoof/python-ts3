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

class ConnectionError():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __str__():
        return 'Error connecting to host %s port %s' % (self.ip, self.port)

ts3_escape = { '/': r"\/",
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
    def __init__(self, response):
        self.response = TS3Proto.parse_command(response)
    
    def is_successful(self):
        if isinstance(self.response, dict):
            return self.response['keys']['msg'] == 'ok'
        
        # if the response is a list, it has to be successful
        return True
    
    def response(self):
        return self.response

class TS3Proto():
    def __init__(self):
        self._log = logging.getLogger('%s.%s' % (__name__, self.__class__.__name__))
        pass

    def connect(self, ip, port, timeout=5):
        self._telnet = telnetlib.Telnet(ip, port)
        self._timeout = timeout
        self._connected = False
        
        data = self._telnet.read_until("TS3\n", self._timeout)
        
        if data.endswith("TS3\n"):
            self._connected = True

        return self._connected

    def disconnect(self):
        self.send_command("quit")

        self._connected = False
        self._log.info('Disconnected')

    def send_command(self, command, keys=None, opts=None):
        cmd = self.construct_command(command, keys=keys, opts=opts)
        
        self._telnet.write("%s\n" % cmd)
                
        return TS3Response(self._telnet.read_until("\n", self._timeout))

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

        if isinstance(value, int): return "%d" % value
        value = value.replace("\\", r'\\')
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

        if isinstance(value, int): return "%d" % value
        value = value.replace(r"\\", "\\")
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
        TS3Proto.__init__(self)

        if self.connect(ip, port) and id > 0:
            self.use(id)

    def login(self, username, password):
        """
        Login to the TS3 Server

        @param username: Username
        @type username: str
        @param password: Password
        @type password: str
        """
        
        response = self.send_command('login', keys={'client_login_name': username, 'client_login_password': password })

        if response.is_successful():
            self._log.info('Login error: %s.')
            return False
        else:
            self._log.info('Login successful.')
            return True

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
        return self.send_command('gm', keys={'msg': msg})

    def use(self, id):
        """
        Use a particular Virtual Server instance

        @param id: Virtual Server ID
        @type id: int
        """
        self.send_command('use', keys={'sid': id})