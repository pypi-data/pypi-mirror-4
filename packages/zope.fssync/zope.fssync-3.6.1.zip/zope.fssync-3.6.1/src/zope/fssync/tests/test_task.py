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
"""Tests for the Commit task.

TODO: This should be rewritten as doctest and moved
to zope.fssync where it belongs.

$Id: test_committer.py 72447 2007-02-08 07:48:58Z oestermeier $
"""
import os
import shutil
import tempfile
import unittest

import zope.component
import zope.interface
from zope.traversing.interfaces import TraversalError, IContainmentRoot
from zope.traversing.interfaces import ITraversable, ITraverser
from zope.xmlpickle import dumps
from zope.location import Location
from zope.filerepresentation.interfaces import IFileFactory
from zope.filerepresentation.interfaces import IDirectoryFactory

from zope.fssync import fsutil
from zope.fssync.tests.mockmetadata import MockMetadata
from zope.fssync.tests.tempfiles import TempFiles

from zope.component.testing import PlacelessSetup

from zope.fssync import synchronizer
from zope.fssync import interfaces
from zope.fssync import repository
from zope.fssync import pickle
from zope.fssync import task

def provideSynchronizer(klass, Synchronizer):
    zope.component.provideUtility(Synchronizer, interfaces.ISynchronizerFactory,
                                        name=synchronizer.dottedname(klass))

class Sample(object):
    pass

class IPretendFile(zope.interface.Interface):
    pass

class PretendFile(object):
    zope.interface.implements(IPretendFile)

    data = ''
    contentType = ''

    def __init__(self, data, contentType):
        self.data = data
        self.contentType = contentType

class IPretendContainer(zope.interface.Interface):
    pass

class PretendContainer(Location):
    zope.interface.implements(IPretendContainer, ITraversable, ITraverser)

    def __init__(self):
        self.holding = {}

    def __setitem__(self, name, value):
        name = name.lower()
        if name in self.holding:
            raise KeyError
        self.holding[name] = value
        return name

    def __delitem__(self, name):
        name = name.lower()
        del self.holding[name]

    def __getitem__(self, name):
        name = name.lower()
        return self.holding[name]

    def get(self, name):
        name = name.lower()
        return self.holding.get(name)

    def __contains__(self, name):
        name = name.lower()
        return name in self.holding

    def keys(self):
        return self.holding.keys()

    def items(self):
        return self.holding.items()

    def iteritems(self):
        return self.holding.iteritems()

    def traverse(self, name, furtherPath):
        try:
            return self[name]
        except KeyError:
            raise TraversalError

PCname = PretendContainer.__module__ + "." + PretendContainer.__name__

class PretendRootContainer(PretendContainer):
    zope.interface.implements(IContainmentRoot)


class TestBase(PlacelessSetup, TempFiles):

    # Base class for test classes

    def setUp(self):
        super(TestBase, self).setUp()

        # Set up serializer factory
        zope.component.provideUtility(synchronizer.DefaultSynchronizer,
                                        interfaces.ISynchronizerFactory)

        zope.component.provideAdapter(pickle.XMLPickler)
        zope.component.provideAdapter(pickle.XMLUnpickler)
        zope.component.provideAdapter(pickle.PathPersistentIdGenerator)
        zope.component.provideAdapter(pickle.PathPersistentLoader)

        zope.component.provideUtility(synchronizer.FileGenerator())
        zope.component.provideUtility(synchronizer.DirectoryGenerator())

        # Set up temporary name administration
        TempFiles.setUp(self)

    def tearDown(self):
        # Clean up temporary files and directories
        TempFiles.tearDown(self)

        PlacelessSetup.tearDown(self)


@zope.component.adapter(IPretendContainer)
@zope.interface.implementer(IFileFactory)
def file_factory_maker(container):
    def file_factory(name, content_type, data):
        return PretendFile(data, content_type)
    return file_factory

@zope.component.adapter(IPretendContainer)
@zope.interface.implementer(IDirectoryFactory)
def directory_factory_maker(container):
    def directory_factory(name):
        return PretendContainer()
    return directory_factory

def sort(lst):
    lst.sort()
    return lst


class TestTaskModule(TestBase):

    def setUp(self):
        super(TestTaskModule, self).setUp()
        self.location = tempfile.mktemp()
        os.mkdir(self.location)

    def tearDown(self):
        super(TestTaskModule, self).tearDown()
        shutil.rmtree(self.location)

    def test_getSynchronizer(self):
        obj = Sample()
        adapter = synchronizer.getSynchronizer(obj)
        self.assertEqual(adapter.__class__, synchronizer.DefaultSynchronizer)

class TestCommitClass(TestBase):

    def create_committer(self):
        filesystem = repository.FileSystemRepository()
        return task.Commit(synchronizer.getSynchronizer, filesystem)

    def test_set_item_without_serializer(self):
        committer = self.create_committer()
        container = {}
        committer.setItem(container, "foo", 42)
        self.assertEqual(container, {"foo": 42})

    def test_set_item_new(self):
        committer = self.create_committer()
        container = PretendContainer()
        committer.setItem(container, "foo", 42)
        self.assertEqual(container.holding, {"foo": 42})

    def test_set_item_replace(self):
        provideSynchronizer(PretendContainer, synchronizer.DirectorySynchronizer)
        committer = self.create_committer()
        container = PretendContainer()
        committer.setItem(container, "foo", 42)
        committer.setItem(container, "foo", 24, replace=True)
        self.assertEqual(container.holding, {"foo": 24})

    def test_set_item_nonexisting(self):
        provideSynchronizer(PretendContainer, synchronizer.DirectorySynchronizer)
        committer = self.create_committer()
        container = PretendContainer()
        self.assertRaises(KeyError, committer.setItem,
                          container, "foo", 42, replace=True)

    def create_object(self, *args, **kw):
        # Helper for the create_object() tests.
        filesystem = repository.FileSystemRepository()
        c = task.Commit(synchronizer.getSynchronizer, filesystem)
        c.createObject(*args, **kw)

    def create_object_debug(self, *args, **kw):
        # Helper for the create_object() tests.
        filesystem = repository.FileSystemRepository()
        c = task.Commit(synchronizer.getSynchronizer, filesystem)
        c.debug = True
        c.createObject(*args, **kw)


    def test_create_object_extra(self):
        class TestContainer(object):
            # simulate AttrMapping
            def __setitem__(self, name, value):
                self.name = name
                self.value = value
        class TestRoot(object):
            zope.interface.implements(IContainmentRoot, ITraverser)
            def traverse(self, *args):
                pass
        fspath = tempfile.mktemp()
        f = open(fspath, 'w')
        f.write('<?xml version="1.0" encoding="utf-8" ?>')
        f.write('<pickle> <string>text/plain</string> </pickle>')
        f.close()
        container = TestContainer()
        name = "contentType"
        try:
            self.create_object(container, name, {}, fspath, list().append) #, context=root)
        finally:
            os.remove(fspath)
        self.assertEqual(container.name, name)
        self.assertEqual(container.value, "text/plain")

    def test_create_object_factory_file(self):
        container = {}
        entry = {"flag": "added", "factory": "__builtin__.dict"}
        tfn = os.path.join(self.tempdir(), "foo")
        data = {"hello": "world"}
        self.writefile(dumps(data), tfn)
        self.create_object_debug(container, "foo", entry, tfn, list().append)
        self.assertEqual(container, {"foo": data})

    def test_create_object_factory_directory(self):
        provideSynchronizer(PretendContainer, synchronizer.DirectorySynchronizer)
        container = {}
        entry = {"flag": "added", "factory": PCname}
        tfn = os.path.join(self.tempdir(), "foo")
        os.mkdir(tfn)
        self.create_object(container, "foo", entry, tfn, list().append)
        self.assertEqual(container.keys(), ["foo"])
        self.assertEqual(container["foo"].__class__, PretendContainer)

    def test_create_object_default(self):
        container = PretendRootContainer()
        entry = {"flag": "added"}
        data = ["hello", "world"]
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(dumps(data), tfn, "wb")
        self.create_object(container, "foo", entry, tfn, list().append)
        self.assertEqual(container.items(), [("foo", ["hello", "world"])])

    def test_create_object_ifilefactory(self):
        zope.component.provideAdapter(file_factory_maker)
        container = PretendContainer()
        entry = {"flag": "added"}
        data = "hello world"
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(data, tfn, "wb")
        self.create_object(container, "foo", entry, tfn, list().append)
        self.assertEqual(container.holding["foo"].__class__, PretendFile)
        self.assertEqual(container.holding["foo"].data, "hello world")

    def test_create_object_idirectoryfactory(self):
        zope.component.provideAdapter(directory_factory_maker)
        container = PretendContainer()
        entry = {"flag": "added"}
        tfn = os.path.join(self.tempdir(), "foo")
        os.mkdir(tfn)
        self.create_object(container, "foo", entry, tfn, list().append)
        self.assertEqual(container.holding["foo"].__class__, PretendContainer)


class TestCheckinClass(TestBase):

    def test_pickle_error_is_reported(self):
        parentdir = self.tempdir()
        foofile = os.path.join(parentdir, 'foo')
        self.writefile(
            '<?xml version="1.0" encoding="utf-8" ?><pickle><foo</pickle>',
            foofile, 'wb')
        metadata = MockMetadata()
        metadata.getentry(foofile)['path'] = 'foo'

        filesystem = repository.FileSystemRepository(metadata=metadata)
        checkin = task.Checkin(synchronizer.getSynchronizer, filesystem)

        container = PretendContainer()
        self.assertRaises(
            Exception, checkin.perform, container, 'foo', foofile)


class TestCheckClass(TestBase):

    def setUp(self):
        # Set up base class (PlacelessSetup and TempNames)
        TestBase.setUp(self)

        # Set up environment
        provideSynchronizer(PretendContainer, synchronizer.DirectorySynchronizer)
        #provideSynchronizer(dict, DictAdapter)
        #zope.component.provideAdapter(file_factory_maker)
        zope.component.provideAdapter(directory_factory_maker)

        # Set up fixed part of object tree
        self.parent = PretendContainer()
        self.child = PretendContainer()
        self.grandchild = PretendContainer()
        self.parent["child"] = self.child
        self.child["grandchild"] = self.grandchild
        self.foo = ["hello", "world"]
        self.child["foo"] = self.foo

        # Set up fixed part of filesystem tree
        self.parentdir = self.tempdir()
        self.childdir = os.path.join(self.parentdir, "child")
        os.mkdir(self.childdir)
        self.foofile = os.path.join(self.childdir, "foo")
        self.writefile(dumps(self.foo), self.foofile, "wb")
        self.originalfoofile = fsutil.getoriginal(self.foofile)
        self.writefile(dumps(self.foo), self.originalfoofile, "wb")
        self.grandchilddir = os.path.join(self.childdir, "grandchild")
        os.mkdir(self.grandchilddir)

        # Set up metadata
        self.metadata = MockMetadata()
        self.getentry = self.metadata.getentry

        # Set up fixed part of entries
        self.parententry = self.getentry(self.parentdir)
        self.parententry["path"] = "/parent"
        self.childentry = self.getentry(self.childdir)
        self.childentry["path"] = "/parent/child"
        self.grandchildentry = self.getentry(self.grandchilddir)
        self.grandchildentry["path"] = "/parent/child/grandchild"
        self.fooentry = self.getentry(self.foofile)
        self.fooentry["path"] = "/parent/child/foo"

        # Set up check task
        filesystem = repository.FileSystemRepository(metadata=self.metadata)
        self.checker = task.Check(synchronizer.getSynchronizer, filesystem)

    def check_errors(self, expected_errors):
        # Helper to call the checker and assert a given set of errors
        self.checker.check(self.parent, "", self.parentdir)
        self.assertEqual(sort(self.checker.errors()), sort(expected_errors))

    def check_no_errors(self):
        # Helper to call the checker and assert there are no errors
        self.check_errors([])

    def test_vanilla(self):
        # The vanilla situation should not be an error
        self.check_no_errors()

    def test_file_changed(self):
        # Changing a file is okay
        self.newfoo = self.foo + ["news"]
        self.writefile(dumps(self.newfoo), self.foofile, "wb")
        self.check_no_errors()

    def test_file_type_changed(self):
        # Changing a file's type is okay
        self.newfoo = ("one", "two")
        self.fooentry["type"] = "__builtin__.tuple"
        self.writefile(dumps(self.newfoo), self.foofile, "wb")
        self.check_no_errors()

    def test_file_conflict(self):
        # A real conflict is an error
        newfoo = self.foo + ["news"]
        self.writefile(dumps(newfoo), self.foofile, "wb")
        self.foo.append("something else")
        self.check_errors([self.foofile])

    def test_file_sticky_conflict(self):
        # A sticky conflict is an error
        self.fooentry["conflict"] = 1
        self.check_errors([self.foofile])

    def test_file_added(self):
        # Adding a file properly is okay
        self.bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(self.bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["flag"] = "added"
        self.check_no_errors()

    def test_file_added_no_file(self):
        # Flagging a non-existing file as added is an error
        barfile = os.path.join(self.childdir, "bar")
        barentry = self.getentry(barfile)
        barentry["flag"] = "added"
        self.check_errors([barfile])

    def test_file_spurious(self):
        # A spurious file (empty entry) is okay
        bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(bar), barfile, "wb")
        self.check_no_errors()

    def test_file_added_no_flag(self):
        # Adding a file without setting the "added" flag is an error
        bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([barfile])

    def test_same_files_added_twice(self):
        # Adding files in both places is ok as long as the files are the same
        self.bar = ["this", "is", "bar"]
        self.child["bar"] = self.bar
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(self.bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["path"] = "/parent/child/bar"
        self.check_no_errors()

    def test_different_files_added_twice(self):
        # Adding files in both places is an error if the files are different
        bar = ["this", "is", "bar"]
        self.child["bar"] = bar
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(["something else"]), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([barfile])

    def test_file_lost(self):
        # Losing a file is an error
        os.remove(self.foofile)
        self.check_errors([self.foofile])

    def test_file_unmodified_lost_originial(self):
        # Losing the original file is ok as long as the file does not change
        os.remove(self.originalfoofile)
        self.check_no_errors()

    def test_file_modified_lost_originial(self):
        # Losing the original file is an error as soon as the file changes
        os.remove(self.originalfoofile)
        self.writefile('something changed', self.foofile, "wb")
        self.check_errors([self.foofile])

    def test_file_removed(self):
        # Removing a file properly is okay
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        self.check_no_errors()

    def test_file_removed_conflict(self):
        # Removing a file that was changed in the database is an error
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        self.foo.append("news")
        self.check_errors([self.foofile])

    def test_file_removed_twice(self):
        # Removing a file in both places is an error
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        del self.child["foo"]
        self.check_errors([self.foofile])

    def test_file_removed_object(self):
        # Removing the object should cause a conflict
        del self.child["foo"]
        self.check_errors([self.foofile])

    def test_file_entry_cleared(self):
        # Clearing out a file's entry is an error
        self.fooentry.clear()
        self.check_errors([self.foofile])

    def test_dir_added(self):
        # Adding a directory is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["flag"] = "added"
        self.check_no_errors()

    def test_dir_spurious(self):
        # A spurious directory is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        self.check_no_errors()

    def test_dir_added_no_flag(self):
        # Adding a directory without setting the "added" flag is an error
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([bardir])

    def test_dir_lost(self):
        # Losing a directory is an error
        shutil.rmtree(self.grandchilddir)
        self.check_errors([self.grandchilddir])

    def test_dir_removed(self):
        # Removing a directory properly is okay
        shutil.rmtree(self.grandchilddir)
        self.grandchildentry["flag"] = "removed"
        self.check_no_errors()

    def test_dir_entry_cleared(self):
        # Clearing ot a directory's entry is an error
        self.grandchildentry.clear()
        self.check_errors([self.grandchilddir])

    def test_tree_added(self):
        # Adding a subtree is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        barentry["flag"] = "added"
        bazfile = os.path.join(bardir, "baz")
        self.baz = ["baz"]
        self.writefile(dumps(self.baz), bazfile, "wb")
        bazentry = self.getentry(bazfile)
        bazentry["flag"] = "added"
        burpdir = os.path.join(bardir, "burp")
        os.mkdir(burpdir)
        burpentry = self.getentry(burpdir)
        burpentry["flag"] = "added"
        self.check_no_errors()

    def test_tree_added_no_flag(self):
        # Adding a subtree without flagging everything as added is an error
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        barentry["flag"] = "added"
        bazfile = os.path.join(bardir, "baz")
        baz = ["baz"]
        self.writefile(dumps(baz), bazfile, "wb")
        bazentry = self.getentry(bazfile)
        bazentry["path"] = "/parent/child/bar/baz"
        burpdir = os.path.join(bardir, "burp")
        os.mkdir(burpdir)
        burpentry = self.getentry(burpdir)
        burpentry["path"] = "/parent/child/bar/burp"
        self.check_errors([bazfile, burpdir])

    def test_tree_removed(self):
        # Removing a subtree is okay
        shutil.rmtree(self.childdir)
        self.childentry["flag"] = "removed"
        self.grandchildentry.clear()
        self.fooentry.clear()
        self.check_no_errors()

    # TODO Extra and Annotations is not tested directly

    # TODO Changing directories into files or vice versa is not tested



class TestCheckAndCommit(TestCheckClass):

    # This class extends all tests from TestCheckClass that call
    # self.check_no_errors() to carry out the change and check on it.
    # Yes, this means that all the tests that call check_errors() are
    # repeated.  Big deal. :-)

    def __init__(self, name):
        TestCheckClass.__init__(self, name)
        self.name = name

    def setUp(self):
        TestCheckClass.setUp(self)
        self.committer = task.Commit(synchronizer.getSynchronizer, self.checker.repository)

    def check_no_errors(self):
        TestCheckClass.check_no_errors(self)
        self.committer.perform(self.parent, "", self.parentdir)
        name = "verify" + self.name[4:]
        method = getattr(self, name, None)
        if method:
            method()
        else:
            print "?", name

    def verify_vanilla(self):
        self.assertEqual(self.parent.keys(), ["child"])
        self.assertEqual(self.parent["child"], self.child)
        self.assertEqual(sort(self.child.keys()), ["foo", "grandchild"])
        self.assertEqual(self.child["foo"], self.foo)
        self.assertEqual(self.child["grandchild"], self.grandchild)
        self.assertEqual(self.grandchild.keys(), [])

    def verify_file_added(self):
        self.assertEqual(self.child["bar"], self.bar)
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])

    def verify_file_changed(self):
        self.assertEqual(self.child["foo"], self.newfoo)

    def verify_file_removed(self):
        self.assertEqual(self.child.keys(), ["grandchild"])

    def verify_file_spurious(self):
        self.verify_vanilla()

    def verify_file_type_changed(self):
        self.assertEqual(self.child["foo"], self.newfoo)

    def verify_file_unmodified_lost_originial(self):
        self.verify_vanilla()

    def verify_same_files_added_twice(self):
        self.assertEqual(self.child["bar"], self.bar)

    def verify_dir_removed(self):
        self.assertEqual(self.child.keys(), ["foo"])

    def verify_dir_added(self):
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])

    def verify_dir_spurious(self):
        self.verify_vanilla()

    def verify_tree_added(self):
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])
        bar = self.child["bar"]
        self.assertEqual(bar.__class__, PretendContainer)
        baz = bar["baz"]
        self.assertEqual(self.baz, baz)

    def verify_tree_removed(self):
        self.assertEqual(self.parent.keys(), [])


class ExampleFile(object):
    fixed_up1 = False
    fixed_up2 = False

    def __init__(self, data=''):
        self.data = data

class SynchronizerWithCB(synchronizer.FileSynchronizer):

    def load(self, readable):
        self.context.fixed_up1 = False
        self.context.fixed_up2 = False
        self.context.data = readable.read()
        return self.callback1

    def callback1(self):
        self.context.fixed_up1 = True
        return self.callback2

    def callback2(self):
        self.context.fixed_up2 = True

class SynchronizerWithBadCB(SynchronizerWithCB):

    def callback2(self):
        return self.callback1


class TestCallback(TestCheckClass):
    """
    Test that synchronizer callbacks work
    """

    def test_callback(self):
        # set up a synchronizer that provides callbacks
        zope.component.provideUtility(
            SynchronizerWithCB, interfaces.ISynchronizerFactory,
            name = synchronizer.dottedname(ExampleFile))

        # add a file that uses a cb synchronizer to the repo
        self.example_file = self.child['file.txt'] = ExampleFile()
        self.file_path = os.path.join(self.childdir, 'file.txt')
        entry = self.getentry(self.file_path)
        entry["path"] = "/parent/child/file.txt"
        entry["factory"] = "fake factory name"

        # make sure the before the commit the file is OK
        self.assertEqual(self.example_file.fixed_up1, False)
        self.assertEqual(self.example_file.fixed_up2, False)

        # update the file
        self.writefile('new data', self.file_path)

        # commit the changes
        committer = task.Commit(synchronizer.getSynchronizer,
                                self.checker.repository)
        committer.perform(self.parent, "", self.parentdir)

        # make sure that after the commit the fix ups have been done
        self.assertEqual(self.example_file.data, 'new data')
        self.assertEqual(self.example_file.fixed_up1, True)
        self.assertEqual(self.example_file.fixed_up2, True)

    def test_infinite_loop(self):
        # set up a synchronizer that provides bad callbacks
        zope.component.provideUtility(
            SynchronizerWithBadCB, interfaces.ISynchronizerFactory,
            name = synchronizer.dottedname(ExampleFile))

        # add a file that uses a cb synchronizer to the repo
        self.example_file = self.child['file.txt'] = ExampleFile()
        self.file_path = os.path.join(self.childdir, 'file.txt')
        entry = self.getentry(self.file_path)
        entry["path"] = "/parent/child/file.txt"
        entry["factory"] = "fake factory name"

        # update the file
        self.writefile('new data', self.file_path)

        # commit the changes
        committer = task.Commit(synchronizer.getSynchronizer,
                                self.checker.repository)

        # a synchronization error is raised
        self.assertRaises(task.SynchronizationError, committer.perform,
                          self.parent, "", self.parentdir)



def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestTaskModule))
    s.addTest(unittest.makeSuite(TestCommitClass))
    s.addTest(unittest.makeSuite(TestCheckinClass))
    s.addTest(unittest.makeSuite(TestCheckClass))
    s.addTest(unittest.makeSuite(TestCheckAndCommit))
    s.addTest(unittest.makeSuite(TestCallback))
    return s

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
