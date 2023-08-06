#!/usr/bin/env python
'''
sweety.log

@author: Yunzhi Zhou (Chris Chou)
'''

import cPickle as pickle 
from datetime import datetime
import logging
import logging.handlers
#import multiprocessing.util
import os
import socket
import SocketServer
import signal
import struct
import sys

import setproctitle

from conf import settings

__all__ = ['get_logger']

_start_time = datetime.now()

_logfile_formatter = logging.Formatter(
                                    '%(asctime)s - %(process)d:%(thread)d:%(name)-8s %(levelname)08s: [%(filename)s:%(lineno)d] - %(message)s'
                                    )
_console_formatter = logging.Formatter(
                                    '%(asctime)s - %(levelname)-8s: %(message)s [%(filename)s:%(lineno)d]'
                                    )



class UnixSocketHandler(logging.handlers.SocketHandler):
    
    def __init__(self, name):
        super(UnixSocketHandler, self).__init__('', 0)
        self.name = name
        
    def makeSocket(self, timeout = 1):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'):
            s.settimeout(timeout)
        s.connect(self.name)
        return s
       
    #def emit(self, record):
    #    return super(UnixSocketHandler, self).emit(record)
        
class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        #if self.server.logname is not None:
        #    name = self.server.logname
        #else:
        #    name = record.name
        logger = get_logger(record.name)
        # logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record);
        if record.name == '_exit':
            self.server.abort = True

class LogRecordSocketReceiver(SocketServer.ThreadingUnixStreamServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1

    def __init__(self, address, handler=LogRecordStreamHandler):
        SocketServer.ThreadingUnixStreamServer.__init__(self, address, handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            try:
                rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
                if rd:
                    self.handle_request()
                abort = self.abort
            except KeyboardInterrupt:
                abort = True
            #print 'abort'
            
    def server_close(self):
        SocketServer.ThreadingUnixStreamServer.server_close(self)
        try:
            os.remove(self.server_address)
        except:
            pass
            

        
def multiproc_logger_main(startcond):
    sys.argv[0] = '%s@log' % sys.argv[0]
    setproctitle.setproctitle('%s [logging]' % ' '.join(sys.argv))
    
    setup_root_logger(remote = False)
    
    startcond.acquire()
    server = LogRecordSocketReceiver(os.environ[settings.ENV_LOGGER_SOCKFILE])
    startcond.notify_all()
    startcond.release()
    #signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        server.serve_until_stopped()
    except:
        pass
    finally:
        server.server_close()


def setup_logger(logger, remote = False):
    #logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        logger.handlers = []
        
    if remote:
        handler = UnixSocketHandler(os.environ[settings.ENV_LOGGER_SOCKFILE])
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    else:    
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(_console_formatter)
        logger.addHandler(console)
    
        if os.environ.has_key(settings.ENV_VERBOSE) and os.environ[settings.ENV_VERBOSE]:
            console.setLevel(logging.INFO)
        else:
            console.setLevel(logging.WARNING)
    
    
        if os.environ.has_key(settings.ENV_LOG_FILENAME):
            fn = os.environ[settings.ENV_LOG_FILENAME]
            fdir = os.path.dirname(fn)
            fdir = os.path.join(fdir, _start_time.strftime('%Y-%m-%d'))
            if not os.path.exists(fdir):
                os.makedirs(fdir)
            fn = '%s/%s.%s.%d' % (
                    fdir,
                    os.path.basename(fn),
                    _start_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    os.getpid()
                    )
            logfile = logging.handlers.TimedRotatingFileHandler(fn, 'h')
            logfile.setFormatter(_logfile_formatter)
            logger.addHandler(logfile)
            logfile.setLevel(logging.DEBUG)

def setup_root_logger(remote = False):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    setup_logger(root, remote)

#def get_remote_logger(name_or_self):
#    if not isinstance(name_or_self, (str, unicode)):
#        name_or_self = name_or_self.__class__.__name__
#    logger = logging.getLogger(name_or_self)
#    handler = logging.handlers.SocketHandler('localhost', 
#                                             logging.handlers.DEFAULT_TCP_LOGGING_PORT)
#    #handler = UnixSocketHandler(os.environ[settings.ENV_LOGGER_SOCKFILE])
#    handler.setLevel(logging.DEBUG)
#    logger.addHandler(handler)
#    
#    return logger
#
#
#def get_local_logger(name_or_self):
#    '''
#    get_logger(name_or_self) -> Logger
#    
#    Gets logger with specified name.
#    
#    @param name: the logger name or self.
#    @return: the logger object.
#    '''
#    
#    #logging.handlers.SocketHandler()
#
#    # lockname = 'invpanel.logger.%s.lock' % _start_time.strftime('%Y-%m-%d')
#    # lock = util.FileLock(lockname)
#    # lock.lock()
#
#    if not isinstance(name_or_self, (str, unicode)):
#        name_or_self = name_or_self.__class__.__name__
#
#    logger = logging.getLogger(name_or_self)
#    #logger = multiprocessing.get_logger()
#    logger.setLevel(logging.DEBUG)
#
#    #if True:
#    if not logger.handlers:
#        setup_logger(logger)
#        
#    return logger

def get_logger(name_or_self):
    if not isinstance(name_or_self, (str, unicode)):
        name_or_self = name_or_self.__class__.__name__

    logger = logging.getLogger(name_or_self)
    logger.setLevel(logging.DEBUG)
    
    #if not logger.handlers:
    #    if os.environ.has_key(settings.ENV_LOGGER_PID) and os.environ[settings.ENV_LOGGER_PID] == str(os.getpid()):
    #        setup_logger(logger, remote = False)
    #    else:
    #        setup_logger(logger, remote = True)
            
    
    return logger

#logging.root = get_logger('root')
