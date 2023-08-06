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
"""Tests for the Merger class.

$Id: test_merger.py 38304 2005-09-06 14:24:18Z benji_york $
"""

import os, sys
import unittest

from os.path import exists

from zope.fssync.merger import Merger

from zope.fssync.tests.mockmetadata import MockMetadata
from zope.fssync.tests.tempfiles import TempFiles

added = {"flag": "added"}
removed = {"flag": "removed"}

class TestMerger(TempFiles):

    diff3ok = None

    def check_for_diff3(self):
        if self.diff3ok is None:
            self.__class__.diff3ok = self.diff3_check()
        return self.diff3ok

    def diff3_check(self):
        if sys.platform == 'win32':
            return False
        if not hasattr(os, "popen"):
            return False
        f1 = self.tempfile("a")
        f2 = self.tempfile("b")
        f3 = self.tempfile("b")
        pipe = os.popen("diff3 -m -E %s %s %s" % (f1, f2, f3), "r")
        output = pipe.read()
        sts = pipe.close()
        return output == "b" and not sts

    def runtest(self, localdata, origdata, remotedata,
                localmetadata, remotemetadata, exp_localdata,
                exp_action, exp_state, exp_merge_state=None):
        local = self.tempfile(localdata)
        orig = self.tempfile(origdata)
        remote = self.tempfile(remotedata)
        md = MockMetadata()
        if localmetadata is not None:
            md.setmetadata(local, localmetadata)
        if remotemetadata is not None:
            md.setmetadata(remote, remotemetadata)
        m = Merger(md)
        action, state = m.classify_files(local, orig, remote)
        self.assertEqual((action, state), (exp_action, exp_state))

        # Now try the actual merge
        state = m.merge_files(local, orig, remote, action, state)
        self.assertEqual(state, exp_merge_state or exp_state)
        self.assert_(md.getentry(remote).get("flag") is None)
        if exp_localdata is None:
            self.assert_(not exists(local))
        else:
            f = open(local, "r")
            try:
                data = f.read()
            finally:
                f.close()
            if exp_merge_state != "Conflict":
                self.assertEqual(data, exp_localdata)
            else:
                self.assert_(data.find(exp_localdata) >= 0)

        # Verify that the returned state matches reality
        if state == "Uptodate":
            self.assert_(self.cmpfile(local, orig))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local))
            self.assert_(not md.getentry(local).get("flag"),
                         md.getentry(local))
            self.assert_(md.getentry(remote))
        elif state == "Modified":
            self.assert_(not self.cmpfile(local, orig))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local))
            self.assert_(not md.getentry(local).get("flag"))
            self.assert_(md.getentry(remote))
        elif state == "Added":
            self.assert_(exists(local))
            self.assert_(not exists(orig))
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(remote))
            self.assert_(md.getentry(local).get("flag") == "added")
        elif state == "Removed":
            self.assert_(not exists(local))
            self.assert_(self.cmpfile(orig, remote))
            self.assert_(md.getentry(local).get("flag") == "removed")
            self.assert_(md.getentry(remote))
        elif state == "Nonexistent":
            self.assert_(not exists(local))
            self.assert_(not exists(orig))
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(local))
            self.assert_(not md.getentry(remote))
        elif state == "Conflict":
            self.assert_(md.getentry(local).has_key("conflict"))
            # No other checks; there are many kinds of conflicts
        elif state == "Spurious":
            self.assert_(exists(local))
            # Don't care about orig
            self.assert_(not exists(remote))
            self.assert_(not md.getentry(local))
            self.assert_(not md.getentry(remote))
        else:
            self.assert_(False)

    # Test cases for files

    def test_all_equal(self):
        self.runtest("a", "a", "a", {}, {}, "a", "Nothing", "Uptodate")

    def test_local_modified(self):
        self.runtest("ab", "a", "a", {}, {}, "ab", "Nothing", "Modified")

    def test_remote_modified(self):
        self.runtest("a", "a", "ab", {}, {}, "ab", "Copy", "Uptodate")

    def test_both_modified_resolved(self):
        if not self.check_for_diff3():
            return
        self.runtest("l\na\n", "a\n", "a\nr\n", {}, {},
                     "l\na\nr\n", "Merge", "Modified")

    def test_both_modified_conflict(self):
        if not self.check_for_diff3():
            return
        self.runtest("ab", "a", "ac", {}, {},
                     "", "Merge", "Modified", "Conflict")

    def test_local_added(self):
        self.runtest("a", None, None, added, None, "a", "Nothing", "Added")

    def test_remote_added(self):
        self.runtest(None, None, "a", None, {}, "a", "Copy", "Uptodate")

    def test_both_added_same(self):
        self.runtest("a", None, "a", added, {}, "a", "Fix", "Uptodate")

    def test_both_added_different(self):
        if not self.check_for_diff3():
            return
        self.runtest("a", None, "b", added, {},
                     "", "Merge", "Modified", "Conflict")

    def test_local_removed(self):
        self.runtest(None, "a", "a", removed, {}, None, "Nothing", "Removed")

    def test_remote_removed(self):
        self.runtest("a", "a", None, {}, None, None, "Delete", "Nonexistent")

    def test_both_removed(self):
        self.runtest(None, "a", None, removed, None,
                     None, "Delete", "Nonexistent")

    def test_local_lost_remote_unchanged(self):
        self.runtest(None, "a", "a", {}, {}, "a", "Copy", "Uptodate")

    def test_local_lost_remote_modified(self):
        self.runtest(None, "a", "b", {}, {}, "b", "Copy", "Uptodate")

    def test_local_lost_remote_removed(self):
        self.runtest(None, "a", None, {}, None, None, "Delete", "Nonexistent")

    def test_spurious(self):
        self.runtest("a", None, None, None, None, "a", "Nothing", "Spurious")

    def test_conflict_report(self):
        local = self.tempfile("CONFLICT")
        orig = self.tempfile("x")
        remote = self.tempfile("x")
        md = MockMetadata()
        m = Merger(md)
        lentry = md.getentry(local)
        lentry["path"] = "/foo"
        lentry["conflict"] = mtime = os.path.getmtime(local)
        rentry = md.getentry(remote)
        rentry["path"] = "/foo"
        action, state = m.classify_files(local, orig, remote)
        self.assertEqual((action, state), ("Nothing", "Conflict"))
        self.assertEqual(lentry.get("conflict"), mtime)

    # TODO: need test cases for anomalies, e.g. files missing or present
    # in spite of metadata, or directories instead of files, etc.

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestMerger)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
