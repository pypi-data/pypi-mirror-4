import os
import tempfile
from ConfigParser import SafeConfigParser
from ConfigParser import NoOptionError
from com.sixsq.slipstream.exceptions import Exceptions
from com.sixsq.slipstream import util

def getContextualizer():
    return LocalContextualizer()

'''
Example of local contextualisation file:
[contextualization]
nodename=<node-name>
diid=<run-id>
serviceurl=http://slipstream.stratuslab.eu
username=<username>
password=<password>
'''
class LocalContextualizer(object):
    LOCAL_CONTEXTUALIZATION_FILENAME = 'slipstream.context'
    LOCAL_CONTEXTUALIZATION_LOCATIONS = [os.getcwd(), os.path.expanduser('~'), 
                                         tempfile.gettempdir(), 
                                         '/opt/slipstream/client/sbin']
    SECTION = 'contextualization'

    def __init__(self):
        self.verboseLevel = 0
        self.configFile = None
        self._load()

    def getContextAsDict(self):
        return dict(self.parser.items(LocalContextualizer.SECTION))

    def _load(self):
        self.parser = self._getParser()

    def _getParser(self):
        parser = SafeConfigParser()
        self.configFile = self._getConfigFile()
        parser.read(self.configFile)
        return parser

    def _getConfigFile(self):
        for location in LocalContextualizer.LOCAL_CONTEXTUALIZATION_LOCATIONS:
            filename = os.path.join(location, LocalContextualizer.LOCAL_CONTEXTUALIZATION_FILENAME)
            if os.path.exists(filename):
                util.printDetail('Using local configuration file: %s' % filename, self.verboseLevel)
                return filename
        raise Exceptions.ConfigurationError('Failed to find local configuration file.')

    def __getattr__(self, key):
        return self._get(key)

    def _get(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        value = None
        try:
            value = self.parser.get(LocalContextualizer.SECTION, key)
        except NoOptionError:
            pass
        value = os.getenv('SLIPSTREAM_' + key.upper(), value)

        if not value:
            raise KeyError('Failed to find key %s in file %s' % (key, self.configFile))

        self.__setattr__(key, value)

        return value

    def set(self, key, value):
        self.parser.set(LocalContextualizer.SECTION, key, value)
        self.parser.write(open(self.configFile,'w'))

    def __str__(self):
        output = '* %s:\n' % self.__class__.__name__
        for k,v in self.__dict__.items():
            output += '  %s = %s\n' % (str(k), str(v))
        return output

