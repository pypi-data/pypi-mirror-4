#!/usr/bin/env python
"""Cgroup and Namespace auto detection script"""
from collections import defaultdict
import os

try:
    from blessings import Terminal
    t = Terminal()
    RED = t.red
    GREEN = t.green
    NORMAL = t.normal
    BOLD = t.bold
    del t
    del Terminal
except ImportError:
    RED = ''
    GREEN = ''
    NORMAL = ''
    BOLD = ''
    
# The below code is data driven, in most cases you should only need to
# update the data to add detection for the feature you want

# kernel setting names are taken from the posible locations below
# this constant is also used to control where to look up the running
# kernels options. Tuple to prevent modification (functions that use this
# take a 'paths' option to specify a diffrent bunch of files to look up
CONFIG_FILES = ("/proc/config", "/proc/config.gz", "/proc/config.bz2")

# <kernel setting name>, <Friendly name> tuples in a list
NAMESPACES = [  ("CONFIG_NAMESPACES", "Basic Namespace Support"),
                ("CONFIG_UTS_NS", "UTS (hostname) Support"),
                ("CONFIG_IPC_NS", "IPC Namespace Support"),
                ("CONFIG_USER_NS", "User Namespace Support"),
                ("CONFIG_PID_NS", "PID Namespace Support"),
                ("CONFIG_NET_NS", "Network Namespace Support"),
                ("CONFIG_NF_CONNTRACK_NETBIOS_NS", "Conntrack Namespace Support"),
                ]

# <kernel setting name>, <Friendly name> tuples in a list
CGROUPS = [ ("CONFIG_CGROUPS", "Basic Cgroup support"),
            ("CONFIG_CGROUP_DEBUG", "Example Cgroup"),
            ("CONFIG_CGROUP_NS", "Namespace Cgroup support"),
            ("CONFIG_CGROUP_CPUACCT", "Cgroup CPU accounting"),
            ("CONFIG_CGROUP_SCHED", "CPU scheduling/throttling Cgroup support"),
            ("CONFIG_BLK_CGROUP", "Block Device rate limiting"),
            ("CONFIG_DEBUG_BLK_CGROUP", "Block Device rate limiting debugging"),
            ("CONFIG_CFQ_GROUP_IOSCHED", "CFQ group IO scheduling throttling"),
            ("CONFIG_CGROUP_FREEZER", "Cgroup freezer support"),
            ("CONFIG_CGROUP_DEVICE", "Cgroup device support"),
            ("CONFIG_CGROUP_MEM_RES_CTLR", "Cgroup memory wupport"),
            ("CONFIG_CGROUP_MEM_RES_CTLR_SWAP", "Cgroup swap support"),
            ("CONFIG_CGROUP_MEM_RES_CTLR_SWAP_ENABLED", "Cgroup swap support enabled by default"),
            ("CONFIG_NET_CLS_CGROUP", "Cgroup network classifier support"),
            ]

# <kernel setting name>, <Friendly name> tuples in a list
NETWORK = [ ("CONFIG_MACVLAN", "Macvlan Support"),
            ("CONFIG_MACVTAP", "Macvlan TAP Support"),
            ("CONFIG_VETH", "Virtual Ethernet Pipe Pair"),
            ("CONFIG_VLAN_8021Q", "VLAN Support"),
            ]

# <kernel setting name>, <Friendly name> tuples in a list
SECURITY = [("CONFIG_SECURITY_DMESG_RESTRICT", "Restrict dmesg to CAP_SYS_ADMIN"),
            ("CONFIG_SECURITY_FILE_CAPABILITIES", "Assign capabilities to arbitrary files"),
            ("CONFIG_DEVPTS_MULTIPLE_INSTANCES", "Multiple Private devpts mounts"),
            ]
 
# A list of posible states a kernel compile option can be in
# the Key is taken from after the "=" sign and the value is the friendly name
STATUS = {"Y":"Compiled", "M":"Module", "N":"Not Compiled", "NA":"Not Avalible"}

def get_config(paths=CONFIG_FILES):
    """Looks for the kernel config in the default places and returns a file object

    Args:
    -----
    paths: a list of paths to look for the config file from
    
    Return:
    -------
    file: file opened read only with open()

    Notes:
    ------
    * if the config file is gzip'd or bz2'd then this will return a decoded file
      uncompresion code is selected based on the file name
    """
    for path in paths:
        if os.path.isfile(path):
            break
    else:
        raise IOError("No Config file found")

    if path.endswith(".gz"):
        import gzip
        # unzip
        file = gzip.open(path)
    elif path.endswith(".bz2"):
        import bz2
        file = bz2.BZ2File(path, "r")
    else:
        file = open(path, "r")

    return file

def config_to_dict(config):
    """Parse the config and convert it to a dictonary
    
    Args:
    -----
    config: The config to read the options from, requires an iterable that returns
            one line per iteration
            
    Returns:
    --------
    options: A dictonary where the Key is te Kernel option and the Value is its status
             see STATUS for a list of posible states
    """
    options = defaultdict(lambda: "NA")

    config = [line for line in config if line.strip() != ""]
    config = [line for line in config if line.strip() != "#"]

    for line in config:
        if line.startswith("# ") and line.strip().endswith(" is not set"):
            option = line.split()[1]
            options[option] = "N"
        elif "=" in line:
            option, setting = line.split("=")
            if setting.strip() == "m":
                options[option] = "M"
            else:
                options[option] = "Y"
    return options

def check_flags(config, flags):
    """Check to see if flags area avalible in the kernel
    
    Args:
    -----
    config: The config file to perfrom the checks against
    flags: The flags to check for

    Returns:
    --------
    options: a list of tuples containg the kernel options and friendly name
    """
    options = []

    for flag_name, description in flags:
        module_status = config[flag_name]
        compile_status = STATUS[module_status]
        options.append((flag_name, description, compile_status))

    return options

def create_check(flags):
    """Closure for generating checks of specific features
    
    Args:
    -----
    flags: The flags to check for
    
    Returns:
    --------
    checker: a function/closure represeneting the check you wish to perform
    
    Notes:
    ------
    * check_flags is not defined as the inner scope as it may be useful on its own
      therefore we just generate a simple wrapper function to call it with the specified 
      args
    """
    def checker(config):
        """Check to see if support for a group of kernel options is enabled
        
        Args:
        -----
        config: The config file to perfrom the checks against
        flags: The flags to check for provided in the outer scope of this closure (create_check)
        
        Returns:
        --------
        output of check_flags: a list of tuples containg the kernel options and friendly name
        """
        return check_flags(config, flags)
    return checker

# as these are all variations on eachother, instiate them using closures from a 
# common base (specified in create_check)
check_namespaces = create_check(NAMESPACES)
check_cgroups = create_check(CGROUPS)
check_network = create_check(NETWORK)
check_security = create_check(SECURITY)

def print_support(configs):
    """Print the supported options directly to stdout in a nicly formated way"""
    if not isinstance(configs, (tuple, list)):
        configs = (configs,)
    config = get_config(configs)
    config = config_to_dict(config)

    # Check the config for support for specific features and put them into 
    # seperate varibles/catgories for later formatting
    namespaces = check_namespaces(config)
    cgroups = check_cgroups(config)
    network = check_network(config)
    security = check_security(config)

    # More data driven programming
    for description, container in [ ("Namespace Support", namespaces),
                                    ("Cgroup Support", cgroups),
                                    ("Network Support", network),
                                    ("Security Extras", security),]:
        print(BOLD + description + ":" + NORMAL)
        print("| {0:^40} | {1:^40} | {2:^12} |".format("Kernel Option", "Description", "Status"))
        print("-" * 102)
        for flag, description, compile_status in container:
            if compile_status in ['Not Avalible', 'Not Compiled']:
                color = RED
            else:
                color = GREEN
            print("| {bold}{0:40}{normal} | {1:40} | {color}{2:^12}{normal} |".format(
                    flag, description, compile_status, color=color, normal=NORMAL, bold=BOLD))
        print("")

if __name__ == "__main__":
    print_support()
