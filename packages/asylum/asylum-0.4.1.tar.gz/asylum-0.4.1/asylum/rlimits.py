#!/usr/bin/env python

import resource

r_names = [(x, y) for x, y in resource.__dict__.iteritems() if x.startswith("RLIMIT_")]
r_names = [(x[7:], y) for x,y in r_names]
r_names = dict(r_names)
# sanitze module namespace
del x, y

def parse_limits(s):
    """extract an rlimit name, soft and hard limit from a string
    
    Args:
    -----
    s:  A sepciall crafted string in the format <rlimit name>=<soft limit>:<hard limit>
        <rlimit name> is taken from r_names in this module
        <soft limit> if an integer, empty ('') or INFINITY in which case it is equal to the maximum allowable setting
        <hard limit> if an integer, empty ('') or INFINITY in which case it is equal to the maximum allowable setting
        
    Returns:
    --------
    rlimit_name (int): the id of the rlimit for passing to setrlimit
    limits (2 element tuple): the soft and hard limits as ints
    
    Raises:
    -------
    ValueError if format string is invalid
    KeyError is <rlimit name> is unknown
    ValueError if <soft limit> or <hard limit> is invalid
    resource.error is the syscall returned an error
    
    Examples:
    ---------
    >>> parse_limits('AS=0:0')
    (9, (0, 0))
    >>> parse_limits('AS=512:INFINITY')
    (9, (512, -1L))
    >>> parse_limits('AS=:')
    (9, (-1L, -1L))
    """
    name, limits = [x.strip() for x in s.split("=")]
    
    name = r_names[name]
    limits = extract_limits(name, limits)
    
    return name, limits

def extract_limits(rlimit, limits):
    """extract the soft and hard limit from a string
    
    Args:
    -----
    rlimit: the rlimit id that the below limits represent, used if one or more limits is not specified
            and therefor needs to be checked for its current value
    limits: A specially crafted string in the format <soft limit>:<hard limit>
        <soft limit> if an integer, empty ('') or INFINITY in which case it is equal to the maximum allowable setting
        <hard limit> if an integer, empty ('') or INFINITY in which case it is equal to the maximum allowable setting
        
    Returns:
    --------
    soft (int): the soft limit extracted from the string
    hard (int): the hard limit extracted from the string
    """
    soft, hard = [x.strip() for x in limits.split(":")]
    cur_soft, cur_hard = resource.getrlimit(rlimit)
    soft = resource.RLIM_INFINITY if soft == 'INFINITY' else cur_soft if soft == '' else int(soft)
    hard = resource.RLIM_INFINITY if hard == 'INFINITY' else cur_hard if hard == '' else int(hard)

    return soft, hard

def set_limits(limits):
    """set rlimits to values specified in dict from the cmdline or a config file
    
    Args:
    -----
    limits: a dictonary of limits, where the keys are the id of the limit to be changed
            and the value is a 2 element tuple (soft, hard) to set the rlimit to
    """
    for name, limit in limits.iteritems():
        resource.setrlimit(name, limit)
