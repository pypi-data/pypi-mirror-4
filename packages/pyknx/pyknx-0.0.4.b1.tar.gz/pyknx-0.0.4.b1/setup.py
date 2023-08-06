#!/usr/bin/python

# Copyright (C) 2012-2013 Cyrille Defranoux
#
# This file is part of Pyknx.
#
# Pyknx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyknx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyknx. If not, see <http://www.gnu.org/licenses/>.
#
# For any question, feature requests or bug reports, feel free to contact me at:
# knx at aminate dot net

from distutils.core import setup

longdesc="""===================================
Pyknx: Python bindings for KNX\
===================================
-------------------------------
Pure python modules and scripts
-------------------------------

Pyknx is a package that is aimed at providing basic functionality related to communicating with a Linknx instance. It should help in sending or receiving data to/from Linknx.

----------------------------------------------------------------------

Why Pyknx?
========

There is no doubt that Linknx is a very powerful, stable and simple to configure solution. It is sufficient for most needs in the frame of home automation. Nevertheless, as a developer, I sometimes find frustrating not having the opportunity to replace a set of XML rules in my Linknx config by a piece of code...
I first wrote a simple python script called lwknxclient whose unique functionality is to read/write Linknx object's values. This script solved the problem of easily sending data to Linknx from a bash script.
But recently, my requirements evolved drastically as I wanted to implement my own alarm system to protect my home. I have a few door switches, cameras and smoke detectors that I wanted to use. I first implemented a simple version in pure XML that worked but it had many drawbacks:
- the configuration is quite verbose. This is the very nature of XML. Factorization is hardly ever possible.
- the configuration is tricky to test. I had to test it interactively after each modification. I quickly reached a point from which I was too afraid breaking something to add new functionality to my system.
- I had to rely on bash scripts for each non-trivial action executed by Linknx, which led to a bunch of scripts disseminated to various places on my server. Difficult to maintain too... And, no offense, but I have to respectfully admit that bash is not the kind of language I am happy to work with.
- calling external scripts from within shell-cmd actions has a major drawback: the script's lifetime is equal to the action's one. If the script has to retain some variables between two executions, it has no solution but polluting Linknx objects pool or storing data to files. None of these are convenient for a non-trivial application.

The answer to those problems was to implement a daemon in Python that would manage my alarm system. This time, I would be able to use the comprehensive Python framework, to factorize my code and to test it automatically!

How does it work?
========
Pyknx relies on the built-in **ioport communication** of Linknx. The principle is as following:
- edit your linknx XML configuration to **add a pyknxcallback attribute** on each object for which you would like a python callback to be called whenever its value changes. The value of the attribute corresponds to the name of the function to call.
- **use pyknxconf.py** to automatically append to the linknx XML configuration rules that are required for the communication to work. These rules use ioport actions to send data to the Python daemon but you don't have to mess with that if you are not willing to. It simply works, that should be enough!
- start Linknx with the above configuration.
- start an instance of the communicator using **pyknxcommunicator.py**. The name of a file of your own that implements every function declared with pyknxcallback attributes shall be **passed to the command line**.

And that's all. Every callback is passed a 'Context' instance that implements an **'object' property** which can be used to identify the object that is the source of the event on Linknx's side. Simply write 'context.object.value' to retrieve or change the value of the object.

Contents of the package
========
The archive comes with a package named pyknx that offers the following pure-python modules:
- linknx.py: common module that implements the communication with a linknx server. With this module, one can retrieve linknx objects, read or write their value, read linknx configuration, ...
- communicator.py: this module contains the Communicator daemon, whose purpose is to receive events from linknx, through ioports.  It is then easy to write callbacks to react to object modifications. Additional scripts based on pyknx are provided (see below) in order to make this bidirectional communication with linknx just a few keystrokes away from now!
- logger.py: internal module that provides logging functionality for the package.
- tcpsocket.py: an internal module that implements common functionality related to socket communication. The end-user is unlikely to use this module directly.

This package also provides additional python scripts that are intended to run as standalone executables. They are briefly explained in the sections above but the --help argument of each script should be enough to help you understand how it really works.
- pyknxconf.py is used to automatically patch your linknx XML configuration in order to generate the ioport service and the rules necessary for the communication between Linknx and the Python daemon work.
- pyknxcommunicator.py is the script that represents the daemon itself. Simply tell it where to find your user-defined python file with your implementation and it should work.
- pyknxcall.py can be used to ask the daemon to perform a function call. For instance 'pyknxcall.py -amyArgument=2 myCallback' should call the function myCallback(context) in your user-defined file and the passed context will contain a property named myArgument whose value is 2. This utility script is useful to help making external applications pass data to your daemon.
- pyknxclient.py is the replacement for the former lwknxclient.py I initially wrote a few months ago. It is a lightweight client for linknx that can retrieve or change the value of an object.

How to install
==========
The pyknx archive has been built with distutils. Uncompress it and use the setup.py script at the root of the archive to install:
python setup.py install
or
python setup.py install --user to install in your home.
Please refer to distutils documentation for further details."""


setup(	name='pyknx',
		version='0.0.4.b1',
		description='Python bindings for KNX',
		long_description=longdesc,
		author='Cyrille Defranoux',
		author_email='knx@aminate.net',
		maintainer='Cyrille Defranoux',
		maintainer_email='knx@aminate.net',
		license='GNU Public General License',
		url='https://pypi.python.org/pypi/pyknx/',
		packages=['pyknx'],
		data_files=['LICENSE'],
		scripts=['pyknxcommunicator.py', 'pyknxcall.py', 'pyknxclient.py', 'pyknxconf.py'])
