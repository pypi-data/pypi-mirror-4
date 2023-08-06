#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  setup.py
#
#  Copyright 2013 dominiquehunziker <dominique.hunziker@gmail.com>
#  Copyright 2013 Dhananjay Sathe <dhananjaysathe@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from setuptools import setup, Extension

LONGSDESC = """
Twisted-based WebSocket/WAMP client and server framework.
Modifeid and optimised for the RoboEarth Cloud Engine

AutobahnPython provides a WebSocket (RFC6455, Hybi-10 to -17, Hixie-76)
framework for creating WebSocket-based clients and servers.

AutobahnPython also includes an implementation of WAMP
(The WebSockets Application Messaging Protocol), a light-weight,
asynchronous RPC/PubSub over JSON/WebSocket protocol.

More information:

   * http://autobahn.ws/python
   * http://wamp.ws

Source Code:

   * https://github.com/IDSCETHZurich/autobahn_rce
"""

## get version string from "autobahn/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

ext_modules = [
    Extension('autobahn.utf8validator', ['src/utf8validator.c']),
    Extension('autobahn.xormasker', ['src/xormasker.c']),
    ]

setup (
   name = 'autobahn_rce',
   version = verstr,
   description = 'AutobahnPython - Optimised and modified for the RoboEarth Cloud Engine.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Dhananjay Sathe',
   author_email = 'dhananjaysathe@gmail.com',
   url = 'https://github.com/IDSCETHZurich/autobahn_rce',
   platforms = ('Any'),
   install_requires = ['setuptools', 'Twisted>=11.1'],
   packages = ['autobahn'],
   ext_modules=ext_modules,
   zip_safe = False,
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries"],
   keywords = 'autobahn rapyuta autobahn.ws websocket realtime rfc6455 wamp rpc pubsub'
)
