#!/usr/bin/env python
'''
sweety.format

@author: Yunzhi Zhou (Chris Chou)
'''

import datetime
import urllib

def to_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

def to_datetime(s):
    if '.' in s:
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f')
        except:
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
    else:
        try:
            return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
        except:
            return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def to_float(s):
    try:
        return float(s)
    except:
        return float('NaN')
    
def to_int(s):
    try:
        return int(s)
    except:
        return float('NaN')
    
def quote_for_path(s):
    return urllib.quote_plus(s, ';?:@&=$,')