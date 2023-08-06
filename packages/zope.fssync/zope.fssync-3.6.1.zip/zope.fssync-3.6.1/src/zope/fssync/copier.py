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
"""Tree-copy helpers for 'zsync copy' and 'zbundle create'.

$Id: copier.py 76667 2007-06-13 15:24:10Z oestermeier $
"""
import os
import shutil

from zope.fssync import fsutil


class FileCopier(object):
    """Copy from a normal file tree into an fssync checkout."""

    def __init__(self, sync):
        self.sync = sync

    def copy(self, source, target, children=True):
        if os.path.isdir(source):
            os.mkdir(target)
            shutil.copymode(source, target)
            self.addEntry(source, target)
            if children:
                queue = self.listDirectory(source)
                while queue:
                    fn = queue.pop(0)
                    src = os.path.join(source, fn)
                    dst = os.path.join(target, fn)
                    if os.path.isdir(src):
                        os.mkdir(dst)
                        shutil.copymode(src, dst)
                        self.addEntry(src, dst)
                        queue.extend([os.path.join(fn, f)
                                      for f in self.listDirectory(src)])
                    else:
                        shutil.copy(src, dst)
                        self.addEntry(src, dst)
        else:
            shutil.copy(source, target)
            self.addEntry(source, target)

    def addEntry(self, source, target):
        self.sync.add(target)

    def listDirectory(self, dir):
        return [fn
                for fn in os.listdir(dir)
                if fn != "@@Zope"
                if not self.sync.fsmerger.ignore(fn)]


class ObjectCopier(FileCopier):
    """Copy objects from an fssync checkout into an fssync checkout."""

    def addEntry(self, source, target):
        type, factory = self.sync.metadata.gettypeinfo(source)
        self._syncadd(target, type, factory)
        self._copyspecials(source, target, fsutil.getextra)
        self._copyspecials(source, target, fsutil.getannotations)

    def _syncadd(self, target, type, factory):
        self.sync.add(target, type, factory)

    def _copyspecials(self, source, target, getwhat):
        src = getwhat(source)
        if os.path.isdir(src):
            dst = getwhat(target)
            fsutil.ensuredir(dst)
            copier = SpecialCopier(self.sync)
            for name in self.sync.metadata.getnames(src):
                # copy a single child
                copier.copy(os.path.join(src, name), os.path.join(dst, name))
            self.sync.metadata.flush()

    def listDirectory(self, dir):
        # We don't need to worry about fsmerger.ignore() since we're
        # only relying on metadata to generate the list of names.
        return self.sync.metadata.getnames(dir)


class SpecialCopier(ObjectCopier):
    """Copy extras and annotations as part of an object copy.

    This is a specialized copier that doesn't expect the original to
    have a path.
    """

    def _syncadd(self, target, type, factory):
        self.sync.basicadd(target, type, factory)
