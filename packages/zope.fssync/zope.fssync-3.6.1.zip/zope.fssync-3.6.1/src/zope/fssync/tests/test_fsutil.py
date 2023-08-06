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
"""Tests for the functions in the fsutil module.

$Id: test_fsutil.py 25177 2004-06-02 13:17:31Z jim $
"""

import os
import unittest

from os.path import split, join, exists, isdir

from zope.fssync import fsutil
from zope.fssync.tests.tempfiles import TempFiles

def FIX(path):
    # This fixes only relative paths
    parts = path.split("/")
    mapping = {".": os.curdir, "..": os.pardir}
    parts = [mapping.get(x, x) for x in parts]
    return join(*parts)

class TestFSUtil(TempFiles):

    def test_split(self):
        self.assertEqual(fsutil.split(FIX("foo/bar")), ("foo", "bar"))
        self.assertEqual(fsutil.split("foo"), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(FIX("foo/")), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(FIX("foo/.")), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(FIX("foo/bar/..")), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(FIX(".")), split(os.getcwd()))

    def test_getspecial(self):
        self.assertEqual(fsutil.getspecial(FIX("foo/bar"), "X"),
                         FIX("foo/@@Zope/X/bar"))

    def test_getoriginal(self):
        self.assertEqual(fsutil.getoriginal(FIX("foo/bar")),
                         FIX("foo/@@Zope/Original/bar"))

    def test_getextra(self):
        self.assertEqual(fsutil.getextra(FIX("foo/bar")),
                         FIX("foo/@@Zope/Extra/bar"))

    def test_getannotations(self):
        self.assertEqual(fsutil.getannotations(FIX("foo/bar")),
                         FIX("foo/@@Zope/Annotations/bar"))

    def test_ensuredir(self):
        tmpdir = self.tempfile(None)
        self.assertEqual(exists(tmpdir), False)
        self.assertEqual(isdir(tmpdir), False)
        fsutil.ensuredir(tmpdir)
        self.assertEqual(isdir(tmpdir), True)
        fsutil.ensuredir(tmpdir)
        self.assertEqual(isdir(tmpdir), True)

    def test_ensuredir_error(self):
        tmpfile = self.tempfile("x\n")
        self.assertRaises(OSError, fsutil.ensuredir, tmpfile)

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestFSUtil)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
