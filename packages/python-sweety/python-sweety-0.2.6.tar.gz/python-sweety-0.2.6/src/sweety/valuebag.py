#!/usr/bin/env python
'''
sweety.valeubag

@author: Yunzhi Zhou (Chris Chou)
'''

import copy
import json
import os

#from django.core.serializers.json import DjangoJSONEncoder

__all__ = ['ValueBag']
 
class ValueBag(dict):
    def __init__(self, d = {}, auto_create = True, empty_string = None):
        super(ValueBag, self).__init__()
        
        #assert parent == None or isinstance(parent, ValueBag)  
        #self.__dict__['__parent'] = parent 
        self.__dict__['__auto_create'] = auto_create
        self.__dict__['__empty_string'] = empty_string
        
        self.update(d)

    def __str__(self):
        if len(self) or self.__dict__['__empty_string'] is None:
            return super(ValueBag, self).__str__()

        return self.__dict__['__empty_string']

    def __unicode__(self):
        return str(self)
        
    def __setattr__(self, name, value):
        if name.startswith('__'):
            self.__dict__[name] = value
        else:
            self[name] = value
                        
    def __setitem__(self, name, value):
        if '.' in name:
            names = name.split('.')
            s = self
            for name in names[:-1]:
                s = s[name]
            name = names[-1]
        else:
            s = self

        if name == name.upper():
            if isinstance(value, (str, unicode)):
                value = os.path.expanduser(value)
                value = os.path.expandvars(value)
                
        if isinstance(value, ValueBag):
            #value.__dict__['__parent'] = self
            pass
        elif isinstance(value, dict):
            value = ValueBag(value)

        super(ValueBag, s).__setitem__(name, value)
        
    def __getattr__(self, name):
        return self[name]
    
    def __getitem__(self, name):
        if '.' in name:
            s = self
            for name in name.split('.'):
                s = s[name]
            return s


        if self.has_key(name):
            return self.get(name)
        
        if not name.startswith('__') and self.__dict__['__auto_create']:
            setattr(self, name, {})
        return super(ValueBag, self).__getitem__(name)
    
    def __copy__(self):
        return ValueBag(super(ValueBag, self).copy())
    
    def __deepcopy__(self, memo = None):
        return ValueBag(copy.deepcopy(dict(self), memo))
        
    def update(self, E, **F):
        for k in F:
            self[k] = F[k]
            
        if hasattr(E, 'keys'):
            for k in E:
                self[k] = E[k]
        else:
            for (k, v) in E:
                self[k] = v

class _JSONEncoder(json.encoder.JSONEncoder):
    def default(self, o):
        return str(o)
    
def dumps(value, indent = 4):
    return json.dumps(value, indent = indent, cls = _JSONEncoder)

def dump(value, fp, indent = 4):
    fp.write(dumps(value, indent = indent))

def loads(s):
    return ValueBag(json.loads(s))

def load(fp):
    return ValueBag(json.load(fp))
    
if __name__ == '__main__':
    import unittest
    import program
    
    class ValueBagTest(unittest.TestCase):
        def setUp(self):
            pass
        
        def tearDown(self):
            pass
        
        def test_init(self):
            obj = ValueBag({'a':{'b':{'c':1, 'd':2}}})
            self.assertTrue(isinstance(obj.a, ValueBag))
            self.assertTrue(isinstance(obj.a.b, ValueBag))
            self.assertTrue(isinstance(obj.a.b.c, int))
            #self.assertEqual(obj.a.b.root(), obj)
        
        def test_setattr(self):
            obj = ValueBag()
            obj.abc = 'abc'
            obj.ABC = '~/abc'
            obj.__abc = 'abc'
            self.assertEqual('abc', obj.abc)
            self.assertNotEquals('~/abc', obj.ABC)
        
        def test_getattr(self):
            obj = ValueBag()
            obj.newitem2
            self.assertTrue(isinstance(obj.newitem, ValueBag))
            self.assertEqual(2, len(obj))
            
    
    program.unittest()
        
