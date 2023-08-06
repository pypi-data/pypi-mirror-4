#!/usr/bin/python

import tcpsocket
import sys
import getopt
import time
import os.path
import logger
import logging
import importlib
from threading import *
from linknx import *

class CallbackContext(object):
	def __init__(self, communicator, args={}):
		# if not args is None and args.has_key('objectId'):
			# self._object = linknx.getObject(args['objectId'])
		# else:
			# self._object = None
		self._communicator = communicator
		self._args = args

		# Create members for easy access.
		for argName, argValue in args.iteritems():
			# Create argument. Do not set its value with exec since handling
			exec('self.{0} = "{1}"'.format(argName, argValue))
		if args.has_key('objectId'):
			self._object = self.linknx.getObject(self.objectId)
		else:
			self._object = None

	@property
	def object(self):
		return self._object

	@property
	def linknx(self):
		return self._communicator.linknx

	@property
	def communicator(self):
		return self._communicator

	@property
	def customArgs(self):
		return self._args

	def getArgument(self, argName, defaultValue = None):
		if self.customArgs.has_key(argName):
			return self.customArgs[argName]
		else:
			return defaultValue

	def __str__(self):
		return str(self._args)

class Communicator:
	class Listener(Thread):
		""" Thread that listens for incoming connection from linknx. """
		def __init__(self, address, communicator):
			Thread.__init__(self, name='Communicator Listening Thread')
			self._address = address
			self._isStopRequested = False
			self._socket = tcpsocket.Socket() # socket to listen on for information coming from linknx.
			self._communicator = communicator
			self.linknx = self._communicator.linknx
			self.isReady = False

		def isListening(self):
			return not self._socket is None and self.isReady
		@property
		def isStopped(self):
			return self._socket is None

		def run(self):
			logger.reportInfo('Listening on ' + str(self._address))
			self._isStopRequested = False
			try:
				self._socket.bind(self._address)

				# Thread loop.
				while not self._isStopRequested:
					self.isReady = True
					data, conn = self._socket.waitForData('$')
					# Throw data away if script has not been initialized yet.
					# See startListening for details.
					if data is None or not self._communicator.isUserScriptInitialized:
						time.sleep(0.1)
						continue

					logger.reportDebug('Data received: {0}'.format(data))

					# Handle request.
					tokens = data.split('|')
					callbackName = tokens[0]
					# Parse arguments. First is object id.
					args={}
					for token in tokens[1:]:
						argName, sep, argValue = token.partition('=')
						if argValue: argValue = argValue.strip()
						args[argName.strip()] = argValue
					context = CallbackContext(self, args)
					res = self._communicator._executeUserCallback(callbackName, context)
					if res:
						conn.sendall(res + '$')
					conn.close()
			except Exception as e:
				logger.reportException()
			finally:
				logger.reportDebug('Closing socket...')
				self._socket.close()
				logger.reportInfo('Socket closed. Listening terminated.')
				self._socket = None

		def stop(self):
			logger.reportInfo('Stopping listener thread...')
			self._isStopRequested = True

	def __init__(self, linknx, userFile, address=('localhost',1029), userScriptArgs={}):
		self._address = address
		self._listenerThread = None # thread that owns the listening socket, None if not listening.
		self._userFile = userFile
		self._linknx = linknx
		self._userModule = None
		self._userScriptArgs = userScriptArgs
		self.isUserScriptInitialized = False

	@property
	def isListening(self):
		return not self._listenerThread is None

	@property
	def linknx(self):
		return self._linknx

	@property
	def address(self):
		return self._address

	def loadUserFile(self):
		# Append the directory that contains the user script to python path.
		if self._userFile:
			dirName, fileName = os.path.split(self._userFile)
			dirName = os.path.abspath(dirName)
			moduleName, fileExt = os.path.splitext(fileName)
			sys.path.append(dirName)
			logger.reportDebug('loadUserFile: moduleName={0} fileExt={1} dirName={2}'.format(moduleName, fileExt, dirName))
			self._userModule = importlib.import_module(moduleName)
			logger.reportDebug('Imported {0}'.format(self._userModule.__file__))
			return True
		else:
			logger.reportError('No user file specified.')
			return False

	def startListening(self):
		""" Start listening for incoming information from linknx. """
		if self.isListening: return

		# Make sure linknx is ready.
		self.linknx.waitForRemoteConnectionReady()

		# Start listening early to avoid communication errors from linknx. Those
		# error are never harmful but the user may be surprized and worried
		# about them! 
		self._listenerThread = Communicator.Listener(self._address, self)
		self._listenerThread.start()
		timeout = time.time() + 4
		while not self._listenerThread.isReady and time.time() < timeout:
			time.sleep(0.3)
		if not self._listenerThread.isReady:
			raise Exception('Could not initialize listening socket.')

		# Initialize user-provided script. The purpose of this callback is to
		# let the user initialize its script by reading state from linknx (and
		# possibly anywhere else). Thus, linknx should not raise events yet,
		# since user script would likely be partially initialized. The
		# isUserScriptInitialized flag is used for that purpose.
		if self.loadUserFile():
			logger.reportInfo('Initializing user script...')
			try:
				self._executeUserCallback('initializeUserScript', CallbackContext(self, args=self._userScriptArgs), True)
			except Exception as e:
				logger.reportException('User script initialization failed, communicator will stop immediately.')
				self.stopListening()
				return
			logger.reportInfo('User script initialized.')
		self.isUserScriptInitialized = True


	def stopListening(self):
		# Notify user script first. This allows linknx to notify a few object
		# changes before communicator really stop listening.
		if self._userFile and self.isUserScriptInitialized:
			self._executeUserCallback('finalizeUserScript', CallbackContext(self), True)
			logger.reportInfo('User script finalized.')

		if not self.isListening: return
		self._listenerThread.stop()

		# Wait for listener thread to end (to be sure that no callback
		# request originating from linknx can reach the user script anymore).
		while not self._listenerThread.isStopped:
			time.sleep(0.5)
		self._listenerThread = None

		if self._userFile:
			self._executeUserCallback('endUserScript', CallbackContext(self), True)
			logger.reportInfo('User script ended.')

	def _executeUserCallback(self, callbackName, context, isOptional=False):
		try:
			if hasattr(self._userModule, callbackName):
				logger.reportDebug('Calling user callback {0} with context {1}'.format(callbackName, context))
				callback = getattr(self._userModule, callbackName)
				res = callback(context)
				logger.reportDebug('Callback {0} returned {1}'.format(callbackName, res))
				return res
			else:
				message='No function {0} defined in {1}'.format(callbackName, self._userFile)
				if isOptional:
					logger.reportInfo(message + ', skipping')
				else:
					logger.reportWarning(message)
		except Exception as e:
			logger.reportException('User code execution failed.')
