from time import sleep
from ts3 import TS3Server

"""
Automover

Automatically moves a list of Client DB IDs to a specified room, and checks for
them every 5 seconds
"""

# List of cldbids to move
moveids = [1111]

# Destination channel
destination = 5

####

server = TS3Server('127.0.0.1', 10011, 1)
server.login('serveradmin', 'supersecretpassword')

while True:
    clientlist = server.clientlist()

    for client in clientlist.values():
        if client['client_database_id'] in moveids and not int(client['cid']) == destination:
            print "Found ID %s: %s" (client['client_database_id'], client['client_nickname'])
            if server.send_client('clientmove', keys={'clid': client['clid'], 'cid': channel}).is_successful:
                print "Moved %s to Channel %s" % (client['client_nickname'], channel)
    sleep(5)
