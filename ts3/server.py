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
from .protocol import TS3Proto, InvalidArguments
from .defines import *


class TS3Server(TS3Proto):
    def __init__(self, ip=None, port=10011, id=0):
        """
        Abstraction class for TS3 Servers

        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int

        """
        TS3Proto.__init__(self)
        self._logger = logging.getLogger(__name__)
        if ip and port:
            if self.connect(ip, port) and id > 0:
                self.use(id)

    @property
    def logger(self):
        return self._logger

    def login(self, username, password):
        """
        Login to the TS3 Server

        @param username: Username
        @type username: str
        @param password: Password
        @type password: str
        """
        
        response = self.send_command('login', keys={'client_login_name': username, 'client_login_password': password})
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
        @type msg: str
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

    def clientlist(self):
        """
        Returns a clientlist of the current connected server/vhost
        """

        response = self.send_command('clientlist')

        if response.is_successful:
            clientlist = {}
            for client in response.data:
                clientlist[client['clid']] = client
            return clientlist
        else:
            # TODO: Raise a exception?
            self.logger.debug("clientlist - error retrieving client list")
            return {}

    def clientkick(self, clid=None, cldbid=None, type=REASON_KICK_SERVER, message=None):
        """
        Kicks a user identified by either clid or cldbid
        """

        client = None
        if cldbid:
            clientlist = self.send_command('clientlist')
            for cl in clientlist.values():
                if int(cl['client_database_id']) == cldbid:
                    client = cl['clid']
                    self.logger.debug("clientkick - identified user from clid (%s = %s)" % (cldbid, client))
                    break
            
            if not client:
                # TODO: we should throw an exception here actually
                self.logger.debug("clientkick - no client with specified cldbid (%s) was found" % cldbid)
                return False
        elif clid:
            client = clid
        else:
            raise InvalidArguments('No clid or cldbid provided')

        if not message:
            message = ''
        else:
            # Kick message can only be 40 characters
            message = message[:40]

        if client:
            self.logger.debug("clientkick - Kicking clid %s" % client)
            response = self.send_command('clientkick', keys={'clid': client, 'reasonid': type, 'reasonmsg': message})
            return response.is_successful

        return False

    def clientpoke(self, clid, message):
        """
        Poke a client with the specified message
        """

        response = self.send_command('clientpoke', keys={'clid': clid, 'msg': message})
        return response.is_successful
