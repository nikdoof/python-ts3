from time import sleep
from ts3 import TS3Server

"""
Automover

Automatically moves a list of Client DB IDs to a specified room, and checks for
them every 5 seconds
"""

# List of people to move
#
# name: defines a fixed name for that user, will kick them after warning
# destination: forces a user into a particular channel.
moveids = {
    4306: {'name': 'daley', 'destination': 405}
}

####

server = TS3Server('127.0.0.1', 10011, 1)
server.login('serveradmin', 'supersecretpassword')

print("Logged In")

poke = []

while True:
    clientlist = server.clientlist()

    for client in clientlist.values():
        # Check if the client is in the Move IDs
        if int(client['client_database_id']) in moveids:
            clinfo = moveids[int(client['client_database_id'])]
            print("Found ID %s: %s" % (client['client_database_id'], client['client_nickname']))

            # If we have a channel defined and they're not in it, move them
            if 'destination' in clinfo and not int(client['cid']) == clinfo['destination']:
                if server.send_command('clientmove', keys={'clid': client['clid'], 'cid': clinfo['destination']}).is_successful:
                    print("Moved %s to Channel %s" % (client['client_nickname'], clinfo['destination']))

            # If we have a fixed name defined, tell them to change it or kick them
            if 'name' in clinfo and not client['client_nickname'] == clinfo['name']:
                if not client['clid'] in poke:
                    poke[client['clid']] = 0
                poke[client['clid']] += 1
                print("Warning %s out of 3" % poke[client['clid']])
                server.send_command('clientpoke', keys={'clid': client['clid'], 'msg': 'Change your name to "%s"! Warning %s of 3' % (clinfo['name'], poke[client['clid']])})
                if poke > 3:
                    server.send_command('clientkick', keys={'clid': client['clid'], 'reasonid': 5})
            else:
                poke[client['clid']] = 0

    sleep(5)
