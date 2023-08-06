#!/usr/bin/env python
'''
sweety.conf

@author: Yunzhi Zhou (Chris Chou)
'''

import importlib
import os
from os.path import join, expandvars, realpath, expanduser

from valuebag import ValueBag

__all__ = ['settings', 'version']

def expand_path(path):
    return realpath(expandvars(expanduser(path)))
  
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
                try:
                    mod = importlib.import_module(ns)
                except:
                    pass
                
            if mod:
                for key in dir(mod):
                    if key == key.upper():
                        setattr(self, key, expand_path(getattr(mod, key)))
                

settings = GlobalSettings({
                           'ENV_VIRTUAL_ENV'    : 'VIRTUAL_ENV',
                           'ENV_VERBOSE'        : 'OPT_VERBOSE',
                           'ENV_PROGRAM'        : 'OPT_PROGRAM',
                           'ENV_LOG_FILENAME'   : 'OPT_LOG_FILENAME',
                           'ENV_LOGGER_PID'     : 'OPT_LOGGER_PID',
                           'ENV_LOGGER_SOCKFILE': 'OPT_LOGGER_SOCKFILE',
                           'ENV_PID'            : 'OPT_PID',
                           'ENV_PIDFILE'        : 'OPT_PIDFILE'
                           })

settings.ROOT_DIR = expand_path('$VIRTUAL_ENV/..')
if os.environ.has_key('OPT_SITE_DIR'):
    settings.SITE_DIR = expand_path(os.environ['OPT_SITE_DIR'])
else:
    settings.SITE_DIR = join(settings.ROOT_DIR, 'site')
settings.DATA_DIR = join(settings.SITE_DIR, 'data')
settings.LOGS_DIR = join(settings.SITE_DIR, 'logs')
settings.TMP_DIR = join(settings.SITE_DIR, 'tmp')

version = ValueBag()
version.VERSION = 'Unspecified'
