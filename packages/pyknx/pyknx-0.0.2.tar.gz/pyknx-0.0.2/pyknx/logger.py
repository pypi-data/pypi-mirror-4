#!/usr/bin/python

import logging
import traceback
import os.path
import sys
import signal

logHandlers = []
stdOutLog = None # None to disable stdout logging, otherwise log level.
fileLog = None # Tuple (filename, level)

def initLogger(fileLogInfo=None, stdoutLogLevel=logging.INFO):
    global logHandler
    global logFilename
    global logLevel

    _setHandlers(None, None)
    _setHandlers(fileLogInfo, stdoutLogLevel)
    logging.getLogger().setLevel(logging.DEBUG)
    signal.signal(signal.SIGUSR1, _usr1SignalHandler)
    reportDebug('Logger initialized.')

def parseLevel(levelToString):
	lValue = levelToString.lower()
	if lValue == 'error':
		return logging.ERROR
	elif lValue == 'warning':
		return logging.WARNING
	elif lValue == 'info':
		return logging.INFO
	elif lValue == 'debug':
		return logging.DEBUG
	else:
		raise Exception('Unknown verbosity level ' + levelToString)

def _setHandlers(fileLogInfo, stdoutLogLevel):
    global logHandlers
    global fileLog
    global stdOutLogLevel

    logger = logging.getLogger()

    # Remove previous handlers.
    for handler in logHandlers:
        logger.removeHandler(handler)

	if not fileLogInfo is None and not isinstance(fileLogInfo, tuple):
		raise Exception('File log info should be specified with a tuple (filename, loglevel).')

    fileLog = fileLogInfo
    stdOutLog = stdoutLogLevel

    # Create new handlers.
    logHandlers = []
    if not fileLog is None:
        _addHandler(logging.FileHandler(fileLog[0]), fileLog[1])
    if not stdoutLogLevel is None:
        _addHandler(logging.StreamHandler(), stdoutLogLevel)

def _addHandler(handler, logLevel):
    global logHandlers

    handler.setLevel(logLevel)
    logHandlers.append(handler)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(threadName)s] [%(callerfilename)s:%(callerlineno)d] %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

def _usr1SignalHandler(signalNumber, frame):
    if signalNumber == signal.SIGUSR1:
        reportInfo('USR1 signal caught. Means that log file has to be reloaded.')
        _setHandlers(fileLog, stdOutLog)

def _reportMessage(message, level):
    stack = traceback.extract_stack()
    frame = stack[len(stack) -3]
    extraDict={'callerfilename' : os.path.basename(frame[0]), 'callerlineno' : frame[1]}
    logging.getLogger().log(level, message, extra=extraDict)

def reportDebug(message):
    _reportMessage(message, logging.DEBUG)

def reportError(message):
    _reportMessage(message, logging.ERROR)
    # logging.getLogger().error(message)

def reportWarning(message):
    _reportMessage(message, logging.WARNING)
    # logging.getLogger().warning(message)

def reportInfo(message):
    _reportMessage(message, logging.INFO)
    # logging.getLogger().info(message)

def reportException(message=None):
    if not message: message = 'Exception caught.'
    _reportMessage(message + ' Traceback is:\n' + traceback.format_exc(), logging.ERROR)
