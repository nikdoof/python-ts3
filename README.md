
python-ts3
==========

python-ts3 is a abstraction library around the Teamspeak 3 ServerQuery API. It
allows native access to the ServerQuery API with most of the formatting
headaches avoided.

[![Build Status](https://travis-ci.org/nikdoof/python-ts3.png?branch=develop)](https://travis-ci.org/nikdoof/python-ts3)

Python Support
--------------

At the moment python-ts3 supports Python 2.6 and Python 2.7.

Python 3 support is on the todo list.


Install
-------

Download the most recent sourcecode and install it::

	git clone git://github.com/nikdoof/python-ts3.git
	cd python-ts3
	python setup.py install

A stable version of python-ts3 is available on PyPi. Active development is done in the `develop` branch with release version merged into `master`


Example Usage
-------------

Example showing how to create a channel and sub-channel for it using python-ts3 library::

	import ts3

	server = ts3.TS3Server('127.0.0.1', 10011)
	server.login('serveradmin', 'secretpassword')

	# choose virtual server
	server.use(1)

	# create a channel
	response = server.send_command('channelcreate', keys={'channel_name': 'Just some channel'})

	# id of the newly created channel
	channel_id = response.data[0]['cid']

	# create a sub-channel
	server.send_command('channelcreate', keys={'channel_name': 'Just some sub-channel', 'cpid': channel_id})
