#!/usr/bin/env python
'''
This software code is made available "AS IS" without warranties of any kind.
You may NOT copy, display, modify or redistribute the software code or binaries
either by itself or as incorporated into your code, without the explicit
written permission from SixSq.  Your use of this software code is at your own
risk and you waive any claim against SixSq Sarl with respect to your use of
this software code. (c) 2011 SixSq Sarl. All rights reserved.

SixSq: http://www.sixsq.com
'''

import com.sixsq.slipstream.util as util
from com.sixsq.slipstream.contextualizers.ContextualizerFactory import ContextualizerFactory


class ConfigHolder(object):

    @staticmethod
    def configFileToDict(configFileName):
        config = ConfigHolder.parseConfig(configFileName)
        _dict = ConfigHolder._convertToDict(config)
        return _dict

    @staticmethod
    def parseConfig(filename):
        return util.parseConfigFile(filename)

    @staticmethod
    def _convertToDict(config):
        dict = {}
        for section in config.sections():
            for k,v in config.items(section):
                dict[k] = v
        return dict

    @staticmethod
    def assignAttributes(obj, dictionary):
        util.assignAttributes(obj, dictionary)

    def __init__(self, options={}, config={}, context={}, configFile=''):
        # command line options
        self.options = self._extractDict(options)
        self.options['ssLogDir'] = util.REPORTSDIR
        # classes to instantiate via Factories
        self.config = config or self._getConfigFromFileAsDict(configFile)
        # SlipStream context
        self.context = context or ContextualizerFactory.getContextAsDict()

    def _getConfigFromFileAsDict(self, filename=''):
        configFileName = filename or util.getConfigFileName()
        return self.configFileToDict(configFileName)

    def _extractDict(self, obj):
        if isinstance(obj, dict):
            return obj

        _dict = {}
        for k,v in obj.__dict__.items():
            if not k.startswith('_') and not callable(v):
                _dict[k] = v
        return _dict

    def assign(self, obj):
        self.assignConfig(obj)
        self.assignOptions(obj)
        self.assignContext(obj)

    def assignConfig(self, obj):
        ConfigHolder.assignAttributes(obj, self.config)

    def assignOptions(self, obj):
        ConfigHolder.assignAttributes(obj, self.options)

    def assignContext(self, obj):
        ConfigHolder.assignAttributes(obj, self.context)

    def assignOptionsAndContext(self, obj):
        self.assignOptions(obj)
        self.assignContext(obj)

    def assgnConfigAndOptions(self, obj):
        self.assignConfig(obj)
        self.assignOptions(obj)

    def set(self, key, value):
        self.options[key] = value

    def copy(self):
        copy = ConfigHolder(self.options.copy(), self.config.copy(), self.context.copy())
        return copy

    def __str__(self):
        output = '* %s:\n' % self.__class__.__name__
        for p in ['options', 'config', 'context']:
            if getattr(self, p):
                output += '** %s:\n' % p.upper()
                output += '  %s\n' % str(getattr(self, p))
        return output

    def __getattr__(self, key):
        if key in self.options:
            source = self.options
        elif key in self.config:
            source = self.config
        elif key in self.context:
            source = self.context
        else:
            raise ValueError('Can\'t find key: %s' % key)
        return source.get(key)
