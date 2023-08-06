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

def realvalue(k, v):
    if k == k.upper() and isinstance(v, (str, unicode)):
        v = os.path.expanduser(v)
        v = os.path.expandvars(v)
    
    return v

class xdict(dict):
    def __init__(self, d = {}, **kwargs):
        dict.__init__(self)
        
        self.update(d, **kwargs)
        
    def __str__(self):
        return dict.__str__(self.toDict()) if self else ''
        
    def __unicode__(self):
        return self.__str__()
    
    #def __repr__(self):
    #    return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))
        
    def __getitem__(self, k):
        if isinstance(k, (str, unicode)) and '.' in k:
            k, rest = k.split('.', 1)
            return self[k][rest]
        
        try:
            return dict.__getitem__(self, k)
        except KeyError:
            v = self[k] = type(self)()
            return v
        
    def __getattr__(self, k):
        try:
            return object.__getattribute__(self, k)
        except AttributeError, e:
            if k.startswith('__'):
                raise e
            try:
                return self[k]
            except KeyError:
                raise e
        
    def get(self, k, default = None):
        v = self[k]
        return v if v else default
        
    def __setitem__(self, k, v):
        if isinstance(k, (str, unicode)) and '.' in k:
            k, rest = k.split('.', 1)
            self[k][rest] = v
        else:
            if isinstance(v, dict) and not isinstance(v, xdict):
                v = xdict(v)
            else:
                v = realvalue(k, v)
            dict.__setitem__(self, k, v)
        
    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            self[k] = v
        else:
            object.__setattr__(self, k, realvalue(k, v))
 
    def update(self, E, **F):
        for k in F:
            self[k] = F[k]
            
        if hasattr(E, 'keys'):
            for k in E:
                self[k] = E[k]
        else:
            for (k, v) in E:
                self[k] = v

    def __copy__(self):
        return xdict(super(xdict, self).copy())
    
    def __deepcopy__(self, memo = None):
        return xdict(copy.deepcopy(super(xdict, self), memo))
    
    def __contains__(self, k):
        try:
            return self.has_key(k) or hasattr(self, k)
        except:
            return False
    
    def has_key(self, k):
        if isinstance(k, (str, unicode)) and '.' in k:
            k, rest = k.split('.', 1)
            child = self[k]
            if not isinstance(child, dict):
                return False
            return child.has_key(rest)
            
        return dict.has_key(self, k)
    
    def __delattr__(self, k):
        if isinstance(k, (str, unicode)) and '.' in k:
            k, rest = k.split('.', 1)
            child = self[k]
            xdict.__delattr__(child, rest)
        else:
            try:
                object.__getattribute__(self, k)
            except AttributeError:
                try:
                    del self[k]
                except KeyError:
                    raise AttributeError(k)
            else:
                object.__delattr__(self, k)
                
    def toDict(self):
        return to_dict(self)
    
    @staticmethod
    def fromDict(d):
        return xdict(d)
 
def to_dict(x):
    if isinstance(x, xdict):
        return dict((k, to_dict(v)) for k, v in x.items())
    elif isinstance(x, (tuple, list)):
        return type(x)(to_dict(v) for v in x)
    else:
        return x
    
try:
    try:
        import json
    except ImportError:
        import simplejson as json
        
    class _JSONEncoder(json.encoder.JSONEncoder):
        def default(self, o):
            return str(o)
                    
    def toJSON(self, **kwargs):
        return json.dumps(self, cls = _JSONEncoder, **kwargs)

    def fromJSON(s, **kwargs):
        return xdict(json.loads(s))
    
    xdict.toJSON = toJSON
    xdict.fromJSON = staticmethod(fromJSON)
    
    
except ImportError:
    pass

# class ValueBag(dict):
#     def __init__(self, d = {}):
#         super(ValueBag, self).__init__()
#         
#         self.update(d)
# 
#     def __setattr__(self, name, value):
#         if name.startswith('__'):
#             self.__dict__[name] = value
#         else:
#             self[name] = value
#                         
#     def __setitem__(self, name, value):
#         if '.' in name:
#             names = name.split('.')
#             s = self
#             for name in names[:-1]:
#                 s = s[name]
#             name = names[-1]
#         else:
#             s = self
# 
#         if name == name.upper():
#             if isinstance(value, (str, unicode)):
#                 value = os.path.expanduser(value)
#                 value = os.path.expandvars(value)
#                 
#         if isinstance(value, dict):
#             value = ValueBag(value)
# 
#         super(ValueBag, s).__setitem__(name, value)
#         
#     def __getattr__(self, name):
#         return self[name]
#     
#     def __getitem__(self, name):
#         if '.' in name:
#             s = self
#             for name in name.split('.'):
#                 s = s[name]
#             return s
# 
# 
#         if self.has_key(name):
#             return super(ValueBag, self).__getitem__(name)
#         
#         if not name.startswith('__'):
#             setattr(self, name, {})
#         return super(ValueBag, self).__getitem__(name)
#     
#     def __copy__(self):
#         return ValueBag(super(ValueBag, self).copy())
#     
#     def __deepcopy__(self, memo = None):
#         return ValueBag(copy.deepcopy(dict(self), memo))
#         
#     def update(self, E, **F):
#         for k in F:
#             self[k] = F[k]
#             
#         if hasattr(E, 'keys'):
#             for k in E:
#                 self[k] = E[k]
#         else:
#             for (k, v) in E:
#                 self[k] = v
# 
#     def get(self, key, default = None):
#         ret = self[key]
#         return ret if ret else default
# 
#     def has_key(self, key):
#         if '.' in key:
#             keys = key.split('.')
#             s = self
#             for key in keys:
#                 if not isinstance(s, dict) or not super(ValueBag, s).has_key(key):
#                     return False
#                 s = s[key]
#             return True
# 
#         return super(ValueBag, self).has_key(key)

ValueBag = xdict

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
            
            obj.dict = {'a':1, 'rec': {'z': 2}}
            self.assertEqual(obj.dict.a, 1)
            self.assertEqual(obj.dict.rec.z, 2)
            
        
        def test_getattr(self):
            obj = ValueBag()
            obj.newitem2
            self.assertTrue(isinstance(obj.newitem, ValueBag))
            self.assertEqual(2, len(obj))

        def test_recursive(self):
            obj = ValueBag()
            obj.a.b.c = 1
            self.assertEqual(obj.a.b.c, 1)
            self.assertEqual(obj['a.b.c'], 1)
            self.assertEqual(obj.get('a.b.c'), 1)

            obj['foo.bar'] = 2
            self.assertEqual(obj.foo.bar, 2)
            self.assertEqual(obj['foo.bar'], 2)
            self.assertEqual(obj.get('foo.bar'), 2)
            
        def test_has_key(self):
            obj = ValueBag()
            obj.a.b.c = 1

            self.assertTrue(obj.has_key('a'))
            self.assertTrue(obj.has_key('a.b'))
            self.assertTrue(obj.has_key('a.b.c'))
            self.assertFalse(obj.has_key('d'))
            self.assertFalse(obj.has_key('d.d'))
            
    unittest.main()
        
