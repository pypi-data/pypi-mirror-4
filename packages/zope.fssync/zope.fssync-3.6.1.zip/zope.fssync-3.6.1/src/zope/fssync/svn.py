##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A subversion repository for serialized data.

$Id: svn.py 73003 2007-03-06 10:34:19Z oestermeier $
"""

import shutil
import zope.interface
import os.path
import py.path

import repository
import metadata
import interfaces
import task

class VersionControlRepository(repository.FileSystemRepository):
    """Version Control Repository.

    (hopefully) version control system agnostic.
    """
    zope.interface.implements(interfaces.IVersionControlRepository)
    
    def __init__(self):
        super(VersionControlRepository, self).__init__()
        self.clear()

    def sync(self, object, message=''):
        self.save(object)
        self.up()
        self.resolve()
        self.load(object)
        self.commit(message)

    def clear(self):
        self._added_by_save = []
        self._deleted_by_save = []
        
    def up(self):
        raise NotImplementedError

    def resolve(self):
        raise NotImplementedError

    def commit(self, message):
        raise NotImplementedError


class SVNChanges(object):
    """A collector for changes in a SVN repository."""
    
    def __init__(self, before, after):
        self.added = sorted(after - before)
        self.deleted = sorted(before - after)
        
    def accept(self):
        for path in self.deleted:
            if path.check(versioned=True):
                path.remove()
            if path.check():
                shutil.rmtree(str(path))


class SVNDirectoryManager(metadata.DirectoryManager):
    """Keeps fssync metadata of objects under version control."""
    
    def __init__(self, wcpath):
        self.entries = {}
        for path in wcpath.listdir():
            if path.check(versioned=True):
                self.entries[path.basename] = dict(name=path.basename)

    def getentry(self, name):
        if name not in self.entries:
            return dict(name=name, flag='removed')
        return self.entries.get(name, {})


class SVNMetadata(metadata.Metadata):
    """Reads the metadata from a SVN repository."""

    def __init__(self, repository):
        super(SVNMetadata, self).__init__()
        self.repository = repository

    def getentry(self, file):
        """Return the metadata entry for a given file (or directory).

        Modifying the dict that is returned will cause the changes to
        the metadata to be written out when flush() is called.  If
        there is no metadata entry for the file, return a new empty
        dict, modifications to which will also be flushed.
        """
        dir, base = self.repository.split(file)
        return self.getmanager(dir).getentry(base)

    def getmanager(self, dir):
        dir = self.repository.fullpath(dir)
        if dir not in self.cache:
            self.cache[dir] = SVNDirectoryManager(dir)
        return self.cache[dir]


class SVNRepository(VersionControlRepository):
    """A subversion repository."""

    zope.interface.implements(interfaces.ISVNRepository)

    debug = False
    
    def __init__(self, path):
        self.svnwc = py.path.svnwc(path)
        allpaths = self.svnwc.visit(rec=True)
        self.before = set(allpaths)
        self.after = set(allpaths)
        super(SVNRepository, self).__init__()

    def up(self):
        self.svnwc.update()

    def fullpath(self, relpath):
        return self.svnwc.join(relpath)
        
    def getMetadata(self):
        """Returns a special metadata database which reads directly 
        from the SVN repository."""
        return SVNMetadata(self)

    def clear(self):
        super(SVNRepository, self).clear()
        self.before = self.after
        self.after = set()
        
    def changes(self):
        return SVNChanges(self.before, self.after)
        
    def isdir(self, path):
        return self.svnwc.join(path).check(dir=True)
    
    def split(self, path):
        if isinstance(path, str):
            return os.path.split(path)
        return path.dirpath(), path.basename
        
    def ensuredir(self, path):
        dir = self.svnwc.ensure(path, directory=True)
        self.after.add(dir)
        return dir
        
    def readable(self, path):
        """Returns a file like object that is open for read operations."""
        realpath = self.svnwc.join(path)
        fp = self.files[path] = realpath.open('rb')
        return fp

    def writeable(self, path):
        """Returns a file like object that is open for write operations.
        
        XXX: Ignores all files with @@ at the moment. These files
        should not be generated at all.
        
        """
        if '@@' in path:
            class DummyStream(object):
                def write(self, data):
                    pass
                def close(self):
                    pass
            return DummyStream()
            
        wcpath = self.svnwc.join(path)
        self.svnwc.ensure(path)
        fp = self.files[path] = wcpath.open('wb')
        while len(str(wcpath)) > len(str(self.svnwc)):
            self.after.add(wcpath)
            wcpath = wcpath.dirpath()
        return fp


class SVNSyncTask(task.SyncTask):
    """A sync task that performs a complete update cycle."""
 
    def resolve(self):
        pass
        
    def commit(self, message):
        self.repository.commit(message)

    def perform(self, container, name, message=''):

        self.repository.debug = True
        
        export = task.Checkout(self.getSynchronizer, self.repository)
        export.perform(container[name], name)

        self.repository.up()

        load = task.Commit(self.getSynchronizer, self.repository)
        load.debug = True
        load.perform(container, name, name)



