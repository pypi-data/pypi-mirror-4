# -*- coding: utf-8 -*-

import os
import signal
import daemoncontext
import atexit
import errno

from loggingdaemon import LoggingDaemonContext
from pidlockfile import TimeoutPIDLockFile

def is_pidfile_stale(pidfile):
    """ Determine whether a PID file is stale.
        
        Return ``True`` (“stale”) if the contents of the PID file are
        valid but do not match the PID of a currently-running process;
        otherwise return ``False``.
        
        """
    result = False
    
    pidfile_pid = pidfile.read_pid()
    if pidfile_pid is not None:
        try:
            os.kill(pidfile_pid, signal.SIG_DFL)
        except OSError, exc:
            if exc.errno == errno.ESRCH:
                # The specified PID does not exist
                result = True
    
    return result

class Daemon(LoggingDaemonContext):
    def __init__(
        self,
        stdout_logger = None,
        stderr_logger = None,
        pidfile_path  = None,
        loggers_preserve = [],
        foreground = False,
    ):
        
        self._terminating = False
        self._foreground = foreground
        
        # Create non blocking pidfile object
        self._pidfile = None
        if pidfile_path:
            self._pidfile = TimeoutPIDLockFile(pidfile_path, acquire_timeout=0)
        
        # Build default signal map
        self._signal_map = {
            signal.SIGTERM : self._terminate,
            signal.SIGHUP  : self._terminate,
            signal.SIGINT  : self._terminate,
        }
        
        super(Daemon, self).__init__(
            loggers_preserve = loggers_preserve,
            pidfile          = self._pidfile,
            stdout_logger    = stdout_logger,
            stderr_logger    = stderr_logger,
            signal_map       = self._signal_map,
        )
    
    def terminate(self):
        pass
    
    def _terminate(self, *args, **kwargs):
        self.terminate()
        self._terminating = True
    
    def terminating(self):
        return self._terminating
    
    def process(self, *args, **kwargs):
        pass
    
    def start(self, *args, **kwargs):
        if self._pidfile and is_pidfile_stale(self._pidfile):
            print "WARNING: Stale lock file detected. Removing it..."
            self._pidfile.break_lock()
        if not self._foreground:
            # Launch in daemonized background mode
            self.open()
            try:
                self.process(*args, **kwargs)
            finally:
                self.close()
        else:
            # Launch in foreground mode
            self._pidfile.acquire()
            try:
                daemoncontext.set_signal_handlers(self._signal_map)
                self.process(*args, **kwargs)
            finally:
                self._pidfile.release()
