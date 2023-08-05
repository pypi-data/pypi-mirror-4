#!/usr/bin/env python

#
# :copyright: (c) 2012 by Mike Taylor
# :license: BSD 2-Clause
#

_version_   = u'0.5.0'
_copyright_ = u'Copyright (c) 2012 Mike Taylor'
_license_   = u'BSD 2-Clause'
__author__  = u'bear (Mike Taylor) <bear@code-bear.com>'

import os
import sys
import json
import types
import logging

from optparse import OptionParser


_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
log      = logging.getLogger(_ourName)


class BearConfig(object):
    def __init__(self, configFile=None):
        """ Parse command line parameters and populate the options object
        """
        self.log        = logging.getLogger(_ourName)
        self.options    = None
        self.appPath    = _ourPath
        self.configFile = configFile
        self.config     = { 'config':  ('-c', '--config',  self.configFile, 'Configuration File'),
                            'debug':   ('-d', '--debug',   False,           'Enable Debug'),
                            'logpath': ('-l', '--logpath', '',              'Path where log file is to be written'),
                            'verbose': ('-v', '--verbose', False,           'show extra output from remote commands'),
                          }

        self.load()

    def addConfig(self, key, shortCmd='', longCmd='', defaultValue=None, helpText=''):
        if len(shortCmd) + len(longCmd) == 0:
            log.error('You must provide either a shortCmd or a longCmd value - both cannot be empty')
        elif key is None and type(key) is types.StringType:
            log.error('The configuration key must be a string')
        else:
            self.config[key] = (shortCm, longCmd, defaultValue, helpText)

    def load(self, defaults=None):
        parser        = OptionParser()
        self.defaults = {}

        if defaults is not None:
            for key in defaults:
                self.defaults[key] = defaults[key]

        for key in self.config:
            items = self.config[key]

            (shortCmd, longCmd, defaultValue, helpText) = items

            if type(defaultValue) is types.BooleanType:
                parser.add_option(shortCmd, longCmd, dest=key, action='store_true', default=defaultValue, help=helpText)
            else:
                parser.add_option(shortCmd, longCmd, dest=key, default=defaultValue, help=helpText)

        (self.options, self.args) = parser.parse_args()

        if self.options.config is None:
            s = os.path.join(_ourPath, '%s.cfg' % _ourName)
            if os.path.isfile(s):
                self.options.config = s

        if self.options.config is not None:
            self.options.config = os.path.abspath(self.options.config)

            if not os.path.isfile(self.options.config):
                self.options.config = os.path.join(_ourPath, '%s.cfg' % self.options.config)

            if not os.path.isfile(self.options.config):
                self.options.config = os.path.abspath(os.path.join(_ourPath, '%s.cfg' % _ourName))

            self.loadJSON(self.options.config)

        if self.options.logpath is not None:
            self.options.logpath = os.path.abspath(self.options.logpath)

            if os.path.isdir(self.options.logpath):
                self.options.logfile = os.path.join(self.options.logpath, '%s.log'% _ourName)
            else:
                self.options.logfile = None

    def loadJSON(filename):
        """ Read, parse and return given config file
        """
        jsonConfig = {}

        if os.path.isfile(filename):
            try:
                jsonConfig = json.loads(' '.join(open(filename, 'r').readlines()))
            except:
                log.error('error during loading of config file [%s]' % filename, exc_info=True)

        for key in jsonConfig:
            setattr(self.options, key, jsonConfig[key])

        return result

    def initLogs(self, echo=True, chatty=False, loglevel=logging.INFO):
        """ Initialize logging
        """
        if self.options.logpath is not None:
            fileHandler   = logging.FileHandler(os.path.join(self.options.logpath, '%s.log' % _ourName))
            fileFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(processName)s: %(message)s')

            fileHandler.setFormatter(fileFormatter)

            self.log.addHandler(fileHandler)
            self.log.fileHandler = fileHandler

        if echo:
            echoHandler = logging.StreamHandler()

            if chatty:
                echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(processName)s[%(process)d]: %(message)s')
            else:
                echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')

            echoHandler.setFormatter(echoFormatter)

            self.log.addHandler(echoHandler)
            self.log.info('echoing')

        if self.options.debug:
            self.log.setLevel(logging.DEBUG)
            self.log.info('debug level is on')
        else:
            self.log.setLevel(loglevel)
