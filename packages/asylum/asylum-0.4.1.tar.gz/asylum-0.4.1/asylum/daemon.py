#!/usr/bin/env python
"""daemon: Daemonization libary, Takes care of the tricky details of turning your 
program into a daemon

Supports Context managers as well as providing an object you call 
methods on. Also provides its own locking mechanism that can be 
overridden when using the object aproch

To use try the following code:

from asylum import daemon
from time import sleep

def sleeper():
    sleep(5)
    print("done")

with daemon.Daemonize(pidfile="./pid", daemonize=False, stdout=sys.stdout,
        stderr=sys.stderr, stdin=sys.stdin) as d:
    sleeper()

alternativly:

from asylum import daemon
from time import sleep

def sleeper():
    sleep(5)

d = daemon.Daemonize(pidfile="./pid", daemonize=False, stdout=sys.stdout,
        stderr=sys.stderr, stdin=sys.stdin)
d.open()
sleeper()
d.close()
print("done")
"""

import asylum.syscall
import asylum.conf
import resource
import logging
import atexit
import signal
import sys
import pwd
import grp
import os

class Daemonize(object):
    """Daemon object for daemonizing a process under unix

    see Module doc string for usage"""
    def __init__(self, user=os.getuid(), group=os.getgid(), daemonize=True, 
                chroot=None, working_dir="/", pidfile=None, umask=0o177, 
                stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, 
                signal_map={}, namespaces=[], profile=None):
        """Paramaeters:
        user:          The username or uid to change to before daemonizing
        group:         The groupname or gid to change to before daemonizing
        daemonize:     if the process should fork or not
        chroot:        The directory to chroot to (use in conjunction with user 
                       and group options for security)
        working_dir:   The directory to change (chdir) to after chrooting
        pidfile:       The location of the pid file (string, filepath)
        umask:         The umask to create files with 
        stdin:         The file to use as stdin after forking/chrooting
        stdout:        The file to use as stdout after forking/chrooting
        stderr:        The file to use as stderr after forking/chrooting
        namespaces:    A list of namespaces to unshare, posible values in the list
                       are:
                         UTS:    Unshare te hostname allowing it to be changed
                         UID:    Unshare the UID namespace allowing private (to the parent) users
                         PID:    Unshare the PID namespace preventing you from seeing 
                                 non namespace processes, the current process becomes PID 1
                         NET:    Unshare the network interfaces giving the process its own
                                 view of the network and routing
                         MOUNT:  Unshare filesystem mounts allowing a process to mount and
                                 unmount filesystems without affecting the parent
                         IPC:    Unshare the IPC, preventing processes from using Inter-process
                                 communicaiton with processes outside the namespace (eg shared mem
                                 or message queues)
        profile:       If an ini file is passed (as a string, filename or fd) then
                       read this ini file for config information to set up the
                       enviroment to clone() into, eg setting up mounts, preexecing
                       setup scripts for the enviroment
        """
        if type(user) == str:
            self.uid = pwd.getpwnam(user)[2]
        else:
            self.uid = user
        if type(group) == str:
            self.gid = grp.getgrnam(user)[2]
        else:
            self.gid = group

        self.prevent_core = True

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        
        self.files_preserve = []

        self.chroot_directory = chroot
        self.working_directory = working_dir
        self.pidfile = pidfile
        self.umask = umask

        self.detach_process = daemonize

        # Merge signal maps
        self.signal_map = {    signal.SIGTERM: self.terminate,
                            signal.SIGHUP:    self.reload,
                            }
        self.signal_map.update(signal_map)

        self.is_open = False
        self.log = logging.getLogger("asylum.daemon.Daemonize")

    def reload(self, signal_number, stack_frame):
        try:
            self.child.__reload__()
        except AttributeError:
            self.log.info("Deamon has no reload function")

    def open(self):
        """Open the daemon context, turning the current program into a daemon process."""
        # If this instance's is_open property is true, return 
        # immediately. This makes it safe to call open multiple times on 
        # an instance.
        if self.is_open == True:
            return

        # If the prevent_core attribute is true, set the resource limits 
        # for the process to prevent any core dump from the process.
        if self.prevent_core == True:
            resource.setrlimit(resource.RLIMIT_CORE, (0,0))
            self.log.debug("Core files disabled")

        # If the chroot_directory attribute is not None, set the 
        # effective root directory of the process to that directory (via 
        # os.chroot). This allows running the daemon process inside a 
        # "chroot gaol" as a means of limiting the system's exposure to 
        # rogue behaviour by the process. Note that the specified 
        # directory needs to already be set up for this purpose.
        if self.chroot_directory != None:
            self.log.debug("Chrooting to %s", self.chroot_directory)
            try:
                os.chroot(self.chroot_directory)
            except OSError:
                self.log.error("Could not chroot to %s", self.chroot_directory)                
            else:
                self.log.debug("Succsfully chroot'd")

        # Set the process UID and GID to the uid and gid attribute 
        # values.
        try:
            os.setgid(self.gid)
            os.setuid(self.uid)
        except OSError:
            self.log.error("Could not change uid/gid for daemon")

        # Close all open file descriptors. This excludes those listed in 
        # the files_preserve attribute, and those that correspond to the 
        # stdin, stdout, or stderr attributes.
        self.log.debug("Closing aditional file descriptors")

        fds = self.files_preserve[:]
        fd_max = 65536
        fds.append(sys.stdin.fileno())
        fds.append(sys.stdout.fileno())
        fds.append(sys.stderr.fileno())
        for i in range(fd_max):
            if i not in fds:
                try:
                    os.close(i)
                except OSError:
                    pass
        # in truth, fdnum may be nearer to 2mil max ((2^31) -1)
        self.log.debug("Extra file descriptors closed")

        # Reset the file access creation mask to the value specified by 
        # the umask attribute.
        if self.umask != None:
            self.log.debug("Setting Umask to %.4o", self.umask)
            os.umask(self.umask)

        # convert profile to a fd
        if profile:
            if isinstance(profile, str):
                if os.path.isfile(profile):
                    profile = open(profile)
                else:
                    from StringIO import StringIO
                    profile = StringIO(profile)
            elif isinstance(profile, file):
                pass
        config = asylum.conf.get_confs(fds=[profile])
        # override conf file namespace spec if a namespace spec is provided
        namespaces = namespaces or config['container']['namespace']
        flags = asylume.syscall.clone_flags_from_list(namespaces)


        # If the detach_process option is true, detach the current 
        # process into its own process group, and disassociate from any 
        # controlling terminal.
        if self.detach_process == True:
            try:
                pid = os.fork()
                if pid > 0:
                    # we are the parent
                    sys.exit(0)
            except OSError:
                self.log.error("Could not do inital daemonizing fork")
                sys.exit(1)
            # seperate from parent environment
            os.setsid()
            
            try:
                #pid = os.fork()
                pid = asylum.syscall.clone(flags)
                if pid > 0:
                    # we are the parent
                    sys.exit(0)
            except OSError:
                self.log.error("Could not do second daemonizing fork")
                sys.exit(2)
            self.log.debug("All forks complete, process detached from controlling terminal")
                
        # Set signal handlers as specified by the signal_map attribute.
        for sig in self.signal_map:
            signal.signal(sig, self.signal_map[sig])
        self.log.debug("Installing signal handlers")

        # If any of the attributes stdin, stdout, stderr are not None, 
        # bind the system streams sys.stdin, sys.stdout, and/or 
        # sys.stderr to the files represented by the corresponding 
        # attributes. Where the attribute has a file descriptor, the 
        # descriptor is duplicated (instead of re-binding the name).
        self.log.debug("Redirecting standard streams")

        def redirect(new, old, mode):
            self.log.debug("opening %s", new)
            try:
                if new == "-":
                    new = old
                else:
                    # line buffered
                    new = open(new, mode, 1)
            except IOError:
                self.log.debug("Failed to open %s, Exiting", new)
                sys.exit()
            else:
                self.log.debug("opened %s", new.name)
            self.log.debug("redirecting %s to %s", old.name, new.name)
            old.flush()
            os.dup2(new.fileno(), old.fileno())
            new.flush()

        redirect(self.stdin, sys.stdin, "r")
        redirect(self.stdout, sys.stdout, "a+")
        redirect(self.stderr, sys.stderr, "a+")

        self.log.debug("Standard streams redirected")

        # Change current working directory to the path specified by the 
        # working_directory attribute.
        if self.working_directory != None:
            self.log.debug("Changing working directory to %s", self.working_directory)
            os.chdir(self.working_directory)
            self.log.debug("Working directory now set to %s", self.working_directory)


        # If the pidfile attribute is not None, enter its context 
        # manager.
        if self.pidfile != None:
            try:
                self.log.debug("Creating lock file")
                self._lock = LockFile(self.pidfile)
                self._lock.create()
                self.log.debug("Lock file aquired")
            except LockHeldError:
                # bail if fail
                self.log.error("Daemon already running, exiting")
                sys.exit(2)
        else:
            self._lock = DummyLockFile()
                

        # Mark this instance as open (for the purpose of future open and 
        # close calls).
        self.is_open = True

        # Register the close method to be called during Python's exit 
        # processing.
        atexit.register(self.close)
        self.log.debug("Daemonizing complete")

    def terminate(self, signal_number, stack_frame):
        self.log.critical("Recived SIGTERM, exiting")
        raise SystemExit("Recived SIGTERM")
    
    def close(self):
        if self.is_open == False:
            return
        try:
            self._lock.close()
        except LockDestroyError:
            # mask it if no lock file
            #raise LockDestroyError()
            pass
        self.is_open = False

    # context manager 
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *execinfo):
        self.close()
        # pass through all exceptions
        return False


class LockHeldError(Exception):
    """Lock is already held by another process"""
    def __init__(self, filename):
        self.filename = filename
    def __str__(self):
        return "lockfile %s already exists"%(self.filename)

class LockDestroyError(Exception):
    """This covers any case where the lock throws an error when being destroyed"""
    def __init__(self, filename=""):
        self.filename = filename
    def __str__(self):
        return "could not remove lockfile %s"%(self.filename)

class LockFile(object):
    """Creates a lockfile for daemon use"""
    def __init__(self, filename):
        """path: the base folder to create the lockfile in"""
        self.filename = filename
        self.log = logging.getLogger("asylum.daemon.LockFile")
        self.log.debug("Created lock object for filename %s", filename)
        self.got_lock = False

    def create(self):
        flags =  os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_TRUNC|os.O_EXCL
        try:
            f = os.open(self.filename, flags, 0o744)
            f = os.fdopen(f, "w")
            f.write(str(os.getpid()))
            f.flush()
            self.got_lock = True
            self.log.debug("Created lock file %s", self.filename)
        except OSError:
            # lock file exsists
            self.log.error("Failed to create lock file %s", self.filename)
            f = ""
            try:
                f = open(self.filename).read(6)
            except IOError:
                pass
            else:
                self.log.debug("Lock held by process %s", f)
            raise LockHeldError(self.filename)

    def close(self):
        if self.got_lock == True:
            try:
                os.unlink(self.filename)
            except OSError:
                self.log.error("Cannot unlink lock file %s", self.filename)
                raise LockDestroyError(self.filename)
            self.log.debug("Destroyed lock file %s", self.filename)

    # context manager 
    def __enter__(self):
        self.create()
        return self

    def __exit__(self, *execinfo):
        self.close()
        # pass through all exceptions
        return False

class DummyLockFile(object):
    """Creates a lockfile for daemon use"""
    def create(self):
        pass

    def close(self):
        pass

    # context manager 
    def __enter__(self):
        return self

    def __exit__(self, *execinfo):
        return False


if __name__ == "__main__":
    pass
