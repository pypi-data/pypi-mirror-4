# -*- coding: utf-8 -*-

import daemon
from daemon.daemon import *

class ExclussiveContext(daemon.DaemonContext):
    def open(self):
        """ 
        Become a daemon process.
        :Return: ``None``
        
        Open the daemon context, turning the current program into a daemon
        process. This performs the following steps:
        
        * If this instance's `is_open` property is true, return
          immediately. This makes it safe to call `open` multiple times on
          an instance.
        
        * If the `prevent_core` attribute is true, set the resource limits
          for the process to prevent any core dump from the process.
        
        * If the `chroot_directory` attribute is not ``None``, set the
          effective root directory of the process to that directory (via
          `os.chroot`).
        
          This allows running the daemon process inside a “chroot gaol”
          as a means of limiting the system's exposure to rogue behaviour
          by the process. Note that the specified directory needs to
          already be set up for this purpose.
        
        * Set the process UID and GID to the `uid` and `gid` attribute
          values.
        
        * Close all open file descriptors. This excludes those listed in
          the `files_preserve` attribute, and those that correspond to the
          `stdin`, `stdout`, or `stderr` attributes.
        
        * Change current working directory to the path specified by the
          `working_directory` attribute.
        
        * Reset the file access creation mask to the value specified by
          the `umask` attribute.
        
        * If the `detach_process` option is true, detach the current
          process into its own process group, and disassociate from any
          controlling terminal.
        
        * Set signal handlers as specified by the `signal_map` attribute.
        
        * If any of the attributes `stdin`, `stdout`, `stderr` are not
          ``None``, bind the system streams `sys.stdin`, `sys.stdout`,
          and/or `sys.stderr` to the files represented by the
          corresponding attributes. Where the attribute has a file
          descriptor, the descriptor is duplicated (instead of re-binding
          the name).
        
        * If the `pidfile` attribute is not ``None``, enter its context
          manager.
        
        * Mark this instance as open (for the purpose of future `open` and
          `close` calls).
        
        * Register the `close` method to be called during Python's exit
          processing.
        
        When the function returns, the running program is a daemon
        process.
        """
        
        if self.is_open:
            return
        
        if self.detach_process:
            if self.chroot_directory is not None:
                change_root_directory(self.chroot_directory)
            
            if self.prevent_core:
                prevent_core_dump()
            
            change_file_creation_mask(self.umask)
            change_working_directory(self.working_directory)
            change_process_owner(self.uid, self.gid)
            
            # Lock the PID file, but do not write the PID yet
        if self.pidfile is not None:
            self.pidfile._acquire()
        
        if self.detach_process:
            detach_process_context()
        
        # After double fork, write the PID
        if self.pidfile is not None:
            self.pidfile._write_pid()
        
        signal_handler_map = self._make_signal_handler_map()
        set_signal_handlers(signal_handler_map)
        
        if self.detach_process:
            exclude_fds = self._get_exclude_file_descriptors()
            close_all_open_files(exclude=exclude_fds)
            
            redirect_stream(sys.stdin, self.stdin)
            redirect_stream(sys.stdout, self.stdout)
            redirect_stream(sys.stderr, self.stderr)
            
        self._is_open = True
        
        register_atexit_function(self.close)
