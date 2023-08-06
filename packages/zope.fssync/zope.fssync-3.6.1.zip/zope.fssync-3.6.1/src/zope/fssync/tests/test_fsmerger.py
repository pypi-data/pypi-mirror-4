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
"""Tests for the (high-level) FSMerger class.

$Id: test_fsmerger.py 117584 2010-10-15 22:05:51Z patricks $
"""

import os
import sys
import unittest

from os.path import exists, isdir, split, join

from zope.fssync.fsmerger import FSMerger

from zope.fssync.tests.mockmetadata import MockMetadata
from zope.fssync.tests.tempfiles import TempFiles

class TestFSMerger(TempFiles):

    def setUp(self):
        TempFiles.setUp(self)
        # Create a mock metadata database
        self.metadata = MockMetadata()
        # Create a handy entry
        self.entry = {"path": "/foo"}

    diff3ok = None

    def check_for_diff3(self):
        if self.diff3ok is None:
            self.__class__.diff3ok = self.diff3_check()
        return self.diff3ok

    def diff3_check(self):
        if sys.platform == 'win32':
            sys.stderr.write(
                "\nrunning on Windows, diff3 tests in %s disabled\n"
                % __name__)
            return False
        if not hasattr(os, "popen"):
            sys.stderr.write("\nos.popen() not found, diff3 tests disabled\n")
            return False
        f1 = self.tempfile("a")
        f2 = self.tempfile("a")
        f3 = self.tempfile("b")
        pipe = os.popen("diff3 -m -E %s %s %s" % (f1, f2, f3), "r")
        output = pipe.read()
        sts = pipe.close()
        ok = output == "b" and not sts
        if not ok:
            sys.stderr.write("\ndiff3 doesn't work, diff3 tests disabled\n")
        return ok

    def addfile(self, dir, path, data, entry=None):
        # Create a file or directory and write some data to it.  If
        # entry is not None, add it as the file's entry.  If data is a
        # dict, create a directory; the dict key/value entries are
        # used as name/data for the directory contents; if entry is
        # not None, entries are also synthesized for the directory
        # contents.
        path = join(dir, path)
        if entry is not None and not callable(entry):
            self.addentry(path, entry)
        if isinstance(data, dict):
            self.ensuredir(path)
            pentry = self.metadata.getentry(path)
            if entry is not None and "flag" in entry:
                pentry["flag"] = entry["flag"]
            for x in data:
                if entry is not None:
                    newentry = entry.copy()
                    newentry["path"] += "/" + x
                else:
                    newentry = None
                self.addfile(path, x, data[x], newentry)
        elif data is not None:
            f = open(path, "w")
            try:
                f.write(data)
            finally:
                f.close()
            if callable(entry):
                self.addentry(path, entry(path))
        return path

    def addorigfile(self, dir, path, data):
        # Create the 'original' for a file or directory and write data to it
        if isinstance(data, dict):
            path = join(dir, path)
            self.ensuredir(path)
            for x in data:
                self.addorigfile(path, x, data[x])
            return None
        else:
            origdir = join(dir, "@@Zope", "Original")
            self.ensuredir(origdir)
            return self.addfile(origdir, path, data)

    def checkfile(self, path, expected_data):
        # Assert that a file or directory contains the expected data
        if isinstance(expected_data, dict):
            self.assert_(isdir(path))
            for x in expected_data:
                self.checkfile(join(path, x), expected_data[x])
        elif expected_data is None:
            self.assert_(not exists(path))
        else:
            f = open(path, "r")
            try:
                actual_data = f.read()
            finally:
                f.close()
            self.assertEqual(actual_data, expected_data)

    def checkorigfile(self, path, expected_data):
        # Assert that the 'original' contains the expected data
        if isinstance(expected_data, dict):
            self.assert_(isdir(path))
            for x in expected_data:
                self.checkorigfile(join(path, x), expected_data[x])
        else:
            head, tail = split(path)
            self.checkfile(join(head, "@@Zope", "Original", tail),
                           expected_data)

    def addentry(self, path, entry):
        e = self.metadata.getentry(path)
        e.update(entry)

    def checkentry(self, path, entry):
        e = self.metadata.getentry(path)
        self.assertEqual(e, entry)

    def test_ignore(self):
        m = FSMerger(None, None)
        self.assertEqual(m.ignore("foo"), False)
        self.assertEqual(m.ignore("foo~"), True)

    def test_reportaction(self):
        reports = []
        m = FSMerger(None, reports.append)
        for action in "Fix", "Copy", "Merge", "Delete", "Nothing":
            for state in ("Conflict", "Uptodate", "Modified",
                          "Added", "Removed", "Spurious", "Nonexistent"):
                m.reportaction(action, state, action+state)
        # I cheated a little here: the list of expected reports was
        # constructed by printing the actual list of reports in a
        # previous run.  But then I carefully looked it over and
        # verified that all was as expected, so now at least it serves
        # as a regression test.
        self.assertEqual(reports,
                         ['C FixConflict',
                          'U FixUptodate',
                          'M FixModified',
                          'A FixAdded',
                          'R FixRemoved',
                          '? FixSpurious',
                          '* FixNonexistent',

                          'C CopyConflict',
                          'U CopyUptodate',
                          'M CopyModified',
                          'A CopyAdded',
                          'R CopyRemoved',
                          '? CopySpurious',
                          '* CopyNonexistent',

                          'C MergeConflict',
                          'U MergeUptodate',
                          'M MergeModified',
                          'A MergeAdded',
                          'R MergeRemoved',
                          '? MergeSpurious',
                          '* MergeNonexistent',

                          'C DeleteConflict',
                          '* DeleteUptodate',
                          'M DeleteModified',
                          'A DeleteAdded',
                          'R DeleteRemoved',
                          '? DeleteSpurious',
                          'D DeleteNonexistent',

                          'C NothingConflict',
                          '* NothingUptodate',
                          'M NothingModified',
                          'A NothingAdded',
                          'R NothingRemoved',
                          '? NothingSpurious',
                          '* NothingNonexistent'])

    def test_reportdir(self):
        reports = []
        m = FSMerger(None, reports.append)
        m.reportdir("X", "foo")
        self.assertEqual(reports, ["X foo" + os.sep])

    def mergetest(self, name, localdata, origdata, remotedata,
                  localentry, remoteentry,
                  expected_reports_template,
                  expected_localdata, expected_origdata, expected_remotedata,
                  expected_localentry, expected_remoteentry,
                  overwrite_local=False):
        # Generic test setup to test merging files
        reports = []
        m = FSMerger(self.metadata, reports.append, overwrite_local)

        localtopdir = self.tempdir()
        remotetopdir = self.tempdir()
        localdir = join(localtopdir, "local")
        remotedir = join(remotetopdir, "remote")
        os.mkdir(localdir)
        os.mkdir(remotedir)

        localfile = self.addfile(localdir, name, localdata, localentry)
        self.addorigfile(localdir, name, origdata)
        remotefile = self.addfile(remotedir, name, remotedata, remoteentry)

        m.merge_dirs(localdir, remotedir)

        expected_reports = []
        for er in expected_reports_template:
            er = er.replace("/", os.sep)
            er = er.replace("%l", localfile)
            er = er.replace("%r", remotefile)
            expected_reports.append(er)
        filtered_reports = [r for r in reports if r[0] not in "*/"]
        self.assertEqual(filtered_reports, expected_reports)

        if isinstance(expected_localdata, str):
            expected_localdata = expected_localdata.replace("%l", localfile)
            expected_localdata = expected_localdata.replace("%r", remotefile)

        self.checkfile(localfile, expected_localdata)
        self.checkorigfile(localfile, expected_origdata)
        self.checkfile(remotefile, expected_remotedata)

        if callable(expected_localentry):
            expected_localentry = expected_localentry(localfile)
        self.checkentry(localfile, expected_localentry)
        self.checkentry(remotefile, expected_remoteentry)

    def test_merge_nochange(self):
        self.mergetest("foo", "a", "a", "a", self.entry, self.entry,
                       [], "a", "a", "a", self.entry, self.entry)

    def test_merge_localchange(self):
        self.mergetest("foo", "b", "a", "a", self.entry, self.entry,
                       ["M %l"], "b", "a", "a", self.entry, self.entry)

    def test_merge_remotechange(self):
        self.mergetest("foo", "a", "a", "b", self.entry, self.entry,
                       ["U %l"], "b", "b", "b", self.entry, self.entry)

    def test_merge_diff3(self):
        if not self.check_for_diff3():
            return
        self.mergetest("foo", "a\nl\n", "a\n", "r\na\n",
                       self.entry, self.entry,
                       ["M %l"], "r\na\nl\n", "r\na\n", "r\na\n",
                       self.entry, self.entry)

    def test_merge_equal(self):
        self.mergetest("foo", "ab", "a", "ab", self.entry, self.entry,
                       ["U %l"], "ab", "ab", "ab", self.entry, self.entry)

    def test_merge_conflict(self):
        if not self.check_for_diff3():
            return
        conflict = "<<<<<<< %l\nl\n=======\nr\n>>>>>>> %r\n"
        self.mergetest("foo", "l\n", "a\n", "r\n", self.entry, self.entry,
                       ["C %l"], conflict, "r\n", "r\n",
                       self.make_conflict_entry, self.entry)

    def make_conflict_entry(self, local):
        # Helper for test_*_conflict
        e = {"conflict": "yes"}
        e.update(self.entry)
        return e

    # Tests for sticky conflict reporting

    def test_sticky_conflict(self):
        conflict = "<<<<<<< foo\nl\n=======\nr\n>>>>>>> foo\n"
        self.mergetest("foo", conflict, "r\n", "r\n",
                       self.make_conflict_entry, self.entry,
                       ["C %l"], conflict, "r\n", "r\n",
                       self.make_conflict_entry, self.entry)

    def test_cleared_but_unresolved_conflict(self):
        # data are the same, but the conflict marker hasn't been cleared
        self.mergetest("foo", "r\n", "r\n", "r\n",
                       self.make_conflict_entry, self.entry,
                       ["C %l"], "r\n", "r\n", "r\n",
                       self.make_conflict_entry, self.entry)

    # Tests for added files: local, remote, both

    def test_added_file_local(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", "x", None, None,
                       added_entry, None,
                       ["A %l"],
                       "x", None, None,
                       added_entry, {})

    def test_added_file_remote(self):
        self.mergetest("foo", None, None, "x",
                       None, self.entry,
                       ["U %l"],
                       "x", "x", "x",
                       self.entry, self.entry)

    def test_added_file_both(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", "x", None, "x",
                       added_entry, self.entry,
                       ["U %l"],
                       "x", "x", "x",
                       self.entry, self.entry)

    # Tests for removed files: local, remote, both

    def test_removed_file_local(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, "x", "x",
                       removed_entry, self.entry,
                       ["R %l"],
                       None, "x", "x",
                       removed_entry, self.entry)

    def test_removed_file_remote(self):
        self.mergetest("foo", "x", "x", None,
                       self.entry, {},
                       ["D %l"],
                       None, None, None,
                       {}, {})

    def test_removed_file_both(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, "x", None,
                       removed_entry, {},
                       ["D %l"],
                       None, None, None,
                       {}, {})

    # Tests for added empty directories: local, remote, both

    def test_added_dir_local(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", {}, None, None,
                       added_entry, None,
                       ["A %l/"],
                       {}, None, None,
                       added_entry, {})

    def test_added__dir_remote(self):
        self.mergetest("foo", None, None, {},
                       None, self.entry,
                       ["N %l/"],
                       {}, {}, {},
                       self.entry, self.entry)

    def test_added_dir_both(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", {}, None, {},
                       added_entry, self.entry,
                       ["U %l/"],
                       {}, None, {},
                       self.entry, self.entry)

    # Tests for added directory trees: local, remote, both

    def test_added_tree_local(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", {"x": "x"}, None, None,
                       added_entry, None,
                       ["A %l/", "A %l/x"],
                       {"x": "x"}, None, None,
                       added_entry, {})

    def test_added_tree_remote(self):
        self.mergetest("foo", None, None, {"x": "x"},
                       None, self.entry,
                       ["N %l/", "U %l/x"],
                       {"x": "x"}, {"x": "x"}, {"x": "x"},
                       self.entry, self.entry)

    def test_added_tree_both(self):
        added_entry = {"flag": "added"}
        added_entry.update(self.entry)
        self.mergetest("foo", {"x": "x"}, None, {"x": "x"},
                       added_entry, self.entry,
                       ["U %l/", "U %l/x"],
                       {"x": "x"}, {"x": "x"}, {"x": "x"},
                       self.entry, self.entry)

    # Tests for removed empty directories: local, remote, both

    def test_removed_dir_local(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, None, {},
                       removed_entry, self.entry,
                       ["R %l/"],
                       None, None, {},
                       removed_entry, self.entry)

    def test_removed_dir_remote(self):
        self.mergetest("foo", {}, None, None,
                       self.entry, {},
                       ["D %l/"],
                       None, None, None,
                       {}, {})

    def test_removed_dir_both(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, None, None,
                       removed_entry, {},
                       ["D %l"],
                       None, None, None,
                       {}, {})

    # Tests for removed non-empty directories: local, remote, both

    def test_removed_tree_local(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, None, {"x": "x"},
                       removed_entry, self.entry,
                       ["R %l/"],
                       None, None, {"x": "x"},
                       removed_entry, self.entry)

    def test_removed_tree_remote(self):
        self.mergetest("foo", {"x": "x"}, {"x": "x"}, None,
                       self.entry, {},
                       ["D %l/x", "D %l/"],
                       None, None, None,
                       {}, {})

    def test_removed_tree_both(self):
        removed_entry = {"flag": "removed"}
        removed_entry.update(self.entry)
        self.mergetest("foo", None, None, None,
                       removed_entry, {},
                       ["D %l"],
                       None, None, None,
                       {}, {})


    def test_overwrite_local(self):
        # make sure that we normally get a conflict when the orginal,
        # local, and remote versions are different
        conflict = "<<<<<<< %l\nl\n=======\nr\n>>>>>>> %r\n"
        self.mergetest("foo", "l\n", "a\n", "r\n", self.entry, self.entry,
                       ["C %l"], conflict, "r\n", "r\n",
                       self.make_conflict_entry, self.entry)

        # now try to same thing but with overwrite_local set to
        # true. This time the local and original should be replaced
        # with the remote file.
        self.mergetest("foo", "l\n", "a\n", "r\n", self.entry, self.entry,
                       ["U %l"], "r\n", "r\n", "r\n",
                       self.entry, self.entry, True)

        # try it when the original and local are the same, but the
        # remote is different. In this case the overwrite_local
        # setting doesn't change things.
        self.mergetest("foo", "a\n", "a\n", "r\n", self.entry, self.entry,
                       ["U %l"], "r\n", "r\n", "r\n",
                       self.entry, self.entry, True)

        self.mergetest("foo", "a\n", "a\n", "r\n", self.entry, self.entry,
                       ["U %l"], "r\n", "r\n", "r\n",
                       self.entry, self.entry)

        # testing if remote is the same as local. Again,
        # overwrite_local shouldn't change things.
        self.mergetest("foo", "l\n", "a\n", "l\n", self.entry, self.entry,
                       ["U %l"], "l\n", "l\n", "l\n",
                       self.entry, self.entry, True)

        self.mergetest("foo", "l\n", "a\n", "l\n", self.entry, self.entry,
                       ["U %l"], "l\n", "l\n", "l\n",
                       self.entry, self.entry)

        # How about when all are the same? Again overwrite_local
        # shouldn't change anything.
        self.mergetest("foo", "a\n", "a\n", "a\n", self.entry, self.entry,
                       [], "a\n", "a\n", "a\n",
                       self.entry, self.entry, True)

        self.mergetest("foo", "a\n", "a\n", "a\n", self.entry, self.entry,
                       [], "a\n", "a\n", "a\n",
                       self.entry, self.entry)

        # test when original and remote are the same. Again,
        # overwrite_local shouldn't make any difference.
        self.mergetest("foo", "l\n", "a\n", "a\n", self.entry, self.entry,
                       ["M %l"], "l\n", "a\n", "a\n",
                       self.entry, self.entry, True)

        self.mergetest("foo", "l\n", "a\n", "a\n", self.entry, self.entry,
                       ["M %l"], "l\n", "a\n", "a\n",
                       self.entry, self.entry)


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestFSMerger))
    return s

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
