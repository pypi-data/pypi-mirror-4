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
"""Repositories for serialized data.

$Id: repository.py 73003 2007-03-06 10:34:19Z oestermeier $
"""
import copy
import os
import sys
import unicodedata

import zope.interface

import metadata
import interfaces
from fsutil import Error

unwanted = ("", os.curdir, os.pardir)

class Repository(object):
    """Represents a repository that uses filepaths.

    Possible examples are filesystems, SNARF-archives,
    zip-archives, svn-repository, etc.

    This base class also handles case insensitive filenames
    and provides methods to resolve ambiguities.
    """

    zope.interface.implements(interfaces.IRepository)

    chunk_size = 32768

    def __init__(self, case_insensitive=False, enforce_nfd=False, metadata=None):
        self.case_insensitive = case_insensitive
        self.enforce_nfd = enforce_nfd
        self.files = {}         # Keeps references to normalized filenames 
                                # which have been used
        self.disambiguated = {} # reserved disambiguated paths
        self.metadata = metadata

    def getMetadata(self):
        """Returns a metadata database.
        
        This implementation returns an empty database
        which reads the metadata on demand.
        """
        if self.metadata is None:
            return metadata.Metadata()
        return self.metadata

    def disambiguate(self, dirpath, name):
        """Disambiguates a name in a directory.
        
        Adds a number to the file and leaves the case untouched.
        """
        if self.case_insensitive or self.enforce_nfd:
            if self.enforce_nfd:
                dirpath = self._toNFD(dirpath)
                name = self._toNFD(name)
            disambiguated = self.disambiguated.setdefault(dirpath, set())
            dot = name.rfind('.')
            if dot >= 0:
                suffix = name[dot:]
                name = name[:dot]
            else:
                suffix = ''
            n = name + suffix
            normalized = self.normalize(n)
            i = 1
            while normalized in disambiguated:
                n = name + '-' + str(i) + suffix
                normalized = self.normalize(n)
                i += 1
            disambiguated.add(normalized)
            return n
        return name

    def dirname(self, path):
        """Returns the dirname."""
        return os.path.dirname(path)

    def join(self, path, *names):
        """Returns a joined path."""
        return os.path.join(path, *names)

    def _toNFD(self, name):
        """Helper to ensure NFD encoding.
                
        Linux and (most?) other Unix-like operating systems use the normalization
        form C (NFC) for UTF-8 encoding by default but do not enforce this.
        Darwin, the base of Macintosh OSX, enforces normalization form D (NFD),
        where a few characters are encoded in a different way.
        """
        if isinstance(name, unicode):
            name = unicodedata.normalize("NFD", name)
        elif sys.getfilesystemencoding() == 'utf-8':
            name = unicode(name, encoding='utf-8')
            name = unicodedata.normalize("NFD", name)
            name = name.encode('utf-8')
        return name

    def _toNFC(self, name):
        """Helper to ensure NFC encoding.
                
        Linux and (most?) other Unix-like operating systems use the normalization
        form C (NFC) for UTF-8 encoding by default but do not enforce this.
        Darwin, the base of Macintosh OSX, enforces normalization form D (NFD),
        where a few characters are encoded in a different way.
        """
        if isinstance(name, unicode):
            name = unicodedata.normalize("NFC", name)
        elif sys.getfilesystemencoding() == 'utf-8':
            name = unicode(name, encoding='utf-8')
            name = unicodedata.normalize("NFC", name)
            name = name.encode('utf-8')
        return name

    def normalize(self, name):
        """Normalize a filename.
        
        Uses lower case filenames if the repository is case sensitive.
        """
        if self.enforce_nfd:
            name = self._toNFD(name)
        if self.case_insensitive:
            name = name.lower()
        return name

    def encode(self, path, encoding=None):
        """Encodes a path in its normalized form.
        
        Uses the filesystem encoding as a default encoding. Assumes that the given path
        is also encoded in the filesystem encoding.
        """
        fsencoding = sys.getfilesystemencoding()
        if encoding is None:
            encoding = fsencoding
        if isinstance(path, unicode):
            return self.normalize(path).encode(encoding)
        return unicode(path, encoding=fsencoding).encode(encoding)

    def writeable(self, path):
        """Must be overwritten.
        """
        pass

    def readable(self, path):
        """Must be overwritten."""
        pass

    def readFile(self, path):
        """Convenient method for reading a whole file."""
        fp = self.readable(path)
        try:
            data = fp.read()
            return data
        finally:
            fp.close()

    def compare(self, readable1, readable2):
        if readable1 is None:
            return False
        if readable2 is None:
            return False
        try:
            for chunk in readable1.read(self.chunk_size):
                size = len(chunk)
                echo = readable2.read(size)
                if echo != chunk:
                    return False
            return True
        finally:
            readable1.close()
            readable1.close()


class FileSystemRepository(Repository):
    """A filesystem repository that keeps track of already written files."""

    zope.interface.implements(interfaces.IFileSystemRepository)

    def exists(self, path):
        """Returns a joined path."""
        return os.path.exists(path)

    def isdir(self, path):
        """Checks whether the path corresponds to a directory."""
        return os.path.isdir(path)

    def readable(self, path):
        """Returns a file like object that is open for read operations."""
        fp = self.files[path] = file(path, 'rb')
        return fp

    def writeable(self, path):
        """Returns a file like object that open for write operations.
        """
        dirname = self.dirname(path)
        self.ensuredir(dirname)
        fp = self.files[path] = file(path, 'wb')
        return fp

    def split(self, path):
        """Split a path, making sure that the tail returned is real."""
        head, tail = os.path.split(path)
        if tail in unwanted:
            newpath = os.path.normpath(path)
            head, tail = os.path.split(newpath)
        if tail in unwanted:
            newpath = os.path.realpath(path)
            head, tail = os.path.split(newpath)
            if head == newpath or tail in unwanted:
                raise Error("path '%s' is the filesystem root", path)
        if not head:
            head = os.curdir
        return head, tail

    def ensuredir(self, path):
        """Make sure that the given path is a directory, creating it if necessary.

        This may raise OSError if the creation operation fails.
        """
        if not os.path.isdir(path):
            os.makedirs(path)


class SnarfMetadata(metadata.Metadata):
    """A metadata implementation that reads the metadata from a SNARF archive."""
 
    def __init__(self, repository):
        super(SnarfMetadata, self).__init__()
        self.repository = repository
        if not repository.stream:
            return
        for path in repository.iterPaths():
            if path.endswith(repository.join('@@Zope', 'Entries.xml')):
                dm = metadata.DirectoryManager.__new__(metadata.DirectoryManager)
                dm.zdir = repository.dirname(path)
                dm.efile = path
                text = repository.readFile(path)
                dm.entries = metadata.load_entries(text)
                dm.originals = copy.deepcopy(dm.entries)
                key = repository.dirname(dm.zdir)
                self.cache[key] = dm              

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
        if dir not in self.cache:
            self.cache[dir] = metadata.DirectoryManager(dir)
        return self.cache[dir]


class SnarfReadable(object):
    """Mimics read access to a serialized SNARF file."""

    def __init__(self, repository, path):
        self.stream = repository.stream
        self.startpos = repository.readpos[path]
        self.size = repository.sizes[path]
        self.name = path

    def seek(self, offset, whence=0):
        if whence == 0:
            self.stream.seek(self.startpos + offset)
            return offset
        elif whence == 1:
            return self.seek(self.tell() + offset)
        elif whence == 2:
            return self.seek(self.size + offset)

    def tell(self):
        return self.stream.tell() - self.startpos

    def readline(self):
        self.stream.readline()

    def read(self, bytes=None):
        if bytes is None or bytes is -1:
            rest = self.size - self.tell()
            return self.stream.read(rest)
        rest = self.size - self.tell()
        if bytes > rest:
           return self.stream.read(rest)
        return self.stream.read(bytes)

    def close(self):
        pass


class SnarfWriteable(object):
    """Mimics write access to a SNARF archive."""

    def __init__(self, repository, path, pos):
        stream = self.stream = repository.stream
        self.name = path
        self.pos = pos              # pos of dummy length
        self.start = stream.tell()
        self.format = repository.len_format

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def close(self):
        self.stream.flush()
        pos = self.stream.tell()
        size = pos - self.start
        self.stream.seek(self.pos)
        self.stream.write(self.format % size)
        self.stream.seek(pos)


class SnarfRepository(FileSystemRepository):
    """A SNARF repository that stores a directory tree in a single archive."""

    zope.interface.implements(interfaces.IArchiveRepository)

    len_format = '%08d' # format of file length indicator

    def __init__(self, stream, case_insensitive=False, enforce_nfd=False):
        super(SnarfRepository, self).__init__(case_insensitive=case_insensitive,
                                                 enforce_nfd=enforce_nfd)
        self.stream = stream
        self.readpos = {}
        self.sizes = {}
        self.directories = set()

    def getMetadata(self):
        """Returns a special metadata database which reads directly 
        from the SNARF archive."""
        return SnarfMetadata(self)

    def isdir(self, path):
        """Returns True iff the path matches a directory name.
        
        Since SNARF refers only implicitely to dirnames all filenames
        are scanned in the worst case.
        """
        if path in self.files or path in self.readpos:
            return False
        return path in self.directories

    def ensuredir(self, path):
        """Does nothing since a snarf treats directories implicitely."""
        pass

    def split(self, path):
        return os.path.split(path)
        
    def writeable(self, path):
        """Returns a file like object that is open for write operations.
        
        Writes a dummy length indicator and a path. The returned
        SnarfWriteable overwrites the length indicator on close.
        """
        pos = self.stream.tell()
        dummy = self.len_format % 0
        self.stream.write("%s %s\n" % (dummy, path.encode('utf-8')))
        fp = self.files[path] = SnarfWriteable(self, path, pos)
        return fp

    def readable(self, path):
        fp = self.files[path] = SnarfReadable(self, path)
        fp.seek(0)
        return fp

    def exists(self, path):
        if not self.readpos:
            self._scan()
        return path in self.readpos or path in self.directories

    def iterPaths(self):
        if not self.readpos:
            self._scan()
        return self.readpos.iterkeys()

    def readFile(self, path):
        self.stream.seek(self.readpos[path])
        return self.stream.read(self.sizes[path])

    def _scan(self):
        """Scans the archive and reads all positions of files into a cache."""

        self.stream.seek(0)
        self.readpos = {}
        pos = 0
        while True:
            infoline = self.stream.readline()
            if not infoline:
                break
            if not infoline.endswith("\n"):
                raise IOError("incomplete info line %r" % infoline)
            offset = len(infoline)
            infoline = infoline[:-1]
            sizestr, path = infoline.split(" ", 1)
            size = int(sizestr)
            self.sizes[path] = size
            pos = self.readpos[path] = pos + offset
            self.directories.add(self.dirname(path))
            pos += size
            self.stream.seek(pos)        
