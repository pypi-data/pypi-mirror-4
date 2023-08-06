##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Simple New ARchival Format (SNARF).

This is for transferring collections of files over HTTP where the key
need is for simple software.

The format is dead simple: each file is represented by the string

    '<size> <pathname>\n'

followed by exactly <size> bytes.  Directories are represented by
paths that end in / and have a zero size. The root directory has a
blank path.

Pathnames are always relative and always use '/' for delimiters, and
should not use '.' or '..' or '' as components.  All files are read
and written in binary mode.

$Id: snarf.py 96852 2009-02-20 20:30:05Z amos $
"""

import os
import fsutil

class Snarfer(object):

    """Snarfer -- write an archive to a stream."""

    def __init__(self, ostr):
        """Constructor.  The argument is the output stream."""
        self.ostr = ostr

    def add(self, fspath, path):
        if os.path.isdir(fspath):
            self.addtree(fspath, path + "/")
        elif os.path.isfile(fspath):
            self.addfile(fspath, path)

    def addtree(self, root, prefix="", filter=None):
        """Snarf a directory tree.

        root -- the root of the tree in the filesystem.
        prefix -- optional snarf path prefix, either empty or ending in '/'.
        filter -- optional filter predicate.
        """
        if prefix:
            assert prefix[0] != "/"
            assert prefix[-1] == "/"
        if filter is None:
            def filter(fspath):
                return True
        names = os.listdir(root)
        names.sort()
        self.adddir(prefix)
        for name in names:
            fspath = os.path.join(root, name)
            if not filter(fspath):
                continue
            if os.path.isdir(fspath):
                self.addtree(fspath, prefix + name + "/", filter)
            elif os.path.isfile(fspath):
                self.addfile(fspath, prefix + name)

    def addfile(self, fspath, path):
        """Snarf a single file given by fspath."""
        assert path[-1] != "/"
        f = open(fspath, "rb")
        try:
            f.seek(0, 2)
            size = f.tell()
            f.seek(0)
            self.addstream(f, size, path)
        finally:
            f.close()

    def adddir(self, path):
        path = fsutil.encode(path, 'utf-8')
        self.ostr.write("0 %s\n" % path)

    def addstream(self, istr, size, path):
        """Snarf a single file from a data stream.

        istr -- the input stream;
        size -- the number of bytes to read from istr;
        path -- the snarf path.

        Raises IOError if reading istr returns an EOF condition before
        size bytes have been read.
        """
        path = fsutil.encode(path, 'utf-8')
        self.ostr.write("%d %s\n" % (size, path))
        copybytes(size, istr, self.ostr)


class Unsnarfer(object):
    """Unsnarfer -- read an archive from a stream."""

    def __init__(self, istr):
        """Constructor.  The argument is the input stream."""
        self.istr = istr

    def unsnarf(self, root):
        """Unsnarf the entire archive into a directory tree.

        root -- the root of the directory tree where to write.
        """
        self.root = root
        while True:
            infoline = self.istr.readline()
            if not infoline:
                break
            if not infoline.endswith("\n"):
                raise IOError("incomplete info line %r" % infoline)
            infoline = infoline[:-1]
            sizestr, path = infoline.split(" ", 1)
            size = int(sizestr)
            if size == 0 and (path == "" or path.endswith("/")):
                self.makedir(path)
            else:
                f = self.createfile(path)
                try:
                    copybytes(size, self.istr, f)
                finally:
                    f.close()

    def makedir(self, path):
        if path.endswith('/'):
            path = path[:-1]
        fspath = self.translatepath(path)
        self.ensuredir(fspath)

    def createfile(self, path):
        fspath = self.translatepath(path)
        self.ensuredir(os.path.dirname(fspath))
        return open(fspath, "wb")

    def ensuredir(self, fspath):
        if not os.path.isdir(fspath):
            os.makedirs(fspath)

    def translatepath(self, path):
        if path == "":
            return self.root
        if ":" in path and os.name != "posix":
            raise IOError("path cannot contain colons: $r" % path)
        if "\\" in path and os.name != "posix":
            raise IOError("path cannot contain backslashes: %r" % path)
        parts = path.split("/")
        for forbidden in "", ".", "..", os.curdir, os.pardir:
            if forbidden in parts:
                raise IOError("forbidden part %r in path: %r" %
                              (forbidden, path))
        return os.path.join(self.root, *parts)

def copybytes(size, istr, ostr, bufsize=8192):
    aim = size - bufsize
    pos = 0
    while pos < aim:
        data = istr.read(bufsize)
        if not data:
            raise IOError("not enough data read from input stream")
        pos += len(data)
        ostr.write(data)
    while pos < size:
        data = istr.read(size - pos)
        if not data:
            raise IOError("not enough data read from input stream")
        pos += len(data)
        ostr.write(data)
