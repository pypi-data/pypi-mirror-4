#!/usr/bin/python

from xml.dom.minidom import parse
from linknx import ObjectConfig
import sys
import getopt
import codecs
import logger
import logging

class Configurator:
    """ Object able to automatically patch the linknx configuration xml to add python bindings. """
    def __init__(self, sourceFile, outputFile, address, rulePrefix):
        self._address = address
        self._sourceFile = sourceFile
        self._outputFile = outputFile
        self._userFileGlobals = {}
        self._rulePrefix = rulePrefix
        self._config = None
        self.ioportServiceName = 'pyknxcommunicator'

    @property
    def config(self):
        if not self._config:
            doc = parse(self._sourceFile)
            self._config = doc.getElementsByTagName('config')[0]
        return self._config

    def cleanConfig(self):
        # Delete all pyknx rules before creating only those that apply to the
        # current config.
        rulesNode = self._getOrAddConfigElement(self.config, 'rules')
        prefixLength = len(self._rulePrefix)
        configuredAtLeastOne = False
        for ruleNode in rulesNode.getElementsByTagName('rule'):
            ruleId = ruleNode.getAttribute('id')
            if ruleId[:prefixLength] == self._rulePrefix:
                configuredAtLeastOne = True
                logger.reportInfo('Clean rule ' + ruleId + ' coming from a previous configure.')
                rulesNode.removeChild(ruleNode)

        if not configuredAtLeastOne:
            logger.reportInfo('Input XML config does not define any pyknx rule. Nothing to clean.')

        servicesNode = self._getOrAddConfigElement(self.config, 'services')
        ioportsNode = self._getOrAddConfigElement(servicesNode, 'ioports')
        for ioportNode in ioportsNode.getElementsByTagName('ioport'):
            if ioportNode.getAttribute('id') == 'pyknxcommunicator':
                logger.reportInfo('Clean ' + ioportNode.toxml())
                ioportsNode.removeChild(ioportNode)

    def createActionNode(self, callbackName, args):
        doc = self.config.ownerDocument
        actionNode = doc.createElement('action')
        actionNode.setAttribute('type', 'ioport-tx')
        actionNode.setAttribute('ioport', self.ioportServiceName)
        dataStr = callbackName
        if not args is None:
            for argName, argValue in args.iteritems():
                dataStr += '|{0}={1}'.format(argName, argValue)
        actionNode.setAttribute('data', dataStr + '$')
        return actionNode

    def generateConfig(self):
        # Read xml to get pyknx special attributes.
        config = self.config
        doc = config.ownerDocument
        rulesNode = self._getOrAddConfigElement(config, 'rules')

        # Generate a rule for each object that has a callback in the user file.
        objectNodes = config.getElementsByTagName('objects')[0]
        configuredAtLeastOne = False
        for objectNode in objectNodes.getElementsByTagName('object'):
            objectConfig = ObjectConfig(objectNode)
            objectId = objectConfig.id
            if not objectConfig.callback:
                logger.reportDebug('No callback found for object ' + objectConfig.id)
                continue

            configuredAtLeastOne = True
            ruleNode = doc.createElement('rule')
            logger.reportInfo('Generating rule pyknxrule_' + objectId)
            ruleNode.setAttribute('id', self._rulePrefix + objectId)
            ruleNode.setAttribute('init', 'false')
            conditionNode = doc.createElement('condition')
            conditionNode.setAttribute('type', 'object')
            conditionNode.setAttribute('id', objectId)
            # conditionNode.setAttribute('value', objectConfig.defaultValue)
            conditionNode.setAttribute('trigger', 'true')
            ruleNode.appendChild(conditionNode)
            actionListNode = doc.createElement('actionlist')
            actionListNode.setAttribute('type', 'if-true')
            ruleNode.appendChild(actionListNode)
            actionNode = self.createActionNode(objectConfig.callback, {'objectId' : objectId})
            actionListNode.appendChild(actionNode)
            # actionListIfFalseNode = actionListNode.cloneNode(True)
            # actionListIfFalseNode.setAttribute('type', 'on-false')
            # # ruleNode.appendChild(actionListIfFalseNode)
            rulesNode.appendChild(ruleNode)

        if not configuredAtLeastOne:
            logger.reportInfo('Nothing to do. None of the objects does define a pyknxcallback attribute.')
        else:
            # Add an ioport service for the communicator.
            servicesNode = self._getOrAddConfigElement(config, 'services')
            ioportsNode = self._getOrAddConfigElement(servicesNode, 'ioports')
            ioportNode = doc.createElement('ioport')
            ioportNode.setAttribute('id', self.ioportServiceName)
            ioportNode.setAttribute('host', self._address[0])
            ioportNode.setAttribute('port', str(self._address[1]))
            ioportNode.setAttribute('type', 'tcp')
            ioportsNode.appendChild(ioportNode)


    def writeConfig(self):
        outputXMLFile = codecs.open(self._outputFile, mode='w', encoding='utf-8')
        outputXMLFile.write(self.config.toxml())
        outputXMLFile.close()
        logger.reportInfo('Output config written to ' + self._outputFile)


    def _getOrAddConfigElement(self, parent, elementTagName):
        elementNodes = parent.getElementsByTagName(elementTagName)
        if not elementNodes:
            elementNode = parent.ownerDocument.createElement(elementTagName)
            parent.appendChild(elementNode)
            logger.reportInfo('No <' + elementTagName + '> element in config, creating one.')
        else:
            elementNode = elementNodes[0]
        return elementNode

def printUsage():
    scriptName = 'pyknxconf.py'
    print 'USAGE:'
    print scriptName + ' [-c communicatoraddress] -i inputfile [-o outputfile]'
    print ''
    print 'OPTIONS:'
    print '\t-c --comm-addr <host:port>       Address of the communicator. This argument must specify the hostname or the ip address followed by a colon and the port to listen on. Default is localhost:1029'
    print '\t-i --inputfile                   Filename of the original linknx xml config file. This file is modified by this script if no output file is specified.'
    print '\t-o --outputfile                  Filename of the modified linknx xml config file to write. If missing, this argument defaults to the same file than the one specified with --inputfile.'
    print '\t--rule-prefix                    Prefix for the rules generated by this script. Default is "pyknxrule_"'
    print '\t--clean                          Clean rules that were generated by this script but do not generate new rules. Rules to delete are those whose id starts by the rule prefix'
    print '\t--help                           Display this help message and exit.'


def parseAddress(addrStr, option):
    ix = addrStr.find(':')
    if ix < 0:
        raise Exception('Malformed value for ' + option +'. Expecting a tuple (hostname:port)')
    return (addrStr[0:ix], addrStr[ix + 1:])

if __name__ == '__main__':
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'c:i:o:p:', ['comm-addr=', 'input-file=', 'output-file=', 'rule-prefix=', 'verbose', 'clean', 'help'])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    # Parse command line arguments.
    communicatorAddress = ('127.0.0.1',1029)
    inputFile = None
    outputFile = None
    rulePrefix = 'pyknxrule_'
    cleanOnly = False
    verbosity = logging.INFO
    for option, value in options:
        if option == '-c' or option == '--comm-addr':
            communicatorAddress = parseAddress(value, option)
        elif option == '-i' or option == '--input-file':
            inputFile = value
        elif option == '-o' or option == '--output-file':
            outputFile = value
        elif option == '-p' or option == '--rule-prefix':
            rulePrefix = value
        elif option == '--verbose':
            verbosity = logging.DEBUG
        elif option == '--clean':
            cleanOnly = True
        elif option == '--help':
            printUsage()
            sys.exit(1)
        else:
            print 'Unrecognized option ' + option
            sys.exit(2)

    if not inputFile:
        printUsage()
        sys.exit(1)

    if not outputFile:
        outputFile = inputFile

    # Configure logger.
    logger.initLogger(None, verbosity)

    # Start configurator.
    configurator = Configurator(inputFile, outputFile, communicatorAddress, rulePrefix)

    # Generate config.
    configurator.cleanConfig()
    if not cleanOnly:
        configurator.generateConfig()
    configurator.writeConfig()
