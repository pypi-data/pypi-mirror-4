try:
    import unittest2 as unittest
except ImportError:
    import unittest
from os.path import join, dirname, exists, isdir

from stanley import fs


class TestFs(unittest.TestCase):

    def setUp(self):
        # folder for writing test files etc.
        self.sbox = join(dirname(__file__), '_sandbox')

    def testCreateAndRemoveFile(self):
        testfile = join(self.sbox, 'testfile.txt')
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

    def testMkAndRmdirs(self):
        self.assertFalse(exists(join(self.sbox, 'testdir')))

        fs.mkdirs(join(self.sbox, 'testdir', 'testdirsub'))
        self.assertTrue(exists(join(self.sbox, 'testdir', 'testdirsub')))
        self.assertTrue(isdir(join(self.sbox, 'testdir', 'testdirsub')))
        fs.touch(join(self.sbox, 'testdir', 'testdirsub', 'test.txt'))

        fs.rmdir(join(self.sbox, 'testdir'))
        self.assertFalse(exists(join(self.sbox, 'testdir')))
