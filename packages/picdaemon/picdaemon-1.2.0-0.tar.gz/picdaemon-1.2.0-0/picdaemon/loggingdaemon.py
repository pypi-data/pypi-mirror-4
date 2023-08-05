#!/usr/bin/env python

import os
import sys
import logging
import daemoncontext

class FileLikeLogger(object):
    "wraps a logging.Logger into a file like object"
    
    def __init__(self, logger):
        self.logger = logger
    
    def write(self, str):
        str = str.rstrip() #get rid of all tailing newlines and white space
        if str: #don't log empty lines
            for line in str.split('\n'):
                self.logger.critical(line) #critical to log at any logLevel
    
    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()
    
    def close(self):
        for handler in self.logger.handlers:
            handler.close()

def openFilesFromLoggers(loggers):
    "returns the open files used by file-based handlers of the specified loggers"
    openFiles = []
    for logger in loggers:
        for handler in logger.handlers:
            if hasattr(handler, 'stream') and \
               hasattr(handler.stream, 'fileno'):
                openFiles.append(handler.stream)
    return openFiles
      
class LoggingDaemonContext(daemoncontext.DaemonContext):
    
    def _addLoggerFiles(self):
        "adds all files related to loggers_preserve to files_preserve"
        for logger in [self.stdout_logger, self.stderr_logger]:
            if logger:
                self.loggers_preserve.append(logger)
        loggerFiles = openFilesFromLoggers(self.loggers_preserve)
        self.files_preserve.extend(loggerFiles)
    
    def __init__(
        self,
        chroot_directory=None,
        working_directory='/',
        umask=0,
        uid=None,
        gid=None,
        prevent_core=True,
        detach_process=None,
        files_preserve=[],   # changed default
        loggers_preserve=[], # new
        pidfile=None,
        stdout_logger = None,  # new
        stderr_logger = None,  # new
        #stdin,   omitted!
        #stdout,  omitted!
        #sterr,   omitted!
        signal_map=None,
        ):

        self.stdout_logger = stdout_logger
        self.stderr_logger = stderr_logger
        self.loggers_preserve = loggers_preserve

        devnull_in = open(os.devnull, 'r+')
        devnull_out = open(os.devnull, 'w+')
        files_preserve.extend([devnull_in, devnull_out])

        daemoncontext.DaemonContext.__init__(self,
            chroot_directory = chroot_directory,
            working_directory = working_directory,
            umask = umask,
            uid = uid,
            gid = gid,
            prevent_core = prevent_core,
            detach_process = detach_process,
            files_preserve = files_preserve, 
            pidfile = pidfile,
            stdin = devnull_in,
            stdout = devnull_out,
            stderr = devnull_out,
            signal_map = signal_map) 

    def open(self): 
        self._addLoggerFiles() 
        daemoncontext.DaemonContext.open(self)
        if self.stdout_logger:
            fileLikeObj = FileLikeLogger(self.stdout_logger)
            sys.stdout = fileLikeObj
        if self.stderr_logger:
            fileLikeObj = FileLikeLogger(self.stderr_logger)
            sys.stderr = fileLikeObj
