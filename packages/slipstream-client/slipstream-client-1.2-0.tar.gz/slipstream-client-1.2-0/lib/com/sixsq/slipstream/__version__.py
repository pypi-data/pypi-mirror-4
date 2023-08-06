#!/usr/bin/env python
# coding=latin-1
version = "1.1-0"

def getVersion():
    global version
    return version

def getFullVersion():
    global version
    return "%s" % version

def getCopyright():
    return '''Copyright (c) SixSq Sàrl. 2013. http://www.sixsq.com'''

def getLicense():
    return '''
TODO.'''

def getPrettyVersion():
    str = '\nSlipStream Client version: %s\n\n' % getFullVersion()
    str += getCopyright()
    return str

def getLongVersion():
    str = '\nSlipStream Client version: %s\n\n' % getFullVersion()
    str += getCopyright()
    str += getLicense()
    return str
    
