import unittest
from os.path import join, dirname, exists

from stanley import fs


class TestFs(unittest.TestCase):

    def testCreateAndRemoveFile(self):
        testfile = join(dirname(__file__), '_test', 'testfile.txt')
        self.assertFalse(exists(testfile))
        fs.touch(testfile)
        self.assertTrue(exists(testfile))
        fs.rm(testfile)
        self.assertFalse(exists(testfile))

    def testUpath(self):
        paths = ['/this/is/cp/my/file', '/this/is/cp/my/file/test/test.txt']
        self.assertEqual(fs.upath(paths), 'test/test.txt')

        paths = ['/this/is/cp/my/file/', '/this/is/cp/my/file/test/test.txt']
        self.assertEqual(fs.upath(paths), 'test/test.txt')
