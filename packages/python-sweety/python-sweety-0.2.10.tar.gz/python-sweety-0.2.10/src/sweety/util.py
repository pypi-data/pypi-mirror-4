#!/usr/bin/env python
'''
sweety.util

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import contextlib
import datetime
import getpass
import os
import random
import shutil
import sys
import fcntl
import uuid

from conf import settings

def get_tmpfile(basename = '', tmpdir = settings.TMP_DIR):
    if not basename:
        basename = os.environ.get('INV_PROGRAM', '') or sys.argv[0] 
    return os.path.join(tmpdir, '%s.user=%s.pid=%d.gid=%d.%s.tmp' % (
            basename, getpass.getuser(), os.getpid(), os.getgid(),
            uuid.uuid4()))
    
def touch(name, makedirs = True, mode = 0777):
    if makedirs:
        dname = os.path.dirname(name)
        try:
            os.makedirs(dname, mode)
        except:
            pass
    with open(name, 'a'):
        os.utime(name, None)
        
def createdirs(dirname, mode = 0777):
    try:
        os.makedirs(dirname, mode)
    except:
        pass

class TemporaryFile(file):
    def __init__(self, name = ''):
        if not name:
            name = get_tmpfile(name)
            
        super(TemporaryFile, self).__init__(name, mode = 'w')
        
    def close(self):
        try:
            return file.close(self)
        finally:
            try:
                os.remove(self.name)
            except:
                pass
        
    #def __del__(self):
    #    self.close()
        
        
class SafeWriter(file):
    def __init__(self, name):
        self.target = name
        self.moved = False
        super(SafeWriter, self).__init__(get_tmpfile(os.path.basename(name)), 'w')
                
    def close(self):
        super(SafeWriter, self).close()
        
        if not self.moved:
            try:
                os.makedirs(os.path.dirname(self.target))
            except:
                pass
            os.rename(self.name, self.target)
            self.moved = True
            


class Shelter(object):
    '''
    A Shelter provides process a safe environment for temporary file storage.
    '''
    def __init__(self, name):
        '''
        Initializes a new Shelter object.
        '''
        self.name = name
        self.path = os.path.join(settings.TMP_DIR, '%s.%d.%s_%s' % (name, os.getpid(), self.get_timestamp(), str(random.random()).split('.')[1]))

        os.makedirs(self.path)


    def __del__(self):
        '''
        Destructor
        '''
        self.depose()


    def get_timestamp(self):
        '''
        get_timestamp(self) -> string
        
        Gets current time stamp.
        
        @return: string of time stamp.
        '''
        n = datetime.datetime.now()

        return '%s.%s' % (n.strftime('%Y-%m-%d_%T'), n.microsecond)


    def get_unique_filename(self, filename):
        '''
        get_unique_filename(self, filename) -> string
        
        Gets a unique filename inside the sheltered environment.
        
        @param filename: the base part of the filename.
        @return: a string of full filename.
        '''
        return os.path.join(self.path, '%s.%s' % (filename, self.get_timestamp()))


    def get_filename(self, filename):
        '''
        get_filename(self, filename) -> string
        
        Gets a filename inside the sheltered environment.
        
        @param filename: the base part of the filename.
        @return: a string of full filename.
        '''
        return os.path.join(self.path, filename)


    def depose(self):
        '''
        depose(self) -> None
        
        Deposes the sheltered environment.
        '''
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)


if __name__ == '__main__':
    import unittest
    
    import program
    
    class SafeWriterTest(unittest.TestCase):
        def setUp(self):
            self.path = '/tmp/safewritertest.file'
        
        def tearDown(self):
            try:
                os.remove(self.path)
            except:
                pass
            
        def test_writer(self):
            fp = SafeWriter(self.path)
            fp.write('abc')
            fp.close()
            self.assertTrue(os.path.exists(self.path))
        
    
    program.unittest()
