import unittest
from os.path import join, dirname

from yaml.scanner import ScannerError

from stanley.config import Config


class TestConfig(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.fixtures = join(dirname(__file__), '_test')

    def testNoExceptionOnNonexistentFile(self):
        # absorb missing file exceptions
        testfile = '/a/test/path/idonotexist.yml'
        Config(testfile)

    def testInvalidYamlFile(self):
        # ensure YAML errors are raised
        testfile = join(self.fixtures, 'invalid.yml')
        self.assertRaises(ScannerError, Config, testfile)

    def testConfigPaths(self):
        testfile = '/a/test/path/config.yml'
        testdir = '/a/test/path'
        conf = Config(testfile)

        self.assertEqual(conf.root, testdir)
        self.assertEqual(conf.sourcedir, join(testdir, 'content'))
        self.assertEqual(conf.destdir, join(testdir, 'site'))
        self.assertEqual(conf.staticdir, join(testdir, 'static'))
        self.assertEqual(conf.deststaticdir, join(testdir, 'site/static'))
        self.assertEqual(conf.templatedir, join(testdir, 'templates'))

    def testGetter(self):
        testfile = join(self.fixtures, 'config.yml')
        expected = {'site_title': 'My Test Site', 'static': '/static'}
        conf = Config(testfile)
        self.assertEqual(getattr(conf, 'global'), expected)
