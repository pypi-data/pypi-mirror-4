#!/usr/bin/env python
'''
sweety.conf

@author: Yunzhi Zhou (Chris Chou)
'''

import importlib
import os
from os.path import join, expandvars, realpath, expanduser

from valuebag import ValueBag

__all__ = ['settings', 'version', 'config']

#def expand_path(path):
#    return realpath(expandvars(expanduser(path)))
  
class GlobalSettings(ValueBag):
    def __init__(self, d = {}):
        super(GlobalSettings, self).__init__(d)        
        #for key in dir(default_settings):
        #    if key == key.upper():
        #        setattr(self, key, getattr(default_settings, key))
                
        if os.environ.has_key('OPT_SETTINGS_MODULE'):
            ns = os.environ['OPT_SETTINGS_MODULE']
            mod = None
            if ns:
               mod = importlib.import_module(ns)
                
            if mod:
                for key in dir(mod):
                    if key == key.upper():
                        #v = getattr(mod, key)
                        setattr(self, key, getattr(mod, key))
                

config = GlobalSettings({
                           'ENV_VIRTUAL_ENV'    : 'VIRTUAL_ENV',
                           'ENV_VERBOSE'        : 'OPT_VERBOSE',
                           'ENV_PROGRAM'        : 'OPT_PROGRAM',
                           'ENV_LOG_FILENAME'   : 'OPT_LOG_FILENAME',
                           'ENV_LOGGER_PID'     : 'OPT_LOGGER_PID',
                           'ENV_LOGGER_SOCKFILE': 'OPT_LOGGER_SOCKFILE',
                           'ENV_PID'            : 'OPT_PID',
                           'ENV_PIDFILE'        : 'OPT_PIDFILE'
                           })

config.ROOT_DIR = '$VIRTUAL_ENV/..'  # expand_path('$VIRTUAL_ENV/..')
if os.environ.has_key('OPT_SITE_DIR'):
    config.SITE_DIR = os.environ['OPT_SITE_DIR'] # expand_path(os.environ['OPT_SITE_DIR'])
else:
    config.SITE_DIR = join(config.ROOT_DIR, 'site')
config.DATA_DIR = join(config.SITE_DIR, 'data')
config.LOGS_DIR = join(config.SITE_DIR, 'logs')
config.TMP_DIR = join(config.SITE_DIR, 'tmp')

settings = config

version = ValueBag()
version.VERSION = 'Unspecified'
