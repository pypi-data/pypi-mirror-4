#!/usr/bin/env python

from distutils.core import setup

VERSION = '1.2-0'
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: Unix",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

setup(name='slipstream-client',
      version=VERSION,
      description='SlipStream end-user client (CLI)',
      long_description='SlipStream client (CLI) to communicate with SlipStream server.',
      author='SixSq Sarl, (sixsq.com)',
      author_email='info@sixsq.com',
      license='Apache License, Version 2.0',
      platforms='Any',
      url='http://sixsq.com',

      scripts = ['bin/ss-abort',
                 'bin/ss-display',
                 'bin/ss-execute',
                 'bin/ss-get',
                 'bin/ss-set',
                 'bin/ss-module-get',
                 'bin/ss-module-put',
                 'bin/ss-run-get',
                 'bin/ss-user-get'],

      packages = ['com', 
                  'com.sixsq',
                  'com.sixsq.slipstream.contextualizers',
                  'com.sixsq.slipstream.contextualizers.dummy'],

      package_dir = {'com': 'lib/com'},

      py_modules = ['com.sixsq.slipstream.ConfigHolder',    
                    'com.sixsq.slipstream.contextualizers.ContextualizerFactory',
                    'com.sixsq.slipstream.CommandBase',
                    'com.sixsq.slipstream.Client',
                    'com.sixsq.slipstream.exceptions.Exceptions',
                    'com.sixsq.slipstream.NodeDecorator',
                    'com.sixsq.slipstream.HttpClient',
                    'com.sixsq.slipstream.SlipStreamHttpClient',
                    'com.sixsq.slipstream.util',
                    'com.sixsq.slipstream.__version__'],
        
      requires=['httplib2'],

      classifiers=CLASSIFIERS
      )
