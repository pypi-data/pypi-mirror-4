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
"""Mock Metadata class used for testing.

$Id: mockmetadata.py 76667 2007-06-13 15:24:10Z oestermeier $
"""

import os

class MockMetadata(object):

    def __init__(self):
        self.database = {}

    def getentry(self, filename):
        key, filename = self.makekey(filename)
        if key not in self.database:
            self.database[key] = {}
        return self.database[key]

    def getnames(self, dirpath):
        dirkey, dirpath = self.makekey(dirpath)
        names = []
        for key, entry in self.database.iteritems():
            if entry:
                head, tail = os.path.split(key)
                if head == dirkey:
                    names.append(tail)
        return names

    def flush(self):
        pass

    def added(self):
        pass

    # These only exist for the test framework

    def makekey(self, path):
        path = os.path.realpath(path)
        key = os.path.normcase(path)
        return key, path

    def setmetadata(self, filename, metadata={}):
        key, filename = self.makekey(filename)
        if key not in self.database:
            self.database[key] = {"path": filename}
        self.database[key].update(metadata)

    def delmetadata(self, filename):
        key, filename = self.makekey(filename)
        if key in self.database:
            del self.database[key]

    def dump(self):
        return dict([(k, v) for (k, v) in self.database.iteritems() if v])
