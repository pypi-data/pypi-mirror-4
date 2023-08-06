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
"""Handy mixin for test case classes to manipulate temporary files.

$Id: tempfiles.py 75796 2007-05-16 07:49:24Z hdima $
"""

import os
import shutil
import tempfile
import unittest

class TempFiles(unittest.TestCase):

    def setUp(self):
        """Initialize the list of temporary names."""
        self.tempnames = []

    def tearDown(self):
        """Clean up temporary names."""
        for fn in self.tempnames:
            if os.path.isdir(fn):
                shutil.rmtree(fn)
            elif os.path.isfile(fn):
                os.remove(fn)

    def tempdir(self):
        """Create and register a temporary directory."""
        dir = tempfile.mktemp()
        self.tempnames.append(dir)
        os.mkdir(dir)
        return dir

    def tempfile(self, data=None, mode="wb"):
        """Create and register a temporary file."""
        tfn = tempfile.mktemp()
        self.tempnames.append(tfn)
        if data is not None:
            self.writefile(data, tfn, mode)
        return tfn

    def cmpfile(self, fn1, fn2, mode="rb"):
        """Compare two files for equality; they must exist."""
        assert mode in ("r", "rb")
        data1 = self.readfile(fn1, mode)
        data2 = self.readfile(fn2, mode)
        return data1 == data2

    def readfile(self, fn, mode="rb"):
        """Read data from a given file."""
        assert mode in ("r", "rb")
        f = open(fn, mode)
        try:
            data = f.read()
        finally:
            f.close()
        return data

    def writefile(self, data, fn, mode="wb"):
        """Write data to a given file."""
        assert mode in ("w", "wb")
        self.ensuredir(os.path.dirname(fn))
        f = open(fn, mode)
        try:
            f.write(data)
        finally:
            f.close()

    def ensuredir(self, dn):
        """Ensure that a given directory exists."""
        if not os.path.exists(dn):
            os.makedirs(dn)
