#!/usr/bin/env python
"""Conf: a template of the default/basic configuration

we build a default conf file with empty values so we can dump it 
so that the key we want is always present when reading in 
additional conf files.
"""
## Adding new values
# 1. Add new argument to argparse/cmdline processing
#    * make the option visible
# 2. update ordered dict with new section/option under argparse
#    * this ordered dict overrides the other config files, so 
#      substitute values that the cmdline overrides into it and
#      do any required validation/transformation
# 3. update default config file below (SafeConfigParser object)
#    * This is just setting some default options for the (blank) conf 
#      generation option
# 4. update get_confs code with new section/options
#    * you will mainly be adding data transforms here and validation
#      of the config file options


from asylum.syscall import CLONE_ALL, CLONE_NEWIPC, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWUTS, CLONE_NEWUSER, CLONE_NEWPID
from asylum.syscall import clone_flags_from_list
from ConfigParser import SafeConfigParser
from asylum.capabilities import get_mask_from_str
from asylum.rlimits import r_names, parse_limits
from collections import OrderedDict
from socket import gethostname
from StringIO import StringIO
import argparse
import logging
import asylum

CONF_FILES = ["/usr/share/asylum/asylum.conf", "/etc/asylum/asylum.conf"]

logger = logging.getLogger("asylum.conf")
logger.addHandler(logging.NullHandler())

class ConfigError(Exception):
    "There was an error with the supplied config file"

# monkeypatch Config parser to prevent mangling filename paths used
# as option keys (currently calls str.lower() on them
SafeConfigParser.optionxform = lambda self, x: x

class MergeFlags(argparse.Action):
    """argparse.action to OR numbers/flags together eg for bitmask creation
    specify MergeFlags as the argument to the action option in add_argument
    """
    def __call__(self, parser, namespace, values, option_string=None):
        val = getattr(namespace, self.dest)
        val |= self.const
        setattr(namespace, self.dest, val)

conf = SafeConfigParser()

conf.add_section("system")
conf.set("system", "cgroup_root", "/cgroup") # Dir
conf.set("system", "status_dir", "/var/run/asylum") # Dir
conf.set("system", "mount_root", "/srv/asylum/") # Dir

conf.add_section("container")
conf.set("container", "name", "") # String
conf.set("container", "description", "") # String (Multiline?)
conf.set("container", "owner", "") # String
conf.set("container", "hostname", "") # String
conf.set("container", "namespace", "") # "UTS,PID,UID,NET,MOUNT,IPC"  MultiChoice/List
conf.set("container", "capabilities", "") # MultiChoice(get_mask_from_str)
conf.set("container", "bounding_set", "") # MultiChoice(get_mask_from_str)
conf.set("container", "priority", "0") # int

conf.add_section("cgroup")
conf.set("cgroup", "on_error", "exit") # Choice: pass|exit
conf.set("cgroup", "cgroup_label", "") # Choice: pass|exit
conf.set("cgroup", "cgroup_name", "") # Choice: pass|exit
# Dynamic

conf.add_section("rlimit")
# Dynamic

conf.add_section("boot")
conf.set("boot", "pre_startup", '') # Multiline String
conf.set("boot", "post_startup", '') # Multiline String
conf.set("boot", "post_shutdown", '') # Multiline String

conf.add_section("network")
# Dynamic

conf.add_section("mounts")
conf.set("mounts", "visible", "True") # Boolean
# Dynamic

# dance monkey, dance
defaultconfig = StringIO()
conf.write(defaultconfig)
defaultconfig.seek(0)
defaultconfig = defaultconfig.read()

##############
# Cmdline
##############
description = """Run a program in a diffrent virtual namespace."""

args = argparse.ArgumentParser(description=description)
args.add_argument("--debug", default=None, const="", type=argparse.FileType("w"), nargs="?", metavar="FILE",
                    help="When an unhandled exception grab as much info as possible and bundle it into a debug file")
args.add_argument("-c", "--conf", default=CONF_FILES, action="append", type=argparse.FileType(),
                    help="Specify a config file")
args.add_argument("-v", "--verbose", default=0, action="count",
                    help="Output more verbose logging, can be specified multiple times")
args.add_argument('--version', action='version', version=asylum.__version__, help="Display the version number and exit")
args.set_defaults(namespaces=0, hostname=None, capabilities=None, bounding=None, rlimit=[], cgroup_name=None, 
cgroup_label='cgroup', cgroup_error='continue')

# Commands #
subparsers = args.add_subparsers()

# Build #
build = subparsers.add_parser("build", help="Build a namespace from a template")
build.add_argument("build_dir", metavar="DIR")
build.add_argument("-c", "--conf", default=CONF_FILES, action="append", type=argparse.FileType(),
                    help="Specify a config file")
build.add_argument("-t", "--template", default=[], action="append", type=argparse.FileType(), nargs="*",
                    help="""Template to build the new instance from. template can be a directory or a
                            tar file that is gzip'd or bzip2'd which will be automatically decompressed"""
                    )
build.set_defaults(command="build")

# Pack #
pack = subparsers.add_parser("pack", help="Build a template from a namespace")
pack.add_argument("template", type=argparse.FileType(), metavar="TEMPLATE", help="File to save the template to")
pack.add_argument("build_dir", metavar="DIR")
pack.set_defaults(command="pack")

# Shell #
shell = subparsers.add_parser("shell", help="Start an interactive asylum shell")
shell.add_argument("script", action="append", default=[], type=argparse.FileType(), nargs="*", metavar="FILE",
                    help='A script to read from, specify "-" for stdin')
shell.set_defaults(command="shell")

# Start #
start = subparsers.add_parser("start", help="Start up a namespace")
namespace = start.add_argument_group("Namespaces", "The namespaces to unshare")
namespace.add_argument("-H", "--UTS", const=CLONE_NEWUTS, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the kernel hostname")
namespace.add_argument("-U", "--UID", const=CLONE_NEWUSER, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the UID namespace")
namespace.add_argument("-P", "--PID", const=CLONE_NEWPID, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the PID namespace")
namespace.add_argument("-M", "--MOUNT", const=CLONE_NEWNS, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the Mount namespace")
namespace.add_argument("-N", "--NET", const=CLONE_NEWNET, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the Network namespace")
namespace.add_argument("-I", "--IPC", const=CLONE_NEWIPC, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the IPC namespace")
namespace.add_argument("-A", "--ALL", const=CLONE_ALL, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the all namespace")
capabilities = start.add_argument_group("Capabilites", "Limit access to admin features")
capabilities.add_argument("-C", "--capabilities", help="List of capabilities to give the namespace, use '-' to remove "
                       "a capability from the full set eg: -KILL,ADMIN will remove KILL and ADMIN from the full "
                        "'all capabilities' set. to grant all capabilities use 'ALL'", metavar="LIST",
                        type=get_mask_from_str, default=None)
capabilities.add_argument("-B", "--bounding", help="List of capabilities to use as the bounding set in the namespace, "
                       "use '-' to remove a capability from the full set. eg: -KILL,ADMIN will remove KILL and ADMIN"
                        " from the full 'all capabilities' set. to grant all capabilities use 'ALL'", metavar="LIST",
                        type=get_mask_from_str, default=None)
rlimit = start.add_argument_group("RLimits", "Per process application limits")
rlimit.add_argument("-r", "--rlimit", help="rlimit the child namespace. eg -r NPROCS=30:INFINITY to set the soft "
                        "limit to 30 and the hard limit to infinity. valid names are [{0}]".format(', '.join(r_names.keys())),
                       type=parse_limits, action='append', default=[], metavar='LIMIT')
cgroup = start.add_argument_group("CGroups", "Multi Process application limits")
cgroup.add_argument("--cgroup-name", default=None, metavar="NAME",
                    help="name of the cgroup to use to manage this container")
cgroup.add_argument("--cgroup-label", default='cgroup', metavar="LABEL",
                    help="The label for the cgroup mount to add the cgroup to, only useful if you have more than one "
                    "cgroup mount point. in most cases this is autodetected. DEFAULT=cgroup")
cgroup.add_argument("--cgroup-error", default='continue', metavar="ACTION",
                    help="What to do when a config file specifies a non existent cgroup setting, 'continue' to continue "
                    "'exit' to quit. DEFAULT='continue'")
start.add_argument("--hostname", default=gethostname(), help="The hostname to set in the child namespace")
start.add_argument("-p", "--priority", default=0, type=int, help="The priority/nice to run as. ranges from -19 to 20 with "
                    "-19 being the highest priority and 20 being the lowest. non-privliged users can only increase this from "
                    "its default value. DEFAULT=0")
start.add_argument("-n", "--name", default="", help="Name to use for the namespace")
start.add_argument("-d", "--description", default="", help="Description of the namespace")
start.add_argument("-c", "--conf", default=CONF_FILES, action="append", type=argparse.FileType(),
                        help="Specify a config file")
start.add_argument("executable", nargs="?", metavar="CMD", help="The program to execute in the namespace")
start.add_argument("args", nargs="*", metavar="ARGS", help="Argument to pass to child program")
start.set_defaults(command="start")

# Pause #
pause = subparsers.add_parser("pause", help="Freeze a selected namespace")
pause.add_argument("namespace", default="", metavar="NAMESPACE", help="The pid or name of the namespace to stop")
pause.set_defaults(command="pause")

# Stop #
stop = subparsers.add_parser("stop", help="Stop a namespace")
kill = stop.add_argument_group("Signaling Options", "Notifcation method to use to shutdown a namespace")
kill.add_argument("-0", "--init", default=False, action="store_true", help="Send a signal to init process")
kill.add_argument("-a", "--all", default=False, action="store_true",
                    help="Send a signal to all processes in the selected namespace")
kill.add_argument("-d", "--delay-kill", default=None, const=5, type=int, metavar="DELAY", nargs="?",
                    help="Send a signal to init then wait a predefinied time before signaling remaining processes. (default: 5 seconds)")
stop.add_argument("-s", "--signal", default=9,
                    help='Signal to send to kill the processes in a namespace, specify "list" to list the avalible signals')
stop.add_argument("namespace", default="", metavar="NAMESPACE", help="The pid or name of the namespace to stop")
stop.set_defaults(command="stop")

# Kill #
# Note: this is a seperate kill to the one used as an argument group above
kill = subparsers.add_parser("kill", help='Kill a namespace, alias for "stop -s 9 -a [name]"')
kill.add_argument("namespace", default="", metavar="NAMESPACE", help="The pid or name of the namespace to stop")
kill.set_defaults(command="stop", all=True, signal=9)

# List #
list = subparsers.add_parser("list", help="List all running instances")
list.set_defaults(command="list")

# Inject #
inject = subparsers.add_parser("inject", help="Start a process in the specified namespace")
namespace = inject.add_argument_group("Namespaces", "The namespaces to unshare")
namespace.add_argument("-H", "--UTS", const=CLONE_NEWUTS, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the kernel hostname")
namespace.add_argument("-U", "--UID", const=CLONE_NEWUSER, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the UID namespace")
namespace.add_argument("-P", "--PID", const=CLONE_NEWPID, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the PID namespace")
namespace.add_argument("-M", "--MOUNT", const=CLONE_NEWNS, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the Mount namespace")
namespace.add_argument("-N", "--NET", const=CLONE_NEWNET, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the Network namespace")
namespace.add_argument("-I", "--IPC", const=CLONE_NEWIPC, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the IPC namespace")
namespace.add_argument("-A", "--ALL", const=CLONE_ALL, action=MergeFlags, dest='namespaces', nargs=0,
                        help="Unshare the all namespace")
capabilities = inject.add_argument_group("Capabilites", "Limit access to admin features")
capabilities.add_argument("-C", "--capabilities", help="List of capabilities to give the namespace, use '-' to remove "
                       "a capability from the full set eg: -KILL,ADMIN will remove KILL and ADMIN from the full "
                        "'all capabilities' set. to grant all capabilities use 'ALL'", metavar="LIST",
                        type=get_mask_from_str, default=None)
capabilities.add_argument("-B", "--bounding", help="List of capabilities to use as the bounding set in the namespace, "
                       "use '-' to remove a capability from the full set. eg: -KILL,ADMIN will remove KILL and ADMIN"
                        " from the full 'all capabilities' set. to grant all capabilities use 'ALL'", metavar="LIST",
                        type=get_mask_from_str, default=None)
rlimit = inject.add_argument_group("RLimits", "Place limits on application resources")
rlimit.add_argument("-r", "--rlimit", help="rlimit the child namespace. eg -r NPROCS=30:INFINITY to set the soft "
                        "limit to 30 and the hard limit to infinity. valid names are [{0}]".format(', '.join(r_names.keys())),
                       type=parse_limits, action='append', default=[], metavar='LIMIT')
inject.add_argument("-p", "--priority", default=0, type=int, help="The priority/nice to run as. ranges from -19 to 20 with "
                    "-19 being the highest priority and 20 being the lowest. non-privliged users can only increase this from "
                    "its default value. DEFAULT=0")
inject.add_argument("namespace", default="", metavar="NAMESPACE",
                        help="The pid or name of the namespace to run the command in")
inject.add_argument("executable", nargs="?", metavar="CMD", help="The program to execute in the namespace")
inject.add_argument("args", nargs="*", metavar="ARGS", help="Argument to pass to child program")
inject.set_defaults(command="inject")

# Detect #
detect = subparsers.add_parser("detect", help="Auto-Detect compiled kernel options")
detect.add_argument(metavar="FILE", dest='kernel_config', nargs="?", action='append',
                    help="The config file to check the settings of")
detect.set_defaults(command="detect")

# Generate #
generate = subparsers.add_parser("generate", help="Generate an empty conf file")
generate.add_argument("generate", type=argparse.FileType("w"), metavar="FILE",
                   help="Config file to write blank config to")
generate.set_defaults(command="generate")

# cleanup
del namespace, rlimit, capabilities, cgroup

def get_args(argv):
    """parse the supplied command line and return a copy of the parsed arguments as well as a
    base config file with the command line overrides interpollated
    
    Args:
    -----
    argv: The arguments to parse with argparse
    
    Returns:
    --------
    Tuple(settings, options):
    =========================
    settings: A Basic config made from Ordered Dicts with default values set and comamnd line 
              flags overriding where applicable
    options:  The argparse object returned from parsing the argv variable
    """

    options = args.parse_args(argv)

    # Take cmdline arguments and dump into config for merging with other configs
    settings = OrderedDict(
                system = OrderedDict(
                    cgroup_root=None,
                    status_dir=None,
                    mount_root=None,
                    ),
                container = OrderedDict(
                    name="",
                    description="",
                    owner="",
                    hostname=options.hostname,
                    namespace=options.namespaces,
                    capabilities=options.capabilities,
                    bounding_set=options.bounding,
                    priority=None,
                    ),
                cgroup = OrderedDict(
                    cgroup_name=options.cgroup_name,
                    cgroup_label=options.cgroup_label,
                    on_error=options.cgroup_error,
                    ),
                rlimit = OrderedDict(options.rlimit),
                boot = OrderedDict(
                    pre_startup="",
                    post_startup="",
                    post_shutdown="",
                    ),
                network = OrderedDict(),
                mounts = OrderedDict(
                    visible=False
                    ),
                )

    logger.debug("cmdline arg settings: %s", settings)
    logger.debug("cmdline arg options: %s", options)

    return settings, options

def get_confs(fns=[], fds=[]):
    """Get the settings from a list of config files

    Args:
    -----
    fns: A list of filenames to open to read configs from
    fds: A list of FDs to read the configs from
    
    Returns:
    --------
    ConfigParser.SafeConfigParser instance:    Contains the merged settings from all the 
                                            config files
    """
    logger.debug("Conf file names: %s", fns)
    logger.debug("Conf file descriptors: %s", fds)

    # this code is longer than it needs to be as it is also an example
    # of how to read the conf corectly if using this code as a module
    config = SafeConfigParser()
    default = StringIO(defaultconfig)
    config.readfp(default)
    config.read(fns)
    [config.readfd(fd) for fd in fds]

    # pull out the ordered dicts directly instead of the annoying ini interface
    config = config._sections

    # normalize file
    # Namespace
    namespaces = config['container']['namespace'].split(",")
    namespaces = [namespace.strip().upper() for namespace in namespaces]
    namespaces = clone_flags_from_list(namespaces)
    config['container']['namespace'] = namespaces
    # Capabilities
    capabilities = config['container']['capabilities']
    capabilities = get_mask_from_str(capabilities)
    config['container']['capabilities'] = capabilities
    # Bounding set
    bounding = config['container']['bounding_set']
    bounding = get_mask_from_str(bounding)
    config['container']['bounding_set'] = bounding
    # Priority
    config['container']['priority'] = int(config['container']['priority'])
    # Cgroup error action
    action = config['cgroup']['on_error'].strip().lower()
    action = "pass" if action == "pass" else "exit"
    config['cgroup']['on_error'] = action
    del config['cgroup']['__name__'] # remove as it interferes with things
                                     # due to keys being processed in a loop
    # rlimits
    del config['rlimit']['__name__'] # remove as it interferes with things
                                     # due to keys being processed in a loop
    # Network
    del config['network']['__name__'] # remove as it interferes with things
                                     # due to keys being processed in a loop
    # Mounts
    action = config['mounts']['visible'].strip().lower()
    action = bool(action)
    config['mounts']['visible'] = action
    del config['mounts']['__name__'] # remove as it interferes with things
                                     # due to keys being processed in a loop

    logger.debug("Conf file settings: %s", config)

    return config
    
def merge_settings(settings):
    """Merge several sets of options/configs into one set of settings

    Args:
    -----
    settings: list of config files

    Returns:
    --------
    OrderedDict Instance: Contains an ORderedDict for each section of the config file

    Notes:
    ------
    * The conf files are specified in order of priority with the first in the
      list being the most high priority item, higher priority items override
      settings in lower priority config files

    Examples:
    ---------
    Example Merging seperate sections:
    >>> from collections import OrderedDict
    >>> a = dict(a={})
    >>> b = dict(b={})
    >>> merge_settings([a, b])
    OrderedDict([('b', OrderedDict()), ('a', OrderedDict())])

    Example merging same section
    >>> from collections import OrderedDict
    >>> a = dict(a={2:2})
    >>> b = dict(a={1:1})
    >>> merge_settings([a, b])
    OrderedDict([('a', OrderedDict([(1, 1), (2, 2)]))])

    Example merging same section and key, with precedence
    >>> from collections import OrderedDict
    >>> a = dict(a={'hostname': 'specified'})
    >>> b = dict(a={'hostname': 'default'})
    >>> merge_settings([a, b])
    OrderedDict([('a', OrderedDict([('hostname', 'specified')]))])

    Example merging same section and key, with precedence v2
    >>> from collections import OrderedDict
    >>> a = dict(a={'hostname': None})
    >>> b = dict(a={'hostname': 'default'})
    >>> merge_settings([a, b])
    OrderedDict([('a', OrderedDict([('hostname', 'default')]))])

    Example of key being created with no value
    >>> from collections import OrderedDict
    >>> a = dict(a={'hostname': None})
    >>> b = dict(a={'hostname': None})
    >>> merge_settings([a, b])
    OrderedDict([('a', OrderedDict([('hostname', None)]))])
    """
    settings = reversed(settings)
    merged_settings = OrderedDict()
    for config in settings:
        for section in config.iterkeys():
            # add section if it does not exsist
            merged_settings.setdefault(section, OrderedDict())
            for key, val in config[section].iteritems():
                if val or key not in merged_settings[section]:
                    merged_settings[section][key] = val

    logger.debug("merged settings: %s", merged_settings)

    return merged_settings

if __name__ == "__main__":
    import sys
    get_args(sys.argv[1:])
