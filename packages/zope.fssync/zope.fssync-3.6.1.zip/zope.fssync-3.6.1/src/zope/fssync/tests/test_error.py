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
"""Tests for the Error class.

(This is slightly non-trivial because it has a bunch of conveniences.)

$Id: test_error.py 25177 2004-06-02 13:17:31Z jim $
"""

import unittest

from zope.fssync.fsutil import Error

class TestError(unittest.TestCase):

    def test_plain(self):
        for sample in "hello", "hello %s world", "hello %% world":
            self.assertEqual(str(Error(sample)), sample)

    def test_format(self):
        for args in [("foo %r bar", "spam"),
                     ("foo %s bar", "spam"),
                     ("foo %r %r bar", "spam", "spam")]:
            self.assertEqual(str(Error(*args)), args[0] % args[1:])

    def test_implied_repr(self):
        self.assertEqual(str(Error("foo", "bar", "spam")),
                         "foo %r %r" % ("bar", "spam"))

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestError)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
