#!/usr/bin/env python
"""Control capability bits and how they are inherited"""
from asylum.syscall import prctl, _libc, CapabilityError
import ctypes
import logging
import errno

log = logging.getLogger("asylum.capabilities")

CAP_NONE            = 0
CAP_CHOWN           = 1 << 0
CAP_DAC_OVERRIDE    = 1 << 1
CAP_DAC_READ_SEARCH = 1 << 2
CAP_FOWNER          = 1 << 3
CAP_FSETID          = 1 << 4
CAP_KILL            = 1 << 5
CAP_SETGID          = 1 << 6
CAP_SETUID          = 1 << 7
CAP_SETPCAP         = 1 << 8
CAP_LINUX_IMMUTABLE = 1 << 9
CAP_NET_BIND_SERVICE = 1 << 10
CAP_NET_BROADCAST   = 1 << 11
CAP_NET_ADMIN       = 1 << 12
CAP_NET_RAW         = 1 << 13
CAP_IPC_LOCK        = 1 << 14
CAP_IPC_OWNER       = 1 << 15
CAP_SYS_MODULE      = 1 << 16
CAP_SYS_RAWIO       = 1 << 17
CAP_SYS_CHROOT      = 1 << 18
CAP_SYS_PTRACE      = 1 << 19
CAP_SYS_PACCT       = 1 << 20
CAP_SYS_ADMIN       = 1 << 21
CAP_SYS_BOOT        = 1 << 22
CAP_SYS_NICE        = 1 << 23
CAP_SYS_RESOURCE    = 1 << 24
CAP_SYS_TIME        = 1 << 25
CAP_SYS_TTY_CONFIG  = 1 << 26
CAP_MKNOD           = 1 << 27
CAP_LEASE           = 1 << 28
CAP_AUDIT_WRITE     = 1 << 29
CAP_AUDIT_CONTROL   = 1 << 30
CAP_SETFCAP         = 1 << 31
CAP_MAC_OVERRIDE    = 1 << 32
CAP_MAC_ADMIN       = 1 << 33
CAP_LAST_CAP        = CAP_MAC_ADMIN
CAP_ALL             = 0b111111111111111111111111111111111 # << 33 "1" bits

# Begin voodoo
capabilities = {}
environ = locals().copy()
for name, val in environ.iteritems():
    if name.startswith("CAP_"):
        # make it fully reversable, int => str and str => int
        capabilities[name] = val
        capabilities[val] = name
# somthing should have died by now, and i belive it was readability

class APIError(Exception):
    """Kernel APIs match no known version, please consider updating this program or contacting the developers"""

def get_mask_from_str(list, sep=",", all_caps=CAP_ALL):
    """Given a string, work out which capabilties are specified and return a mask
    contaning those capabilities (1=present)
    
    Args:
    -----
    list:       A 'sep' seperated string of capabilities that may optiannly be prepended
                with '-', all entries are striped of whitespace and the '-'. only the
                first char is used to deterimine wether permissions are added or
                subtracted from CAP_ALL
    sep:        The seperater to use between capabilities, defaults to "-" however "|"
                may be useful for some applications
    all_caps:   Used for debugging in doctests, canbe used to override CAP_ALL when
                subtracting permissions, all bits to the left of the right most bit
                must be 1 (uses Xor)

    Exceptions:
    -----------
    ValueError: an unknown capability was specified
                
    Usage:
    ------
    >>> ret = get_mask_from_str("CHOWN,KILL")
    >>> bin(ret)
    '0b100001'
    >>> ret = get_mask_from_str("CHOWN|KILL", "|")
    >>> bin(ret)
    '0b100001'
    >>> ret = get_mask_from_str("-CHOWN|KILL", "|", 0b11111111)
    >>> bin(ret)
    '0b11011110'
    """
    negate = False
    if list[:1] == "-":
        negate = True

    mask = 0
    list = [x.strip("-").strip() for x in list.split(sep)]
    for item in list:
        try:
            if len(item) > 0:
                mask |= capabilities["CAP_" + item]
        except KeyError:
            raise ValueError('Unknown Capability "%s" specified', item)
    if negate:
        # invert CAP_ALL at the places specified by mask
        # therefore removing specifed features
        mask ^= all_caps
            
    return mask

# Which permission set to update/read
# (as per linux/capabiltites.h)
PERMITTED, INHERITABLE, EFFECTIVE = range(3)

# Get/set whether or not to drop capabilities on setuid() away from
# uid 0 (as per security/commoncap.c)
PR_GET_KEEPCAPS = 7
PR_SET_KEEPCAPS = 8

# Get/set the capability bounding set (as per security/commoncap.c)
PR_CAPBSET_READ = 23
PR_CAPBSET_DROP = 24

# Get/set securebits (as per security/commoncap.c) (see SECBITS section below)
PR_GET_SECUREBITS = 27
PR_SET_SECUREBITS = 28

# SECBITS
# taken from 3.1-rc4 in include/linux/securebits.h
SECBITS_NOROOT = 1 << 0          # do not reset capabilties across uid 0 execv OR execv on a setuid binary
SECBITS_NO_SUID_FIXUP = 1 << 2   # dont change cap bits on a uid of fsuid change (setuid or setresuid) 
                                 # (effective and filesystem uid only)
SECBITS_KEEP_CAPS = 1 << 4       # if a process drops all uid 0s then dont reset the capabilities (reset across execv)
# 'Locked' versions on the secbits that cannot be undone/set
SECBITS_NOROOT_LOCKED = 1 << 1
SECBITS_NO_SUID_FIXUP_LOCKED = 1 << 3
SECBITS_KEEP_CAPS_LOCKED = 1 << 5

SECBITS_ALL = SECBITS_NOROOT | SECBITS_NO_SUID_FIXUP | SECBITS_KEEP_CAPS
SECBITS_ALL_LOCKED = SECBITS_NOROOT_LOCKED | SECBITS_NO_SUID_FIXUP_LOCKED | SECBITS_KEEP_CAPS_LOCKED


# Linux capability version
# tuple is (Version, how many cap_data structures)
# (as per linux/capabiltites.h)
LINUX_CAPABILITY_VERSIONS = {0x19980330: (1, 1),
                            0x20071026: (2, 2),
                            0x20080522: (3, 2),
                            }


# The following information is as acurate as the man pages, which is to say its tottally wrong

# capabilties are ethier permited, inheritable or effective
# Permitted:    What is allowed
# Inheritable:  What the descendents get
# Effective:    What is currently active
# Bounding:     The set of capabilities that is permitted across execv()

# VM wide limiting comes from the Bounding set as that overrides any filesystem granted Permited
# capabiltieis that may be granted, as the effective == permited after an execv and inherited is 
# unchanged

# therefore for a VM we should limit only the Bounding set and the rest sorts itself out
# but we should find a way to poll the P I and E sets and change them as required

# note: changing P requires CAP_SETPCAP

def get_sec_bits():
    """Retrive a copy of the secbits mask
    
    relevant Flags are stored in the asylum.capabilities module and start with SECBIT_
    see the prctl man page for more info

    Returns:
    int: bitmask of SECBITS_*
    """
    return prctl(PR_GET_SECUREBITS)
    
def set_sec_bits(flags=0):
    """Set the secbits to the first argument
    
    relevant Flags are stored in the asylum.capabilities module and start with SECBIT_
    see the prctl man page for more info
    
    Args:
    -----
    flags: the bitmask of features to enable/disable
    
    Notes:
    -----_
    * Use of a SECBIT ending in LOCKED is irreversable
    """
    prctl(PR_SET_SECUREBITS, flags)
    
def get_bounding(flags=CAP_ALL):
    """Retrive the current status of the bounding capability set
    
    Args:
    -----
    flags=CAP_ALL: The flags you are intrested in retriving
    
    Returns:
    --------
    int: Bitmask of CAP_* capabilities
    
    Notes:
    ------
    * You can specific a specific flag you are intrested in or provide a bitmask
      of all the flags you are intrested in due to the prctl api only allowing
      you to retrive the value of one capability at a time, therefore we patch
      over this and accept a bit mask to eb consistent with the other apis in
      this module
    """
    caps = 0
    i = 0
    while flags != 0:
        flag = flags & 1
        if flag:
            caps |= prctl(PR_CAPBSET_READ, i) << i
        i += 1
        flags >>= 1
    return caps

def drop_bounding(flags=CAP_NONE):
    """Drop capabilites from the Bounding set, see the man pages for prctl and 
    capabilities for more in depth info
    
    Args:
    -----
    flags:  a bit mask of capabilies to drop from the bounding set
    
    Notes:
    ------
    * CAP_SETPCAP is always dropped last so that all drop operations have the
      required capabilites to complete as the prctl only allows dropping of a 
      single capability at a time
    """
    # check if we are dropping capability setting
    cappset = flags & CAP_SETPCAP
    # mask out SETPCAP so we can set it last
    flags &= (CAP_ALL ^ CAP_SETPCAP)

    i = 0
    # drop the capabilites one by one
    while flags != 0:
        flag = flags & 1
        if flag:
            prctl(PR_CAPBSET_DROP, i)
        i += 1
        flags >>= 1
    
    # finally, if we are trying to drop SETPCAP, do it last
    # as otherwise it prevents us from correclty dropping it
    if cappset:
        prctl(PR_CAPBSET_DROP, CAP_SETPCAP)

def get_caps(process=0):
    """Retrive the current permmited, inheritable and effective capability sets
    
    Args:
    -----
    process: the PID of the process to retrive the capabilities list of
             0 selects the current process as returnd by os.getpid()
    
    Returns:
    --------
    Tuple:
    ======
    arg1: The permiited capability bitmask (long)
    arg2: The inheritable capability bitmask (long)
    arg3: The effective capability bitmask (long)
    """
    header = cap_header()
    header.version = VERSION_MAGIC
    # pid=0 means us, specifing a diffrent (valid) pid allows cross process
    # capability retrival
    header.pid = 0
    # are we using the 32bit api or a newer version
    if DATA_SECTIONS == 1:
        data = cap_data()
        _capget(header, data)
        return data.permitted, data.inheritable, data.effective
    else:
        data = cap_data * 2
        data = data()
        _capget(header, data)
        # merge 2x 32bit values into one 64bit long
        permitted = data[1].permitted << 32 | data[0].permitted
        inheritable = data[1].inheritable << 32 | data[0].inheritable
        effective = data[1].effective << 32 | data[0].effective
        return permitted, inheritable, effective
            
def set_caps(permitted, inheritable, effective, process=0):
    """Set the permitted, inheritable and effective capabilites
    
    Args:
    -----
    permitted:   The permitted bitmask consisting of ORed CAP_*
    inheritable: The inheritable bitmask consisting of ORed CAP_*
    effective:   The effective bitmask consisting of ORed CAP_*
    process:     the PID of the process to retrive the capabilities list of
                 0 selects the current process as returnd by os.getpid()


    """
    header = cap_header()
    header.version = VERSION_MAGIC
    # pid=0 means us, specifing a diffrent (valid) pid allows cross process
    # capability changes
    header.pid = 0
    # are we using the 32bit api or a newer version
    if DATA_SECTIONS == 1:
        data = cap_data()
        data.permitted = permitted
        data.inheritable = inheritable
        data.effective = effective
    else:
        data = cap_data * 2
        data = data()
        mask = pow(2, 32) - 1
        # split our longs into 2 32 bit values
        data[0].permitted = permitted & mask
        data[0].inheritable = inheritable & mask
        data[0].effective = effective & mask
        # no need to perform an AND as the >> discards those bits
        data[1].permitted = permitted >> 32
        data[1].inheritable = inheritable >> 32
        data[1].effective = effective >> 32
    _capset(header, data)
    
def cap_valid(cap):
    """Determine if the specified capability is valid
    
    Returns:
    --------
    Boolean: True = valid, False = not valid
    """
    return 0 <= cap <= CAP_LAST_CAP

class cap_data(ctypes.Structure):
    """"cap_user_data_t datap" from "linux/capability.h" used in conjunction with C call capset/capget
    
    Fields:
    -------
    effective:   The effective capability set (unsigned 32bit int on all paltforms)
    permitted:   The permitted capability set (unsigned 32bit int on all paltforms)
    inheritable: The inheritable capability set (unsigned 32bit int on all paltforms)
    
    Notes:
    ------
    * On some platforms (older kernels) only one of these is required as CAP_LAST is smaller than a u32 
      (unsigned 32bit int), on newer kernels (those with Mandatory Access Control (MAC)) the capabilies
      exceed this and as such another cap_data structure is used to hold the upper bits and cap_data
      is then interpreted as a pointer to an array of a fixed size instead of a pointer to a cap_data
      structure
    """
    _fields_ = [('effective', ctypes.c_uint),
                ('permitted', ctypes.c_uint),
                ('inheritable', ctypes.c_uint),
                ]

class cap_header(ctypes.Structure):
    """"cap_user_header_t hdrp" from "linux/capability.h" used in conjunction with C call capset/capget
    
    Fields:
    -------
    version: Which API version to use, specifing a version unknwon to the kernel causes
             an EPERM error and this field in the structure passed to the syscall to be
             updated with the prefered version of the api the kernel wishes you to use
             LINUX_CAPABILITY_VERSIONS contains a list of known api versions and info
             about them             
    pid:     The PID of the process to retrive/set the capabilities of, setting this
             to 0 is the same as specifing the result of os.getpid()

    Notes:
    ------
    * The API version returned by the kernel does not start at 1 and count up but is semi random
    * Some API versions require more cap_data structures to be passed to them than others,
      LINUX_CAPABILITY_VERSIONS contains a mapping of version magic numbers to sane version naumbers
      and ammount of data_sections required as a 2 element tuple
    """
    _fields_ = [('version', ctypes.c_uint),
                ('pid', ctypes.c_int),
                ]

CAPABILITY_VERSION = 1
VERSION_MAGIC = 0
DATA_SECTIONS = 1
def _cap_error(val, func, args):
    """For the logic behind this command see "man capset" but dont trust it without testing
    the kernel likes to document it returns EINVAL when it returns EPERM instead
    
    
    logic here is not fully tested due to the complexity of producing error conditions, the code
    below is a best effort at 'marking up' the error information with additional information as to
    why the error occurred and what to look for but should not be considered exhaustive or correct
    """
    if val < 0:
        val = abs(val)
        if val == errno.EFAULT:
            raise ValueError("Header must be supplied, Data can only be null to determine version")
        elif val == errno.EINVAL:
            raise ValueError("One of the arguments is invalid, check the version of pid fields")
        elif val == errno.EPERM:
            if args[0].pid != 0:
                raise CapabilityError('You do not have the required capabilities (CAP_SETPCAP) to use this syscall')
            else:
                if DATA_SECTIONS == 1:
                    perms = args[1].effective | args[1].inheritable
                    allowed = args[1].permitted
                    mask = 0xFFFFFFFFFFFFFFFF
                    allowed = mask ^ allowed
                    capabilities = allowed & perms
                else:
                    cap_data_0 = args[1].contents[0]
                    cap_data_1 = args[1].contents[1]
                    perms_l = cap_data_0.effective | cap_data_0.inheritable
                    perms_u = cap_data_1.effective | cap_data_1.inheritable
                    perms = perms_u << 32 | perms_l
                    allowed_l = cap_data_0.permitted
                    allowed_u = cap_data_1.permitted
                    allowed = allowed_u << 32 | allowed_l
                    mask = 0xFFFFFFFFFFFFFFFF
                    allowed = mask ^ allowed
                    capabilities = allowed & perms
                if capabilities:
                    raise CapabilityError('Attempted to add a permission to the inherited/effective set that was not in the permitted set')
                else:
                    raise CapabilityError('An attempt was made to add a permission to the permitted set')
        elif val == errno.ESRCH:
            raise ValueError("No Such Thread: pid:%d", args[0].pid)            

# Get a minamal capget going, then autodetect which version
_capget = _libc.capget
_capget.argtypes = [ctypes.POINTER(cap_header), ctypes.POINTER(cap_data)]
_capget.restype = ctypes.c_int
_capget.errcheck = _cap_error

# Auto detect supported capabilities version
header = cap_header()
header.pid = 0
header.version = 0
data = cap_data()
try:
    ret = _capget(header, data)
except CapabilityError:
    # mask stupid C code mutate in place, overloaded errno shit mother functor
    ret = -1

# modify API of _capget with correct signature
try:
    if ret == -1:
        CAPABILITY_VERSION, DATA_SECTIONS = LINUX_CAPABILITY_VERSIONS[header.version]
        if DATA_SECTIONS == 2:
            _capget.argtypes = [ctypes.POINTER(cap_header), ctypes.POINTER(cap_data*2)]
        VERSION_MAGIC = header.version
    else:
        raise ValueError
except KeyError:
    log.warn("Unknown Linux Capability Version")
    raise APIError()
except ValueError:
    log.warn("Unexpected return value")
# posibly handy to have a way to work out which API version we are using
log.debug('Detected capability API version %d, uses %d data sections', CAPABILITY_VERSION, DATA_SECTIONS)
# cleanup
del header, data, ret

# set up _capset with correct cap_data from API info above
_capset = _libc.capset
if DATA_SECTIONS == 1:
    _capset.argtypes = [ctypes.POINTER(cap_header), ctypes.POINTER(cap_data)]
else:
    _capset.argtypes = [ctypes.POINTER(cap_header), ctypes.POINTER(cap_data*2)]
_capset.restype = ctypes.c_int
_capset.errcheck = _cap_error

if __name__ == "__main__":
    pass
