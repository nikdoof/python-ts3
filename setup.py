#!/usr/bin/env python
 
from setuptools import setup
from ts3 import __version__
 
setup(
    name="python-ts3",
    version=__version__,
    description="TS3 ServerQuery library for Python",
    author="Andrew Willaims",
    author_email="andy@tensixtyone.com",
    url="https://github.com/nikdoof/python-ts3/",
    keywords="teamspeak ts3 voice serverquery teamspeak3",
    packages=['ts3'],
    scripts=['examples/gents3privkey.py'],
    test_suite='ts3.test.suite',
    test_require=['unittest2'],

    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet',
        'Topic :: Communications',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ]
)
