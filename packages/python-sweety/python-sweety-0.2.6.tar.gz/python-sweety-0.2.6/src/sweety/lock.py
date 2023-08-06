#!/usr/bin/env python
'''
sweety.lock

@author: Yunzhi Zhou (Chris Chou)
'''

import contextlib
import errno
import fcntl

__all__ = ['FileReadLock', 'readlock', 'FileWriteLock', 'writelock']

class FileReadLock(object):
    def __init__(self, fp, lock = False):
        self.fp = fp
        self.locked = False
        if lock:
            self.lock()
        
    def __del__(self):
        self.unlock()
        
    def lock(self):
        fcntl.lockf(self.fp, fcntl.LOCK_SH)
        self.locked = True

    def trylock(self):
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_SH | fcntl.LOCK_NB)
            self.locked = True
            return True
        except IOError, e:
            if e.errno == errno.EAGAIN:
                return False
            
            raise e
      
    def unlock(self):
        fcntl.lockf(self.fp, fcntl.LOCK_UN)
        self.locked = False

@contextlib.contextmanager
def readlock(fp):
    l = FileReadLock(fp)
    try:
        l.lock()
        yield fp
    finally:
        l.unlock()
    
class FileWriteLock(object):
    def __init__(self, fp, lock = False):
        self.fp = fp
        self.locked = False
        if lock:
            self.lock()
        
    def __del__(self):
        self.unlock()
        
    def lock(self):
        fcntl.lockf(self.fp, fcntl.LOCK_EX)
        self.locked = True
        
    def trylock(self):
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.locked = True
            return True
        except IOError, e:
            if e.errno == errno.EAGAIN:
                return False
            
            raise e
    
    def unlock(self):
        fcntl.lockf(self.fp, fcntl.LOCK_UN)
        self.locked = False
    
@contextlib.contextmanager
def writelock(fp):
    l = FileWriteLock(fp)
    try:
        l.lock()
        yield fp
    finally:
        l.unlock()

if __name__ == '__main__':
    import unittest
    
    import program
    import util
    
    class FileReadLockTest(unittest.TestCase):
        def setUp(self):
            self.fp = open('/etc/csh.cshrc')
        
        def tearDown(self):
            self.fp = None
        
        def test_readlock(self):
            lock = FileReadLock(self.fp)
            lock.lock()
            self.assertTrue(lock.locked)
            lock.unlock()
        
    class FileWriteLockTest(unittest.TestCase):
        def setUp(self):
            self.fp = util.TemporaryFile()
        
        def tearDown(self):
            self.fp = None
        
        def test_writelock(self):
            lock = FileWriteLock(self.fp)
            lock.lock()
            self.assertTrue(lock.locked)
            lock.unlock()

    program.unittest()
