#!/usr/bin/env python
#
# gents3privkey - Connects to a Teamspeak server and creates a permission key
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

"""
Connects to a TS3 Server and generates a Permission Key for the specified Server Group
"""

__version__ = "0.1"
__license__ = "BSD 3-Clause"
__copyright__ = "Copyright 2011, Andrew Williams"
__author__ = "Andrew Williams"

import sys
try:
    import argparse
except ImportError:
    sys.exit("This script requires argparse, please use Python 2.7 or install with 'pip install argparse'")
from ts3 import TS3Server
from ts3.defines import *

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--server', help="Teamspeak server address", required=True)
    parser.add_argument('-l', '--login', help="Login for the Teamspeak server query", default="serveradmin")
    parser.add_argument('-pw', '--password', help="Password for the server query user", required=True)
    parser.add_argument('-p', '--port', help="Port number of the Teamspeak server query interface", default=10011)
    parser.add_argument('-v', '--vhost', help="Virtual host ID where the key is to be generated", default=1)
    parser.add_argument('-sg', '--servergroup', help="Server group to create the permission key for")
    parser.add_argument('-cg', '--channelgroup', help="Channel group to create the permission key for")
    parser.add_argument('-ch', '--channel', help="For channel keys, which channel to give permissions on")

    args = vars(parser.parse_args())

    if 'channelgroup' in args and 'servergroup' in args:
        sys.exit("You can't specify a channel and server group")
    if 'channelgroup' in args and not 'channel' in args:
        sys.exit("You need to specify a channel to create a channelgroup key")

    ts3 = TS3Server(args['server'], args['port'], args['vhost'])
    ts3.login(args['login'], args['password'])


    if 'servergroup' in args:
        response = ts3.send_command('privilegekeyadd', keys={'tokentype': TOKEN_SERVER_GROUP, 'tokenid1': args['servergroup'], 'tokenid2': 0})
    else:
        response = ts3.send_command('privilegekeyadd', keys={'tokentype': TOKEN_CHANNEL_GROUP, 'tokenid1': args['channelgroup'], 'tokenid2': args['channel']})
    if response.is_successful:
        print(response.data[0]['token'])
        sys.exit(0)
    else:
       sys.exit("Error creating key: %s" % response.response['msg'])

if __name__ == '__main__':
    main()
