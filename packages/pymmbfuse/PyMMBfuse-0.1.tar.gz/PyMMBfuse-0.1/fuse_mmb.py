#!/usr/bin/python
#===============================================================================
# Copyright (C) 2012 Adrian Hungate
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#===============================================================================
"""
This file is part of PyMMB - The crossplatform MMB library and toolset
If you don't use MMC Flash cards in a BBC Microcomputer, this is unlikely
to be a lot of use to you!
"""

import errno
import sys
import time
import math
import stat
import getopt
import fuse
import PyMMB

author = "Adrian Hungate <adrian@haqa.co.uk>"
version = 0.1
license = "Apache License, Version 2.0"

class _internal_dfs_file(PyMMB.dfs.dfs_file):
    """
    Subclass of dfs_file to replace characters in filenames which are illegal
    under Unix etc.
    """
    @property
    def fullname(self):
        """
        Replace some illegal characters
        """
        name = "%s.%s" % (self._dir, self._name,)
        return name.replace("/", "_").replace("'", "_").replace('"', "_")

class _internal_dfs(PyMMB.dfs.dfs):
    """
    Use _internal_dfs_file instead of dfs_file, and replace characters
    in titles which are illegal in filenames under Unix etc
    """
    def __init__(self, filename = None):
        """
        Set up using _internal_dfs_file instead
        """
        self._files = [_internal_dfs_file(self) for i in range(31)]
        if filename != None:
            self.open_file(filename)

    @property
    def fullname(self):
        """
        Replace some illegal characters
        """
        return self.title.replace("/", "_").replace("'", "_").replace('"', "_")

    def find_fullname(self, filename):
        """
        Match using fullname
        """
        filename = filename.upper()
        for file_entry in self.files:
            if file_entry.fullname.upper() == filename.upper():
                return file_entry
        raise PyMMB.dfs.FileNotFoundException("File Not Found: %s", (filename))

class _internal_disc(_internal_dfs, PyMMB.mmb.disc):
    """
    Use _internal_dfs instead of dfs
    """
    def __init__(self, did, mmb, title = "", status = 0xFF):
        """
        Setup using _internal_dfs instead
        """
        _internal_dfs.__init__(self)
        self._mmb = mmb
        self._id = did
        self.title = title
        self.status = status

class _internal_mmb(PyMMB.mmb.mmb):
    """
    Use _internal_disc instead of disc
    """
    def __init__(self, filename = None):
        """
        Setup using _internal_disc instead
        """
        self.drives = [0, 1, 2, 3]
        self.discs = [_internal_disc(did, self) for did in range(PyMMB.mmb.MAXDISCS)]
        if filename != None:
            self.open_file(filename)

class fuse_dfs(fuse.LoggingMixIn, fuse.Operations):
    """
    A fuse operations class to handle mounting DFS images
    """
    dfs = None

    def __init__(self, image):
        """
        Open the DFS image and get ready to use it
        """
        try:
            if image is not None and isinstance(image, _internal_dfs):
                self.dfs = image
            else:
                self.dfs = _internal_dfs(image)
        except IOError:
            print "Failed to create fuse_dfs"
            raise fuse.FuseOSError(errno.ENOENT)

    def getattr(self, path, fh = None):
        """
        Stat a file
        """
        entry = self.__find__(path)
        uid, gid, pid = fuse.fuse_get_context()
        st = {
            'st_mode'   :   (
                stat.S_IRUSR |
                stat.S_IRGRP |
                stat.S_IROTH
            ),
            'st_nlink'  :   1,
            'st_size'   :   0,
            'st_uid'    :   uid,
            'st_gid'    :   gid,
            'st_ctime'  :   time.time(),
            'st_mtime'  :   time.time(),
            'st_atime'  :   time.time()
        }
        if isinstance(entry, _internal_dfs):
            st['st_mode'] = st['st_mode'] | stat.S_IFDIR | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            st['st_size'] = entry.sectors * 256
            st['st_nlink'] = entry.fileCount + 2
        elif isinstance(entry, _internal_dfs_file):
            st['st_mode'] = st['st_mode'] | stat.S_IFREG
            if not entry.locked:
                st['st_mode'] = st['st_mode'] | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            st['st_size'] = entry.length
        else:
            print "WAAAA - I got an unexpected object type!! %s" % (str(entry),)
            raise fuse.FuseOSError(errno.EINVAL)
        return st

    def readdir(self, path, fh):
        entry = self.__find__(path)
        files = ['.', '..']
        if isinstance(entry, _internal_dfs):
            for dfs_file in entry.files:
                files.append(dfs_file.fullname)
        else:
            raise fuse.FuseOSError(errno.ENOTDIR)
        return files

    def read(self, path, size, offset, fh):
        entry = self.__find__(path)
        if not isinstance(entry, _internal_dfs_file):
            raise fuse.FuseOSError(errno.EINVAL)
        return entry.read()[offset:offset + size]

    def chmod(self, path, mode):
        entry = self.__find__(path)
        if not hasattr(entry, "locked"):
            raise fuse.FuseOSError(errno.EINVAL)
        locked = (mode & stat.S_IWUSR) == stat.S_IWUSR
        entry.locked = not locked
        entry._dfs.write_catalog()
        return 0

    def chown(self, path, uid, gid):
        entry = self.__find__(path)

    def unlink(self, path):
        entry = self.__find__(path)
        if not hasattr(entry, "locked"):
            raise fuse.FuseOSError(errno.EINVAL)
        try:
            entry._dfs.delete_file(entry.dir, entry.name)
        except:
            raise fuse.FuseOSError(errno.EPERM)

    def mkdir(self, path, mode):
        raise fuse.FuseOSError(errno.EINVAL)

    def create(self, path, mode, fi = None):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            try:
                dir, name = name.split(".")
            except:
                dir = ""
            if len(dir) != 1 or len(name) == 0 or len(name) > 7:
                raise fuse.FuseOSError(errno.EINVAL)
            parent.create_file(dir, name, "")
            return 0
        raise fuse.FuseOSError(errno.ENOENT)

    def truncate(self, path, length, fh = None):
        entry = self.__find__(path)
        if length > entry.length:
            entry._dfs.create_file(entry.dir, entry.name, "\0" * length)
        else:
            entry.length = length
            entry._dfs.write_catalog()

    def write(self, path, data, offset, fh):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            try:
                dir, name = name.split(".")
            except:
                dir = ""
            if len(dir) != 1 or len(name) == 0 or len(name) > 7:
                raise fuse.FuseOSError(errno.EINVAL)
            try:
                obj = self.__find__(path)
                olddata = obj.read()
            except:
                olddata = "\0" * (offset + len(data))
            newdata = olddata[0:offset] + data + olddata[offset + len(data):]
            parent.create_file(dir, name, newdata)
            return len(data)
        raise fuse.FuseOSError(errno.ENOENT)

    def rename(self, old, new):
        entry = self.__find__(old)
        try:
            newentry = self.__find__(new)
            raise fuse.FuseOSError(errno.EEXIST)
        except:
            pass
        p1, n1 = self.__find_parent__(old)
        p2, n2 = self.__find_parent__(new)
        if p1 != p2:
            raise fuse.FuseOSError(errno.EINVAL)
        try:
            dir, name = n2.split(".")
        except:
            dir = ""
            name = n2
        if len(dir) != 1 or len(name) == 0 or len(name) > 7:
            raise fuse.FuseOSError(errno.EINVAL)
        entry.dir = dir
        entry.name = name
        p1.write_catalog()

    def statfs(self, path):
        """Returns a dictionary with keys identical to the statvfs C
           structure of statvfs(3).

           On Mac OS X f_bsize and f_frsize must be a power of 2
           (minimum 512)."""
        maxfiles = 0  # Number of existant discs * 31
        files = 0  # Number of files
        size = 0  # Size of files on discs (In blocks)
        space = 0  # Total number of blocks on discs
        space = self.dfs.sectors
        maxfiles = 31
        files = self.dfs.fileCount
        for file in self.dfs.files:
            size = size + int(math.ceil(file.length / 256))
        statvfs = {
            'f_bsize'   :   256,
            'f_frsize'  :   256,
            'f_blocks'  :   space,
            'f_bfree'   :   space - size,
            'f_bavail'  :   space - size,
            'f_files'   :   maxfiles,
            'f_ffree'   :   maxfiles - files,
            'f_favail'  :   maxfiles - files
        }
        return statvfs

    def __find_parent__(self, path):
        """
        Given a path, return the mmb or disc containing the target, and the basename
        """
        # Split the path so we can see what we are dealing with
        elements = path.split("/")
        # Remove any empty elements.
        elements = filter(lambda x: x != "", elements)
        # Special case for root directory
        if elements == []:
            raise fuse.FuseOSError(errno.EINVAL)
        return (self.__find__("/".join(elements[:-1])), elements[-1])

    def __find__(self, path):
        """
        Given a path return the file object representing it, or None
        """
        print "FIND: %s" % (path,)
        # Split the path so we can see what we are dealing with
        elements = path.split("/")
        # Remove any empty elements.
        elements = filter(lambda x: x != "", elements)
        # Special case for root directory
        if elements == []:
            return self.dfs
        try:
            entry = self.dfs.find_fullname(elements[0])
        except:
            raise fuse.FuseOSError(errno.ENOENT)
        return entry

class fuse_mmb(fuse.LoggingMixIn, fuse.Operations):
    """
    A fuse operations class to handle mounting MMB images
    """
    mmb = None

    def __init__(self, image):
        """
        Open the MMB image and get ready to use it
        """
        try:
            if image is not None and isinstance(image, _internal_mmb):
                self.mmb = image
            else:
                self.mmb = _internal_mmb(image)
        except IOError:
            raise fuse.FuseOSError(errno.ENOENT)

    def getattr(self, path, fh = None):
        """
        Stat a folder or file (delegated)
        """
        entry = self.__find__(path)
        uid, gid, pid = fuse.fuse_get_context()
        if isinstance(entry, _internal_dfs_file):
            dfs_operations = fuse_dfs(entry._dfs)
            return dfs_operations.getattr(entry.fullname, fh)
        st = {
            'st_mode'   :   (
                stat.S_IFDIR |
                stat.S_IRUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IXOTH
            ),
            'st_nlink'  :   0,
            'st_size'   :   0,
            'st_uid'    :   uid,
            'st_gid'    :   gid,
            'st_ctime'  :   time.time(),
            'st_mtime'  :   time.time(),
            'st_atime'  :   time.time()
        }
        if isinstance(entry, _internal_disc):
            if not entry.locked:
                st['st_mode'] = st['st_mode'] | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            st['st_size'] = entry.sectors * 256
            st['st_nlink'] = entry.fileCount + 2
        elif isinstance(entry, _internal_mmb):
            cnt = 0
            size = 0
            for disc in entry.discs:
                if disc.exists:
                    size = size + (800 * 256)
                    if disc.formatted:
                        cnt = cnt + 1
            st['st_nlink'] = cnt
            st['st_size'] = size
        else:
            print "WAAAA - I got an unexpected object type!! %s" % (str(entry),)
            raise fuse.FuseOSError(errno.EINVAL)
        return st

    def readdir(self, path, fh):
        entry = self.__find__(path)
        files = ['.', '..']
        if isinstance(entry, PyMMB.mmb.mmb):
            for disc in entry.discs:
                if disc.exists and disc.formatted:
                    if disc.title == "":
                        disc.title = "XXX"
                    files.append(disc.title)
        elif isinstance(entry, PyMMB.dfs.dfs):
            dfs_operations = fuse_dfs(entry)
            return dfs_operations.readdir("/", fh)
        else:
            raise fuse.FuseOSError(errno.ENOTDIR)
        return files

    def chmod(self, path, mode):
        print "mmb chmod %s %04o" % (path, mode,)
        entry = self.__find__(path)
        if isinstance(entry, _internal_dfs_file):
            dfs_operations = fuse_dfs(entry._dfs)
            return dfs_operations.chmod(entry.fullname, mode)
        if not hasattr(entry, "locked"):
            raise fuse.FuseOSError(errno.EINVAL)
        locked = (mode & stat.S_IWUSR) == stat.S_IWUSR
        entry.locked = not locked
        entry._mmb.write_catalog()

    def chown(self, path, uid, gid):
        entry = self.__find__(path)

    def create(self, path, mode, fi = None):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            dfs_operations = fuse_dfs(parent)
            return dfs_operations.create(name, mode)
        raise fuse.FuseOSError(errno.EINVAL)

    def truncate(self, path, length, fh = None):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            dfs_operations = fuse_dfs(parent)
            return dfs_operations.truncate(name, length, fh)
        raise fuse.FuseOSError(errno.EINVAL)

    def write(self, path, data, offset, fh):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            dfs_operations = fuse_dfs(parent)
            return dfs_operations.write(name, data, offset, fh)
        raise fuse.FuseOSError(errno.EINVAL)

    def read(self, path, size, offset, fh):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            dfs_operations = fuse_dfs(parent)
            return dfs_operations.read(name, size, offset, fh)
        raise fuse.FuseOSError(errno.EINVAL)

    def unlink(self, path):
        parent, name = self.__find_parent__(path)
        if isinstance(parent, _internal_dfs):
            dfs_operations = fuse_dfs(parent)
            return dfs_operations.unlink(name)
        raise fuse.FuseOSError(errno.EINVAL)

    def mkdir(self, path, mode):
        parent, name = self.__find_parent__(path)
        if not isinstance(parent, _internal_mmb):
            raise fuse.FuseOSError(errno.EINVAL)
        try:
            parent.find_empty_disc().format(name)
            parent.write_catalog()
        except PyMMB.dfs.DiscFullException:
            raise fuse.FuseOSError(errno.ENOSPC)

    def rmdir(self, path):
        entry = self.__find__(path)
        if not isinstance(entry, _internal_disc):
            raise fuse.FuseOSError(errno.EINVAL)
        if entry.fileCount != 0:
            raise fuse.FuseOSError(errno.ENOTEMPTY)
        try:
            entry.unformat()
        except:
            raise fuse.FuseOSError(errno.EPERM)

    def rename(self, old, new):
        entry = self.__find__(old)
        try:
            newentry = self.__find__(old)
            raise fuse.FuseOSError(errno.EEXIST)
        except:
            pass
        p1, n1 = self.__find_parent__(old)
        p2, n2 = self.__find_parent__(new)
        if p1 != p2:
            raise fuse.FuseOSError(errno.EINVAL)
        if isinstance(p1, _internal_dfs):
            dfs_operations = fuse_dfs(p1)
            return dfs_operations.rename(n1, n2)
        entry.title = n1
        entry.write_catalog()
        p1.write_catalog()

    def statfs(self, path):
        """Returns a dictionary with keys identical to the statvfs C
           structure of statvfs(3).

           On Mac OS X f_bsize and f_frsize must be a power of 2
           (minimum 512)."""
        maxfiles = 0  # Number of existant discs * 31
        files = 0  # Number of files
        size = 0  # Size of files on discs (In blocks)
        space = 0  # Total number of blocks on discs
        for did in range(PyMMB.mmb.MAXDISCS):
            disc = self.mmb.discs[did]
            if disc.exists:
                space = space + disc.sectors
                if disc.formatted:
                    maxfiles = maxfiles + 31
                    files = files + disc.fileCount
                    for entry in disc.files:
                        size = size + int(math.ceil(entry.length / 256))
        statvfs = {
            'f_bsize'   :   256,
            'f_frsize'  :   256,
            'f_blocks'  :   space,
            'f_bfree'   :   space - size,
            'f_bavail'  :   space - size,
            'f_files'   :   maxfiles,
            'f_ffree'   :   maxfiles - files,
            'f_favail'  :   maxfiles - files
        }
        return statvfs

    def __find_parent__(self, path):
        """
        Given a path, return the mmb or disc containing the target, and the basename
        """
        # Split the path so we can see what we are dealing with
        elements = path.split("/")
        # Remove any empty elements.
        elements = filter(lambda x: x != "", elements)
        # Special case for root directory
        if elements == []:
            raise fuse.FuseOSError(errno.EINVAL)
        return (self.__find__("/".join(elements[:-1])), elements[-1])

    def __find__(self, path):
        """
        Given a path return the mmb, disc, or file object representing it, or None
        """
        # Split the path so we can see what we are dealing with
        elements = path.split("/")
        # Remove any empty elements.
        elements = filter(lambda x: x != "", elements)
        # Special case for root directory
        if elements == []:
            return self.mmb
        elif len(elements) > 2:
            raise fuse.FuseOSError(errno.ENOENT)
        try:
            disc = self.mmb.find_disc(elements[0])
        except:
            raise fuse.FuseOSError(errno.ENOENT)
        if len(elements) == 1:
            return disc
        dfs_operations = fuse_dfs(disc)
        return dfs_operations.__find__(elements[1])


if __name__ == "__main__":
    syntax = False
    usage = False
    mmb = None
    dfs = None
    foreground = False
    debug = False
    nothreads = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:m:fhDn", ["dfs=", "mmb=", "foreground", "help", "debug", "nothreads"])
        if len(args) != 1:
            syntax = True
        for opt in opts:
            if opt[0] == '-m' or opt[0] == '--mmb':
                mmb = opt[1]
            elif opt[0] == '-d' or opt[0] == '--dfs':
                dfs = opt[1]
            elif opt[0] == '-h' or opt[0] == '--help':
                syntax = True
                usage = True
            elif opt[0] == '-f' or opt[0] == '--foreground':
                forground = True
            elif opt[0] == '-D' or opt[0] == '--debug':
                debug = True
            elif opt[0] == '-n' or opt[0] == '--nothreads':
                nothreads = True
        if (mmb == None and dfs == None) or (mmb != None and dfs != None):
            syntax = True
    except:
        syntax = True
    if syntax:
        print "Usage: %s <options> <mountpoint>" % (sys.argv[0],)
        if usage:
            print """
Options:
    -d <image>    --dfs <image>    Mount a DFS image
    -m <image>    --mmb <image>    Mount an MMB image
    -f            --foreground     Keep the process in the foreground
    -D            --debug          Output debugging messages
    -n            --nothreads      Run the fuse process in a single thread
    -h            --help           Print this help

You may choose only one of --dfs and --mmb (Only one type of image may be
mounted by a single command).
"""
        sys.exit(-1)
    if dfs:
        print "Mounting DFS image '%s' at '%s'" % (dfs, args[0],)
        fuse.FUSE(fuse_dfs(dfs), args[0], foreground = foreground, debug = debug, nothreads = nothreads, fsname = 'DFS:' + dfs)
    elif mmb:
        print "Mounting MMB image '%s' at '%s'" % (mmb, args[0],)
        fuse.FUSE(fuse_mmb(mmb), args[0], foreground = foreground, debug = debug, nothreads = nothreads, fsname = 'MMB:' + mmb)
#    root_time = time.time()
#    if hasattr(self, "mmb") and self.mmb is not None:
#        try:
#            self.fuse_args.optdict['fsname'] = "MMB:" + self.mmb
#            self.mmb = PyMMB.mmb.mmb(self.mmb)
#        except IOError:
#            raise MMB_Error, "Failed to open the. MMB image file specified"
#    elif hasattr(self, "dfs") and self.dfs is not None:
#        try:
#            self.fuse_args.optdict['fsname'] = "DFS:" + self.dfs
#            self.dfs = PyMMB.dfs.dfs(self.dfs)
#        except IOError:
#            raise MMB_Error, "Failed to open the DFS image file specified"
#    return fuse.Fuse.main(self)
