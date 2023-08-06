#!/usr/bin/env python
"""cgroups: utils for managing a cgroups, a resrouce managment feature of linux"""
import logging
import os

log = logging.getLogger('asylum.cgroups')

# The seperator between cgroup children and parents, same as os.path.sep
cgroup_sep = '.'

class ContainsCgroups(Exception):
    """The specified cgroup ({0}) contains children cgroups/processes and cannot be deleted"""
    def __init__(self, cgroup):
        self.cgroup = cgroup
        
    def __str__(self):
        return self.__doc__.format(self.cgroup)
        
class CGroupMount(object):
    def __init__(self, path, label=None):
        """CGroup: represents a mounted cgroup hireachy
        
        Args:
        -----
        path:   the basepath of the cgroup mount, all cgroups are relative to this
                point
        label:  The label of the mountpoint that this cgroup controls (mainly used for
                identifcation in debugging where there are multiple cgroup mount points)
        """
        self.basepath = os.path.abspath(path)
        self.label = label
    
        # get the inital set of cgroups
        self.refresh()
    
    def refresh(self):
        """refresh: Retrive the current cgrups and update our cache
        """
        cgroups = {}
        walker = os.walk(self.basepath)
        for path, dirs, files in walker: 
            path = os.path.abspath(path)
            path = path[len(self.basepath):].strip("/")
            path = path.replace(os.path.sep, cgroup_sep)
            cgroups[path] = CGroup(self.basepath, path, files, self.label)
        self.cgroups = cgroups
        self.cgroup_attributes = files
        
    def list(self):
        """List all cgroups in our cache
        """
        return self.cgroups.keys()
    
    def create(self, name, perm=0o750):
        """create: create a new cgroup
        
        Args:
        -----
        name:    The name of the cgroup, "."'s get covnerted to path seperators
        perm:    The permssions to create the cgroup subgroup with, the default is 750 (unix permissions)
        """
        path = name.replace(cgroup_sep, os.path.sep)
        path = os.path.join(self.basepath, path)
        try:
            os.mkdir(path, perm)
        except OSError, err:
            # if it exsits then we can just continue on
            if err.errno == 17:
                pass
            else:
                raise
    
        cgroup = CGroup(self.basepath, name, self.cgroup_attributes, self.label)
        self.cgroups[name] = cgroup

    def __iter__(self):
        return self.cgroups.iteritems()
        
    def __getitem__(self, key):
        return self.cgroups[key]
        
#    use create() instead        
#    def __setitem__(self, key, val):
#        self.cgroups[key] = val
        
    def __delitem__(self, key):
        # if it exsists, we can kill it</predetor>
        self.cgroups[key].remove()
        del self.cgroups[key]

class CGroup(object):
    def __init__(self, basepath, group, attributes, label=None):
        object.__setattr__(self, 'basepath', basepath)
        object.__setattr__(self, 'group', group)
        object.__setattr__(self, 'attributes', attributes)
        object.__setattr__(self, 'label', label)
        
    def get_path(self, attr):
        path = self.group.replace('.', '/')
        return os.path.join(self.basepath, path, attr)
    
    def remove(self):
        """Remove ourselves from the cgroup"""
        try:
            os.rmdir(self.get_path(''))
        except OSError, err:
            if err.errno == 16:
                raise ContainsCgroups(self.group)
            else:
                raise
        
    def __getattr__(self, key):
        if key in self.attributes:
            path = self.get_path(key)
            with open(path) as attr:
                return attr.read()
        else:
            raise AttributeError("CGroup object '{0}' has no attribute '{1}'".format(self, key))

    def __setattr__(self, key, val):
        if key in self.attributes:
            path = self.get_path(key)
            with open(path, 'w') as attr:
                attr.write(val)
        else:
            raise AttributeError("CGroup object '{0}' has no attribute '{1}'".format(self, key))

    def __repr__(self):
        if self.label is not None:
            return "<CGroup: {0}:{1}>".format(self.label, self.group)
        else:
            return "<CGroup: {0}>".format(self.group)

def get_cgroup_mounts():
    subsystems = []
    with open('/proc/cgroups') as cgroups:
        for line in cgroups:
            line = line.strip()
            if line.startswith("#"):
                continue
            line = line.split()
            subsystems.append(line[0])

    cgroups = []
    with open('/proc/mounts') as mounts:
        for line in mounts:
            line = line.split()
            if line[2] == 'cgroup':
                label = line[0]
                mount_point = line[1]
                mount_args = line[3].split(',')
                # make sure we only include valid cgroup types and not other mount flags
                cgroup_types = [x for x in mount_args if x in subsystems]
                cgroups.append((label, mount_point, cgroup_types))
    
    return cgroups

if __name__ == "__main__":
    cgroups = get_cgroup_mounts()
    width = max([len(x[0]) for x in cgroups]) + 1
    print 'CGroups:'
    print '----------------------------------------------'
    for cgroup in cgroups:
        label = cgroup[0]
        mount = cgroup[1]
        system = ",".join(cgroup[2])
        print "{0:>{width}}: {1} ({2})".format(label, mount, system, width=width)

    print('\n')
            
    cgroups = [CGroupMount(x[1], x[0]) for x in cgroups]
    
    for cgroup in cgroups:
        print "CGroup: {0} ({1})".format(cgroup.label, cgroup.basepath)
        print '----------------------------------------------'
        for name, group in cgroup:
            print "* {0}".format(group.group)
        print

    # try and read a cgroup attribute for testing
    print "Testing attribute access:"
    print "cgroup: {0}:{1}({2})".format(group.label, group.group, group.basepath)
    print group.tasks.strip().split('\n')

    # try and create a cgroup for testing
    print "Creating Asylum cgroup"
    cgroup.create('asylum')
    print "Creating Asylum.base cgroup"
    cgroup.create('asylum.base')

    print "Deleting Asylum cgroup with children"
    try:
        del cgroup['asylum']
    except ContainsCgroups:
        pass
    else:
        raise AssertionError("We were able to delete a root cgroup that contained children")
        
    print 'adding outselves to the base cgroup'
    cgroup['asylum'].tasks = str(os.getpid())
    print 'moving process to root cgroup'
    cgroup[''].tasks = str(os.getpid())

    print "Deleting Asylum.base cgroup"
    del cgroup['asylum.base']
    print "Deleting Asylum cgroup"
    del cgroup['asylum']
    
    print "All tests pass, manual cleanup may be required"
