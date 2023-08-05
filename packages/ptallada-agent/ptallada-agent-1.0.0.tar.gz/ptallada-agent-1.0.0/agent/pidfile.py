# -*- coding: utf-8 -*-

import errno
import os
import signal

import daemon.pidlockfile

class AgentPIDLockFile(daemon.pidlockfile.PIDLockFile):
    """
    Lockfile with default timeout, implemented as a Unix PID file.
    
    This uses the ``PIDLockFile`` implementation, with the
    following changes:
    
    * The `acquire_timeout` parameter to the initialiser will be
      used as the default `timeout` parameter for the `acquire`
      method. Defaults to 0 to avoid blocking.
    """
    
    def __init__(self, path, acquire_timeout=0, *args, **kwargs):
        self.acquire_timeout = acquire_timeout
        super(AgentPIDLockFile, self).__init__(path, *args, **kwargs)
    
    def acquire(self, timeout=None, *args, **kwargs):
        self._acquire(*args, **kwargs)
        self._write_pid()
        
    def _acquire(self, timeout=None, *args, **kwargs):
        if timeout is None:
            timeout = self.acquire_timeout
        # Call acquire from LinkFileLock class
        super(daemon.pidlockfile.PIDLockFile, self).acquire(timeout, *args, **kwargs)
    
    def _write_pid(self):
        try:
            daemon.pidlockfile.write_pid_to_pidfile(self.path)
        except OSError, exc:
            error = LockFailed("%(exc)s" % vars())
            raise error
        
def is_pidfile_stale(pidfile):
    """
    Determine whether a PID file is stale.
    
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