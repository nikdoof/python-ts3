#!/usr/bin/env python

import sys
from setuptools import setup
from ts3 import __version__

tests_require = ['mock']
if sys.version < '2.7':
      tests_require.append('unittest2')
      tests_require.append('ordereddict')

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
    tests_require=tests_require,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet',
        'Topic :: Communications',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ]
)
