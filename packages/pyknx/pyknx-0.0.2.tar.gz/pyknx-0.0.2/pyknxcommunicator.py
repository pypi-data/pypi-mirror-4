#!/usr/bin/python

import sys
import getopt
import signal
import time
import logger
import logging
from linknx import *
from communicator import *

def signal_handler(signal, frame):
	logger.reportInfo('Terminating...')
	communicator.stopListening()

def printUsage():
	scriptName = 'pyknxcommunicator.py'
	print 'USAGE:'
	print scriptName + ' [-l linknxaddress] [-c communicatoraddress] -f userfile'
	print ''
	print 'OPTIONS:'
	print '\t-l --linknx-addr			 Address of the linknx daemon. This must be of the form <hostname:port> of <ipaddress:port>. Default is localhost:1028'
	print '\t-c --comm-addr				 Address the communicator will bind to. This must be of the form <hostname:port> of <ipaddress:port>. Default is localhost:1029'
	print '\t-f --user-file				 Filename of the python script that implement the callbacks specified in linknx XML configuration.'
	print '\t   --verbose				 Verbosity level, amongst [debug, info, warning, error]. Default is info.'
	print '\t--help						 Display this help message and exit.'

def parseAddress(addrStr, option):
	ix = addrStr.find(':')
	if ix < 0:
		raise Exception('Malformed value for ' + option +'. Expecting a tuple (hostname:port)')
	return (addrStr[0:ix], int(addrStr[ix + 1:]))

if __name__ == '__main__':
	logger.initLogger(None, logging.INFO)
	try:
		try:
			options, remainder = getopt.getopt(sys.argv[1:], 'c:l:f:', ['comm-addr=', 'linknx-addr=', 'user-file=', 'log-file=', 'verbose=', 'pid-file=', 'help'])
		except getopt.GetoptError as err:
			logger.reportException()
			sys.exit(2)

		# Parse command line arguments.
		communicatorAddress = ('127.0.0.1',1029)
		linknxAddress = ('127.0.0.1',1028)
		userFile = None
		configFile = None
		verbosity = logging.INFO
		logFile = None
		pidFile = None
		# TODO Add support for script arguments (already implemented in
		# Communicator).
		for option, value in options:
			if option == '-c' or option == '--comm-addr':
				communicatorAddress = parseAddress(value, option)
			elif option == '-l' or option == '--linknx-addr':
				linknxAddress = parseAddress(value, option)
			elif option == '-f' or option == '--user-file':
				userFile = value
			elif option == '--help':
				printUsage()
				sys.exit(1)
			elif option == '--log-file':
				logFile = value
			elif option == '--pid-file':
				pidFile = value
			elif option == '--verbose':
				verbosity = logger.parseLevel(value)
			else:
				logger.reportError('Unrecognized option ' + option)
				sys.exit(2)

		# Init logger.
		if not logFile is None:
			logger.initLogger((logFile, verbosity), None)
		else:
			logger.initLogger(None, verbosity)

		if not userFile:
			printUsage()
			sys.exit(1)

		if remainder:
			logger.reportError('Unknown arguments {0}.'.format(remainder))
			printUsage()
			sys.exit(3)

		# Create pid file.
		# Start linknx.
		linknx = Linknx(linknxAddress[0], linknxAddress[1])

		# Start communicator.
		communicator = Communicator(linknx, userFile, communicatorAddress)
		communicator.startListening()

		signal.signal(signal.SIGINT, signal_handler)
		signal.signal(signal.SIGTERM, signal_handler)

		# Main loop.
		while communicator.isListening:
			time.sleep(1)
	except:
		logger.reportException()
