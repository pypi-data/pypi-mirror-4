##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the fssync package's documentation files

$Id: test_docs.py 70826 2006-10-20 03:41:16Z baijum $
"""
import os
import unittest
import zope
import py

from zope import interface
from zope.testing import doctest, doctestunit, module, cleanup


from zope.traversing.interfaces import IContainmentRoot

from zope.fssync import pickle
from zope.fssync.pickle import TLocation

_test_dirs = []

TESTDIR = os.path.dirname(__file__)

def cleanUpZope(test):
    for wcdir in _test_dirs:
        wcdir.remove()
    cleanup.cleanUp()

def svn_test_checkout():
    base = py.path.svnwc(TESTDIR).mkdir('svntestdir')
    pat = 'test%s'
    count = 1
    while base.join(pat % count).check():
        count += 1
    name = pat % count
    wcdir = py.path.svnwc(base).mkdir(name)
    _test_dirs.append(base)
    return wcdir

def rel_paths(checkout, paths):
    result = []
    start = len(str(checkout))
    for path in paths:
        result.append(str(path)[start:])
    return sorted(result)

def setUp(test):
    module.setUp(test, 'zope.fssync.doctest')

def tearDown(test):
    module.tearDown(test, 'zope.fssync.doctest')
    cleanUpZope(test)

class PersistentLoaderTestCase(unittest.TestCase):

    def setUp(self):
        root = TLocation()
        interface.directlyProvides(root, IContainmentRoot)
        o1 = TLocation(); o1.__parent__ = root; o1.__name__ = 'o1'
        o2 = TLocation(); o2.__parent__ = root; o2.__name__ = 'o2'
        o3 = TLocation(); o3.__parent__ = o1; o3.__name__ = 'o3'
        root.o1 = o1
        root.o2 = o2
        o1.foo = o2
        o1.o3 = o3
        self.root = root
        self.o1 = o1
        self.o2 = o2

    def testPathPersistentLoader(self):

        pickler = pickle.StandardUnpickler(self.o1)
        loader = pickle.PathPersistentLoader(pickler)
        self.assert_(loader.load('/') is self.root)
        self.assert_(loader.load('/o2') is self.o2)

#     def testParentPersistentLoader(self):
#         loader = pickle.ParentPersistentLoader(self.o1, self.o1)
#         self.assert_(loader.load(fspickle.PARENT_MARKER) is self.o1)
#         self.assert_(loader.load('/') is self.root)
#         self.assert_(loader.load('/o2') is self.o2)


def test_suite():

    globs = {'zope':zope,
            'pprint': doctestunit.pprint,
            'svn_test_checkout': svn_test_checkout,
            'rel_paths': rel_paths}

    flags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    suite = unittest.TestSuite()

    suite = unittest.makeSuite(PersistentLoaderTestCase)
    suite.addTest(doctest.DocTestSuite('zope.fssync.pickle'))


    suite.addTest(doctest.DocFileSuite('../README.txt',
                                            globs=globs,
                                            setUp=setUp, tearDown=tearDown,
                                            optionflags=flags))

    suite.addTest(doctest.DocFileSuite('../caseinsensitivity.txt',
                                            globs=globs,
                                            setUp=setUp, tearDown=tearDown,
                                            optionflags=flags))

    suite.addTest(doctest.DocFileSuite('../generic.txt',
                                            globs=globs,
                                            setUp=setUp, tearDown=tearDown,
                                            optionflags=flags))

    if '.svn' in os.listdir(TESTDIR):
        suite.addTest(doctest.DocFileSuite('../svn.txt',
                                           globs=globs,
                                           setUp=setUp, tearDown=tearDown,
                                           optionflags=flags))

    return suite

if __name__ == '__main__':
    unittest.main(default='test_suite')
