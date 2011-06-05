#!/usr/bin/env python
 
from distutils.core import setup
from ts3 import __version__
 
setup(name = "python-ts3",
	version = __version__,
	description = "TS3 ServerQuery library for Python",
	author = "Andrew Willaims",
	author_email = "andy@tensixtyone.com",
	url = "https://github.com/nikdoof/python-ts3/",
	py_modules = ['ts3',],
)
