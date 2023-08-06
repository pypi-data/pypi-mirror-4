import unittest
import zope.fssync.synchronizer

class TestSynchronizer(unittest.TestCase):

    def test_missing_synchronizer(self):
        self.assertRaises(zope.fssync.synchronizer.MissingSynchronizer,
                          zope.fssync.synchronizer.getSynchronizer,
                          object(), True)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSynchronizer))
    return suite
