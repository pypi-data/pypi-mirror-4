#!/usr/bin/env python
"""support the mount syscalls"""

from ctypes import c_int, c_char_p, c_ulong, c_void_p
from asylum.syscall import _libc
import ctypes.util
import errno
import os

## mount flags ##
# Taken from /usr/include/linux/fs.h
MS_RDONLY = 0x00000001 # Mount the filesystem Read only
MS_NOSUID = 0x00000002 # disallow SUID binaries on this mount point
MS_NODEV = 0x00000004  # disallow device node creation/usage on this mount point
MS_NOEXEC = 0x00000008 # disallow execve of files on this mount point
MS_SYNC = MS_SYNCHRONOUS = 0x00000010 # all access is syncronous
MS_REMOUNT = 0x00000020 # remount the filesystem with updated options without unmounting it
MS_MANDLOCK = 0x00000040 # Permit Mandatry locks on this filesystem
MS_DIRSYNC = 0x00000080 # Make directory changes on this filesystem syncronous
MS_NOATIME = 0x00000400 # do not update atime of file access
MS_NODIRATIME = 0x00000800 # do not update atime on directory access
MS_BIND = 0x00001000 # perform a bind mount instead of a normal mount
MS_MOVE = 0x00002000 # move a mount to a new location without unmounting it
MS_REC = 0x00004000
MS_SILENT = MS_VERBOSE = 0x00008000 # no longer used
MS_POSIXACL = 0x00010000 # enable access control lists
MS_UNBINDABLE = 0x00020000 # ensure this directory cannot be used as the source of a bind mount
MS_PRIVATE = 0x00040000 # mark this mount as private (only visible to the current process)
MS_SLAVE = 0x00080000 # mark this as a slave mount (visible to a processes children)
MS_SHARED = 0x00100000 # mark this a a shared mount (any process can see a change in this mount)
MS_RELATIME = 0x00200000 # update atime under epcific circimstances
MS_KERNMOUNT = 0x00400000 # the mount point was mounted by kern_mount
MS_I_VERSION = 0x00800000 # update inode I_Version field
MS_STRICTATIME = 0x01000000 # always update atime when accessed
MS_NOSEC = 0x20000000
MS_ACTIVE = 0x40000000
MS_NOUSER = 0x80000000

# Taken from /usr/include/sys/mount.h, note linux/fs.h disagrees with the value below
MS_RMT_MASK = MS_RDONLY | MS_SYNC | MS_MANDLOCK | MS_NOATIME | MS_NODIRATIME
MS_MGC_VAL = 0xc0ed0000
MS_MGC_MASK = 0xffff0000

## Filesystems ##
filesystems = open("/proc/filesystems")
filesystems = [x.split()[-1] for x in filesystems]
TMPFS = "tmpfs"
SYSFS = "sysfs"
PROC = "proc"
CGROUP = "cgroup"

class UnknownErrno(Exception):
    """Do not trap this exception"""
    pass

## Mount syscall ##
def _mount_error(val, func, args):
    if val < 0:
        val = abs(val)
        if val == errno.EACCES:
            raise ValueError("Filesystem is RO but MS_RDONLY not specified or"
                                "source is on a filesystem with MS_NODEV or"
                                "path resolution failed")
        elif val == errno.EBUSY: 
            rdonly = args[3] & MS_RDONLY
            if rdonly:
                raise ValueError("A process has writable files open and MS_RDONLY was specified")
            else:
                raise ValueError("source is already mounted or target still busy")
        elif val == errno.EFAULT: 
            # this should never happen from python due to type checking
            raise ValueError("source, target, fs_type or fs_options does not point to a valid memory location")
        elif val == errno.EINVAL:
            remount = args[3] & MS_REMOUNT
            move = args[3] & MS_MOVE
            if remount:
                raise ValueError("MS_REMOUNT attempted but source was not already mounted on target")
            elif move:
                raise ValueError("MS_MOVE was attempted but source was not a mountpoint or was '/'")
            else:
                raise ValueError("source has an invalid superblock")
        elif val == errno.ELOOP:
            source = os.path.abspath(args[0])
            target = os.path.abspath(args[1])
            contains = os.path.commonprefix((source, target)) == source
            if contains:
                raise ValueError("Target is a descendent of source (destination is inside mount point)")
            else:
                raise ValueError("Too many links encountered during path resolution")
        elif val == errno.EMFILE: raise ValueError("Dummy device table full")
        elif val == errno.ENAMETOOLONG: raise ValueError("Path name was too long")
        elif val == errno.ENODEV: raise ValueError("Unknown filesystem type specified")
        elif val == errno.ENOENT: raise ValueError("Path does not exsist")
        elif val == errno.ENOMEM: raise ValueError("Not enough memory to perform mount")
        elif val == errno.ENOTBLK: raise ValueError("Source is not a block device")
        elif val == errno.ENOTDIR: raise ValueError("target or a prefix of srouce is not a directory")
        elif val == errno.ENXIO: raise ValueError("The major number of a block device is out of range")
        elif val == errno.EPERM: raise ValueError("Insufficent privileges")
        else:
            raise UnknownErrno("Unknown error code ({0}), please contact the devs".format(val))
    return val

_mount = _libc.mount
_mount.argtypes = (c_char_p, c_char_p, c_char_p, c_ulong, c_void_p)
_mount.rettype = c_int
_mount.errcheck = _mount_error

def mount(source, target, fs_type, flags=0, fs_options=""):
    """Thin wrapper around _mount designed to make fs_options optional
    
    Args:
    -----
    source (str):    The Source of the mount, this may be an arbitrary name for filesystems
                    with no backing object such as cgroups or tmpfs, a device file for
                    filessytems such as ext3 that require a block backing device, a file
                    or directory for a bind mount or a remote address in the form or
                    <ip>:<remote mount point> for NFSv3 and v4
    target (str):     The Target folder to mount the new filesystem on
    fstype (str):     The filesystem to mount, may be 'auto'/blank XXX FIXME XXX to automaticaly
                    determine the correct filesystem type
    flags (int):    Generic Filesystem flags that control the mounting, they are specified
                    in asylum.mount and start with MS_*, as this is a bitmask, all flags must 
                    be ORed together
    fs_options (str):     Options seperated by a "," that are decoded by the kernel, these are 
                        FS specifc and are passed by the /sbin/mount comand as the argument 
                        to -o
    Notes:
    ------
    * See 'man 2 mount' for extra information regarding fs_options
    
    """
    _mount(source, target, fs_type, flags, fs_options)

## Umount Flags ##
# Values taken from 'linux/fs.h'
MNT_FORCE = 0x01 # Force unmount even if busy.  This can cause data loss.  (Only for NFS mounts.)
MNT_DETACH = 0x02     # Perform a lazy unmount, make it unavalible to user processes and perform the
                    # unmount in the background as early as possible
MNT_EXPIRE = 0x04     # Mark a mount point as 'expired', a mount point stays 'expired' as long as no
                    # Process uses it, a second call with this flag performs an actual umount
UMOUNT_NOFOLLOW = 0x08 # Dont Follow a symlink when performing an umount operation

def _umount_error(val, func, args):
    if val < 0:
        val = abs(val)
        if val == errno.EAGAIN: raise ValueError("Filesystem sucseffuly marked as expired")
        elif val == errno.EBUSY: raise ValueError("Target could not be unmounted as it is busy")
        elif val == errno.EFAULT:
            # due to python typechecking on ctypes access this should not happen
            raise ValueError("Target points outside of valid memory")
        elif val == errno.EINVAL: 
            if not os.path.ismount(args[0]):
                raise ValueError("Target is not a mount point")
            else:
                raise ValueError("umount called with MNT_EXPIRE and (MNT_FORCE or MNT_DETACH)")
        elif val == errno.ENAMETOOLONG: raise ValueError("Path name too long")
        elif val == errno.ENOENT:
            if args[0] == "":
                raise ValueError("Please specify a mount directory")
            else:
                raise ValueError("The specified mount directory does not exist")
        elif val == errno.ENOMEM: raise ValueError("Not enough memory to perform an umount")
        elif val == errno.EPERM: raise ValueError("Insufficent privileges")
        else:
            raise UnknownErrno("Unknown error code ({0}), please contact the devs".format(val))
    return val

## Unmount syscall ##
_umount = _libc.umount2
_umount.argtypes = (c_char_p, c_int)
_umount.rettype = c_int
_umount.errcheck = _umount_error

def umount(target, flags=0):
    """A wrapper around _umount so flags does not need to be specified
    
    Args:
    -----
    target (str):    The directory to unmount
    flags (int):    a bitmask of flags to use to unmount the mount point
                    Relevent flags are in asylum.mount and start with 
                    MNT_*. as this is a bitmask, all values need to be
                    ORed together

    Notes:
    * see 'man 2 umount' for more information about flags
    * Calling umount with any flag MNT_* flag in addition to MNT_EXPIRE is invalid
      and will generate a ValueError
    * UNMOUNT_NOFOLLOW can be called with MNT_EXPIRE with no issues
    """
    _umount(target, flags)

if __name__ == "__main__":
    pass
