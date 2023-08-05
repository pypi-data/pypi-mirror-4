# -*- coding: utf-8 -*-

import logging
import pidfile
import signal
import sys

from logging_context import LoggingDaemonContext

log = logging.getLogger("agent")

class AgentExit(Exception):
    pass

class Agent(LoggingDaemonContext):
    
    class CriticalSectionContext(object):
        def __init__(self, callback):
            # Number of critical sections entered
            self._critical_sections = 0
            # Method to call when we exit the last critical section
            self._callback = callback
        
        def __enter__(self):
            self._critical_sections += 1
            log.debug("Entered critical section. Depth = %d." % self._critical_sections)
        
        def __exit__(self, *args, **kwargs):
            self._critical_sections -= 1
            log.debug("Exitted critical section. Depth = %d." % self._critical_sections)
            if self._critical_sections < 0:
                raise Exception("You are already out of all critical sections.")
            elif self._critical_sections == 0:
                self._callback()
        
        def locked(self):
            return self._critical_sections > 0
    
    def __init__(
        self,
        stdout_logger = None,
        stderr_logger = None,
        pidfile_path  = None,
        loggers_preserve = [],
        detach_process = True,
        **kwargs
    ):
        # Reentrant Lock to count the number of critical sections
        self.critical_section = Agent.CriticalSectionContext(self._try_exit)
        # Flag to indicate whether we have been signaled to exit
        self._terminating = False
        
        # Create non blocking pidfile object
        self._pidfile = None
        if pidfile_path:
            self._pidfile = pidfile.AgentPIDLockFile(pidfile_path)
        
        # Build default signal map
        self._signal_map = {
            signal.SIGTERM : self._signal_handler,
            signal.SIGHUP  : self._signal_handler,
            signal.SIGINT  : self._signal_handler,
        }
        
        super(Agent, self).__init__(
            loggers_preserve = loggers_preserve,
            pidfile          = self._pidfile,
            stdout_logger    = stdout_logger,
            stderr_logger    = stderr_logger,
            signal_map       = self._signal_map,
            detach_process   = detach_process,
            **kwargs
        )
    
    def _signal_handler(self, *args, **kwargs):
        log.debug("We have been signaled to terminate.")
        self._terminating = True
        self.terminate()
        self._try_exit()
    
    def terminate(self):
        pass
    
    def _try_exit(self):
        if self.terminating() and not self.critical_section.locked():
            log.debug("It is safe to exit. Raising AgentExit exception ;)")
            raise AgentExit()
    
    def terminating(self):
        return self._terminating
    
    def process(self, *args, **kwargs):
        pass
    
    def start(self, *args, **kwargs):
        if self._pidfile and pidfile.is_pidfile_stale(self._pidfile):
            sys.stderr.write("WARNING: Stale lock file detected. Removing it.\n")
            self._pidfile.break_lock()
        # Start agent code
        self.open()
        try:
            self.process(*args, **kwargs)
        except AgentExit:
            log.debug("Caught AgentExit exception. Agent is exitting.")
        finally:
            log.debug("Closing Agent context...")
            self.close()

if __name__ == '__main__':
    import logging
    import optparse
    import time
    import sys
    
    def opt_parser():
        parser = optparse.OptionParser(usage="Usage: %prog [options]")
        parser.add_option("-d", "--daemonize", dest="daemonize",
                          action="store_true", default=False,
                          help="Run the process in background [default: %default].")
        parser.add_option("-p", "--pidfile", dest="pidfile",
                          default="/var/run/agent.pid",
                          help="Store the process PID in this file [default: %default].")
        
        (options, args) = parser.parse_args()
        
        return (options, args)
    
    # Parse command line arguments
    (options, args) = opt_parser()
    
    # Setup logging
    #logging.basicConfig(level = logging.DEBUG, filename="agent.log")
    logging.basicConfig(level = logging.DEBUG)
    log = logging.getLogger()
    
    import sys
    
    class TestAgent(Agent):
        def terminate(self):
            log.info("We've been asked to terminate.")
        
        def process(self, limit):
            for i in xrange(1, limit):
                log.debug("Interruptible Iteration %s" %i)
                time.sleep(2)
            
            with self.critical_section:
                for i in xrange(1, limit):
                    log.debug("Uninterruptible Iteration %s" %i)
                    time.sleep(2)
            
            for i in xrange(1, limit):
                log.debug("Interruptible Iteration %s" %i)
                time.sleep(2)

    
    agent=TestAgent(
        detach_process = options.daemonize,
        pidfile_path = options.pidfile,
        loggers_preserve = [log],
        #files_preserve = [sys.stdout, sys.stderr],
        #stdout_logger = log,
        #stderr_logger = log,
    )
    log.debug("before start")
    agent.start(5)
    log.debug("after start")
