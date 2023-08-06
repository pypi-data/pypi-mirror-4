#!/usr/bin/python

import sys
import getopt
import traceback
import logging
import logger
from xml.dom.minidom import parseString
from threading import *
from linknx import *

def printUsage():
	scriptName = 'pyknxclient.py'
	print(scriptName + " python script - Copyright (C) 2012 Cyrille Defranoux\n\
This script acts as a lightweight client for linknx. It is aimed at reading or writing object values from/to linknx. Its read and write functions may be imported in another script but it may be used merely from command line as well.\n\n\
Syntax when used from command line:\n" +
		scriptName + " [-h host] [-p port] [-r OBJECT_ID] [-w OBJECT_ID=value] [-v]\n\n\
		Where OBJECT_ID is the identifier of the object as specified in the linknx configuration XML by the 'id' attribute.\n\n\
		OPTIONS:\n\
		   -h, --host			Hostname of the machine running the linknx daemon (default is 'localhost').\n\
		   -p, --port			Port linknx listens on (default is 1028).\n\
		   -r, --read OBJECT_ID	Read value of object with id OBJECT_ID. Can occur multiple times and can be used in conjunction with -w options.\n\
		   -w, --write value	Changes the object's value to the specified value.\n\
		   -v, --verbose		Let the script output useful information, for debugging purpose.")

if __name__ == '__main__':
	logger.initLogger(None, logging.INFO)

	try:
		options, remainder = getopt.getopt(sys.argv[1:], 'rw:h:p:v:', ['read', 'write=','host=', 'port=','verbose=','help'])
	except getopt.GetoptError as err:
		logger.reportException()
		sys.exit(2)

	# Parse command line arguments.
	reads = False
	writes = False
	valueToWrite = None
	objectId = None
	host = 'localhost'
	port = 1028
	verbosity = logging.WARNING
	for option, value in options:
		if option == '-r' or option == '--read':
			reads = True
		elif option == '-w' or option == '--write':
			writes = True
			valueToWrite = value
		elif option == '-h' or option == '--host':
			host = value
		elif option == '-p' or option == '--port':
			port = value
		elif option == '-v' or option == '--verbose':
			verbosity = logger.parseLevel(value)
		elif option == '--help':
			printUsage()
			sys.exit(1)
		else:
			print 'Unrecognized option ' + option
			sys.exit(2)

	logger.initLogger(None, verbosity)

	if reads == writes:
		print 'Expecting -r or -w.'
		printUsage()
		sys.exit(2)

	if len(remainder) < 1:
		print 'No object id specified.'
		printUsage()
		sys.exit(3)

	if len(remainder) > 1:
		print 'Too many arguments: ' + str(remainder)
		sys.exit(4)
	objectId = remainder[0]

	# Start linknx.
	linknx = Linknx(host, int(port))
	try:
		if reads:
			print str(linknx.getObject(objectId).value)
		elif writes:
			linknx.getObject(objectId).value = valueToWrite
	except Exception as e:
		if verbosity == logging.DEBUG:
			logger.reportException()
		else:
			logger.reportError(sys.exc_info()[1])
		sys.exit(3)
