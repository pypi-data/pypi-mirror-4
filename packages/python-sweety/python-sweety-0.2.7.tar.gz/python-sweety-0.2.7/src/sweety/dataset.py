#!/usr/bin/env python
'''
sweety.dataset

@author: Yunzhi Zhou (Chris Chou)
'''

import copy

from . import prettytable

def print_table(data, colnames = [], aligns = [], format = 'console'):
    x = prettytable.PrettyTable(
                                field_names = colnames,
                                border = True
                                )

    for i, f in enumerate(x.field_names):
        if len(aligns) <= i:
            x.align[f] = 'l'
        else:
            x.align[f] = aligns[i]
    for l in data:
        x.add_row(l)

    if format == 'html':
        x.print_html()
    elif format == 'console':
        x.printt(hrules = prettytable.FRAME)
        
def write_table(data, fp, sep = '\t'):
    fp.writelines(
                  ['%s\n' % sep.join([str(c) for c in rec]) for rec in data]
                  )
    
def write_list(data, fp):
    fp.writelines(
                  ['%s\n' % rec for rec in data]
                  )
    
def read_table(fp, sep = '\t', types = []):
    ret = []
    for l in fp:
        l = l.strip().split(sep)
        for i, c in enumerate(l):
            if i >= len(types):
                break
            c = types[i](c)
            l[i] = c
        ret.append(l)

    return ret

def read_list(fp, typefunc = str):
    ret = []
    for l in fp:
        l = l.strip('\r\n')
        ret.append(typefunc(l))
        
    return ret

def update_table(old, new, bycol = 0, sort = False):
    ret = copy.copy(new)
    keys = set([rec[bycol] for rec in new])
    for rec in old:
        key = rec[0]
        if key not in keys:
            ret.append(rec)
            keys.add(key)
            
    if sort:
        #ret.sort(lambda x,y: -1 if x[0] < y[0] else (1 if x[0] > y[0] else 0))
        ret.sort()
            
    return ret

def merge_table(t1, t2, bycol = 0):
    raise NotImplemented()
    