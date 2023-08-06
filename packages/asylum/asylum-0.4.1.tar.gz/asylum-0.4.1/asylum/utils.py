#!/usr/bin/env python
"""util: Various util routines and cmdline apps
"""
from asylum.conf import merge_settings, get_confs
from asylum.rlimits import set_limits
from asylum.cgroups import get_cgroup_mounts, CGroupMount
from multiprocessing import Lock
from cmd import Cmd
import asylum.conf as conf
import asylum.capabilities
import asylum.syscall
import subprocess
import argparse
import logging
import errno
import shlex
import sys
import os

###########
# Logging #
###########
logger = logging.getLogger("asylum.utils")
logger.addHandler(logging.NullHandler())

def setup_logging(level=logging.ERROR):
    """Misc logging setup to keep things in one place 
    """
    log = logging.getLogger()
    log.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s:%(process)6s:%(name)s:%(levelname)-7s:%(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(level)
    log.addHandler(handler)

#########
# Shell #
#########
class Shell(Cmd):
    prompt = os.path.basename(sys.argv[0]) + "> "
    
    # Build
    def help_build(self):
        conf.build.print_help()

    def do_build(self, args):
        self.handle_command(args, 'build')
        
    def handle_command(self, args, cmdname):
        raw_args = shlex.split(args)
        try:
            command_config, args = conf.get_args([cmdname] + raw_args)
            # commands is defined after the worker functions below
            ret = commands[cmdname](args, command_config)
            if cmdname == 'start':
                self.stdout.write('Process exited with exit code {0}\n'.format(ret))
        except ValueError, err:
            self.stdout.write('Error: {0}\n'.format(err.args[0]))
        except EarlyExit:
            pass

    # Pack
    def help_pack(self):
        conf.pack.print_help()

    def do_pack(self, args):
        self.handle_command(args, 'pack')

    # Start
    def help_start(self):
        conf.start.print_help()

    def do_start(self, args):
        self.handle_command(args, 'start')
        
    # Pause
    def help_pause(self):
        conf.pause.print_help()

    def do_pause(self, args):
        self.handle_command(args, 'pause')
        
    # Stop
    def help_stop(self):
        conf.stop.print_help()

    def do_stop(self, args):
        self.handle_command(args, 'stop')
        
    # kill
    def help_kill(self):
        conf.kill.print_help()

    def do_kill(self, args):
        self.handle_command(args, 'kill')
        
    # List
    def help_list(self):
        conf.list.print_help()

    def do_list(self, args):
        self.handle_command(args, 'list')
        
    # Inject
    def help_inject(self):
        conf.inject.print_help()

    def do_inject(self, args):
        self.handle_command(args, 'inject')
        
    # conf manipulation
    def help_conf(self):
        pass

    def do_conf(self, args):
        self.handle_command(args, 'conf')
        
    def complete_conf(self, text, line, begidx, endidx):
        cmds = ["open", "write", "get", "set", "delete"]
        return [x for x in cmds if x.startswith(text)]

    # Exit
    def do_exit(self, args):
        """Exit the program"""
        sys.exit(0)
        
    do_quit = do_exit
    do_e = do_exit
    do_q = do_exit

    def do_EOF(self, args):
        self.do_exit(args)

####################
# Worker Functions #
####################
def build():
    pass

def pack():
    pass

# Shell money patching/hacks
class EarlyExit(Exception):
    """Work around to prevent parsing of cmdline args if a help option is encountered
    
    it appears argparse relies on the fact that printing the help on '-h' exits, as we
    dont want to exit, raise an exception to jump back to the location we want to be at
    """
    pass
    
class HelpPrinter(argparse._HelpAction):
    @staticmethod
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        raise EarlyExit()

def shell(args, config):
    # monkey patch argparse to not exit on displaying help
    logger.info('Monkey Patching argparse')
    argparse._HelpAction.__call__ = HelpPrinter.__call__

    logger.info('Starting Shell')
    shell = Shell()
    shell.base_args = args
    shell.config = config
    shell.cmdloop()

def start(args, config):
    # Pull settings from conf file
    pre_startup = config["boot"]["pre_startup"]
    post_startup = config["boot"]["post_startup"]
    post_shutdown = config["boot"]["post_shutdown"]
    hostname = config["container"]["hostname"]

    # Work out which namespaces should be enabled
    flags = config["container"]["namespace"]
    
    if args.executable == None:
        logger.info("No command specified, falling back to /bin/sh")
        args.executable = "/bin/sh"

    # pre startup
    if pre_startup:
        logger.info("Executing pre_startup script: %s", pre_startup)
        ret_value = subprocess.Popen(pre_startup, shell=True).wait()
        logger.info("pre_startup returned exit code: %d", ret_value)

    # create a lock here so its avalible to both processes after clone
    # we use this to ensure the child blocks before creating more processes 
    # so we can put it in the correct cgroup in a race free manner
    # unfortuantly we cant ad flags 
    lock = Lock()
    logger.debug("Acquiring client hold lock")
    lock.acquire()
    
    # clone
    logger.debug("Begining Clone")
    pid = asylum.syscall.clone(flags)
    if pid == 0:
        # child
        uts = flags & asylum.syscall.CLONE_NEWUTS
        if uts and hostname:
            logger.info("Setting Hostname: %s", hostname)
            asylum.syscall.sethostname(hostname)
        elif not uts and hostname:
            logger.warn("Not changing hostname, please unshare UTS namespace")
        else:
            if hostname is not None:
                logger.debug("Not setting hostname as unsharing of UTS namespace was not specified")


        # Set priority/nice
        # make sure we do this before we drop capabilities such as CAP_SYS_RESROUCE or rlimit the process
        # which would prevent decreasing of the nice/priority to negative numbers
        logger.info("Setting Priority")
        if args.priority:
            logger.info('Setting priority level: %d', args.priority)
            cur = os.nice(0)
            adj = args.priority - cur
            new_priority = os.nice(adj)
            logger.info("New priority: %d, requested priority: %d, old priority: %d", new_priority, args.priority, cur)

        # Set rlimits
        # make sure we do this before we drop capabilities such as CAP_SYS_RESROUCE
        # which would prevent increasing of rlimits
        logger.info("Setting rlimits")
        if args.rlimit:
            limits = dict(args.rlimit)
            logger.debug("Limits: %s", limits)
            set_limits(limits)

        # Set bounding set and drop capabilities
        logger.info("Setting capabilities")
        try:
            bounding = args.bounding
            if bounding is not None:
                bounding ^= asylum.capabilities.CAP_ALL # we want 1 = what we want to drop
                                                        # not 1 = what we want to keep
                logger.debug("Dropping capabilities from bounding set: 0x%X", bounding)
                asylum.capabilities.drop_bounding(args.bounding)
            caps = args.capabilities
            if caps is not None:
                logger.debug("Setting capabilites set: 0x%X", caps)
                asylum.capabilities.set_caps(caps, caps, caps)
        except (asylum.capabilities.CapabilityError, ValueError, asylum.syscall.ConfigError):
            logger.error("Unable to set requested capabilites")
            # die die die, may be a security risk if we continue
            raise ValueError("Unable to set requested capabilites")

        # post startup
        if post_startup:
            logger.info("Executing post_startup script: %s", post_startup)
            ret_value = subprocess.Popen(post_startup, shell=True).wait()
            logger.info("post_startup returned exit code: %d", ret_value)

        # command execution
        # make sure we get the all clear from the parent before continuing
        lock.acquire()
        logger.debug("Parent released lock, we are go in 5")
        logger.debug('4')
        logger.debug('3')
        logger.debug('2')
        logger.debug('1')
        logger.debug('Blast Off!!')
        logger.debug("Executing %s", args.executable)
        os.execvp(args.executable, [args.executable] + args.args)
    else:
        # parent

        # Place child in cgroup
        if config['cgroup']['cgroup_name']:
            label = config['cgroup']['cgroup_label']
            name = config['cgroup']['cgroup_name']
            mounts = get_cgroup_mounts()
            mount = [x for x in mounts if x[0] == label][0] # select the first valid option
            label, mount, subsystems = mount
            logger.info('Selecting cgroup {0}({1}) of type {2}'.format(label, mount, subsystems))
            cgroup = CGroupMount(mount, label)
            cgroup.create(name)
            
            group = cgroup[name]
            group.tasks = str(pid)
            logger.debug('Process now in cgroup')
            for key, value in config['cgroup'].iteritems():
                if key not in ['cgroup_label', 'cgroup_name', 'on_error']:
                    logger.debug('Setting cgroup setting {0} to {1}'.format(key, value))
                    try:
                        setattr(group, key, value)
                    except (OSError, IOError, AttributeError):
                        if config['cgroup']['on_error'].lower() == 'continue':
                            continue
                        else:
                            raise EarlyExit('cgroup {0}({1}) has no setting {2}'.format(label, mount, key))
             
        # Child can now run freely
        logger.debug("Releasing client hold lock, on behalf of parent process, we wish you good luck and godspeed")
        lock.release()

        while True:
            try:
                child_pid, status = os.waitpid(-1, asylum.syscall.WALL)
                if pid == child_pid:
                    status = os.WEXITSTATUS(status)
                    logger.info("pid:%d has exited with error code %d", child_pid, status)
            except OSError as err:
                if err.errno == errno.ECHILD:
                    # ECHILD inidcates there are no children to wait on, assume all children are dead
                    break
                raise
        logger.info("Namespace init (pid:%d) has exited with error code %d", pid, status)

        # post shutdown
        if post_shutdown:
            logger.info("Executing post_shutdown script: %s", post_shutdown)
            ret_value = subprocess.Popen(post_shutdown, shell=True).wait()
            logger.info("post_startup returned exit code: %d", ret_value)

        # pipe the childs exit code out the parent
        return status

def pause(args, config):
    pass

def stop(args, config):
    pass

def kill(args, config):
    # kill is a specific type of stop
    stop(args, config)

def list(args, config):
    pass

def inject(args, config):
    ### XXX: FIXME, align with start()
    logger.debug("Namespace flags: 0x%x", flags)
    if flags == 0:
        logger.error("No namespace(s) selected")
        raise ValueError("No namespace(s) selected")
        

    if options.executable == None:
        logger.info("No command specified, falling back to /bin/sh")
        options.executable = "/bin/sh"

    pid = args.pid
    logger.debug("Preparing to enter existing namespace (pid=%d)", pid)
    namespace = open("/proc/{0}/ns".format(pid))
    asylum.syscall.setns(flags, namespace)

# Only avalible fromt he command line and not the shell at this time
# Generate a dummy conf file
def generate(args, config):
    config_file = args.generate
    with config_file:
        config_file.write(conf.defaultconfig)
    logger.info("Wrote blank config to %s", config_file.name)
    print("Wrote blank config to %s" % config_file.name)

# Only avalible fromt he command line and not the shell at this time
# Detect kernel support
def detect(args, config):
    from asylum.detect import print_support, CONFIG_FILES
    # filter out [None] from argparse as len() > 0 and therefore [None] == True
    # as its True, it is used instead of CONFIG_FILES and open() barfs on 
    # open(None)
    configs = [x for x in args.kernel_config if x] or CONFIG_FILES
    logger.debug("Detecting cgroup/namespace support in %s", configs)
    try:
        print_support(configs)
    except (IOError, OSError):
        print "Could not open specified config file: %s" % configs[0]
    except ValueError:
        print "Specified file is not a valid config file: %s" % configs[0]

# Command to function mapping
commands = {'build':  build,
            'pack':   pack,
            'shell':  shell,
            'start':  start,
            'pause':  pause,
            'stop':   stop,
            'kill':   kill,
            'list':   list,
            'inject': inject,
            'detect': detect,
            'generate': generate,
            }


####################
# Main Entry Point #
####################
def asylum_main(raw_args=sys.argv[1:]):
    """The main entry point for the asylum command line application
    
    Args:
    -----
    raw_args (list): a list of arguments simmilar to sys.argv[1:] (ie, minus the filename) to be
                     processed and acted upon
    """
    try:
        arg_config, args = conf.get_args(raw_args)
    except IOError:
        logger.critical("Invalid File specified")
        sys.stderr.write("Invalid File Specified\n")
        sys.exit(2)

    # Set up logging
    log_level = { 0:logging.CRITICAL,
                  1:logging.ERROR,
                  2:logging.WARN,
                  3:logging.INFO,
                  4:logging.DEBUG,
                 }.get(args.verbose, logging.DEBUG)
    setup_logging(log_level)

    # now we can log what we parsed from the cmdline
    logger.debug("Conf parsed sys.args: %s", args)

    # Merge configs
    merged_configs = get_confs(args.conf)
    config = merge_settings([arg_config, merged_configs])

    logger.debug("User specified %s command", args.command)

    # begin a pyabussa switchspatch 
    ## i have no idea what it is, but it sounds awesome
    ### we would have also accepted 'dictspatch'
    func = commands.get(args.command, None)
    ret = 0
    try:
        ret = func(args, config)
    except ValueError, err:
        print "Error: {0}".format(err.args[0])

    if args.command == 'start':
        sys.exit(ret)

if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(asylum_main(args))

