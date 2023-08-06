#!/usr/bin/python

import tcpsocket
import sys
import getopt
import logging
import logger

def printUsage():
    scriptName = 'pyknxcall.py'
    print 'USAGE:'
    print scriptName + ' [-c communicatoraddress] [-a|--argument argname=argvalue [-a|--argument argname=argvalue [...]]] function'
    print ''
    print 'OPTIONS:'
    print '\t-c --comm-addr              Address of the communicator. This must be of the form <hostname:port> of <ipaddress:port>. Default is localhost:1029'
    print '\t-a --argument               Argument to pass to user function. It is of the form argument_name=argument_value. Be careful not to insert whitespaces around the "=" sign.'
    print '\t--help                      Display this help message and exit.'

def parseAddress(addrStr, option):
    ix = addrStr.find(':')
    if ix < 0:
        raise Exception('Malformed value for ' + option +'. Expecting a tuple (hostname:port)')
    return (addrStr[0:ix], int(addrStr[ix + 1:]))

if __name__ == '__main__':
    logger.initLogger(None, logging.INFO)
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'c:a:', ['comm-addr=', 'argument=', 'verbose=', 'help'])
    except getopt.GetoptError as err:
        logger.reportException()
        sys.exit(2)

    # Parse command line arguments.
    communicatorAddress = ('127.0.0.1',1029)
    arguments = []
    verbosity = logging.INFO
    for option, value in options:
        if option == '-c' or option == '--comm-addr':
            communicatorAddress = parseAddress(value, option)
        elif option == '-a' or option == '--argument':
            arguments.append(value)
        elif option == '--help':
            printUsage()
            sys.exit(1)
        elif option == '--verbose':
            lValue = value.lower()
            if lValue == 'error':
                verbosity = logging.ERROR
            elif lValue == 'warning':
                verbosity = logging.WARNING
            elif lValue == 'info':
                verbosity = logging.INFO
            elif lValue == 'debug':
                verbosity = logging.DEBUG
            else:
                print 'Unknown verbosity level ' + value
        else:
            logger.reportError('Unrecognized option ' + option)
            sys.exit(2)

    if not remainder:
        logger.reportError('Missing function name.')
        printUsage()
        sys.exit(3)

    if len(remainder) > 1:
        logger.reportError('Too many arguments: {0}'.format(remainder))
        printUsage()
        sys.exit(4)

    functionName = remainder[0]

    # Init logger.
    logger.initLogger(None, verbosity)

    s = tcpsocket.Socket()
    s.connect(communicatorAddress)
    message=functionName
    for arg in arguments:
        message += '|{0}'.format(arg)
    s.sendData(message, '$')

