import os
import datetime

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from stanley.site import Site
from stanley.config import Config
from stanley.parser import parse_yaml
from stanley import fs


class TestSite(unittest.TestCase):

    def testBuild(self):
        c = Config(os.path.join(os.path.dirname(__file__), '_test', 'config.yml'))
        s = Site(c, parse_yaml)
        # clear existing contents from destination directory
        if os.path.exists(c.destdir):
            fs.rmdir(c.destdir)

        # sanity check
        self.assertFalse(os.path.exists(c.destdir))

        fs.mkdirs(c.destdir)
        s.build(False)

        self.assertTrue(os.path.isdir(os.path.join(c.destdir, 'static')))
        self.assertTrue(os.path.isdir(os.path.join(c.destdir, 'static', 'css')))
        self.assertTrue(os.path.isdir(os.path.join(c.destdir, 'static', 'img')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'static', 'css', 'styles.css')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'static', 'img', 'pic.jpg')))
        self.assertTrue(os.path.isdir(os.path.join(c.destdir, 'sub')))
        self.assertTrue(os.path.isdir(os.path.join(c.destdir, 'sub', 'sub')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'index.html')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'sub', 'index.html')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'sub', 'sub', 'index.html')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'some-test-content.html')))
        self.assertTrue(os.path.isfile(os.path.join(c.destdir, 'sub', 'some-sub-content.html')))
