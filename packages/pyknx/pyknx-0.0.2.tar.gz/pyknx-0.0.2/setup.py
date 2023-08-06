#!/usr/bin/python

from distutils.core import setup

setup(	name='pyknx',
		version='0.0.2',
		description='Python bindings for KNX',
		long_description='Pyknx provides modules useful for interacting with a linknx server. It allows to read/write objects configuration or object values. It also implements a communicator daemon that can be used to receive events from linknx (through ioports).',
		author='Cyrille Defranoux',
		author_email='knx@aminate.net',
		maintainer='Cyrille Defranoux',
		maintainer_email='knx@aminate.net',
		license='GNU Public General License',
		url='https://pypi.python.org/pypi/pyknx/',
		packages=['pyknx'],
		scripts=['pyknxcommunicator.py', 'pyknxcall.py', 'pyknxclient.py', 'pyknxconf.py'])
