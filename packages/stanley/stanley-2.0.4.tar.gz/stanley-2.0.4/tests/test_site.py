import unittest
import os

from stanley.site import Site


class TestSite(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.testdir = os.path.join(os.path.dirname(__file__), '_test')
        self.s = Site(os.path.join(self.testdir, 'config.yml'))

    def testEmptyConfig(self):
        s = Site(os.path.join(self.testdir, 'empty_config.yml'))
        self.assertEqual(s.config, {})

    def testNonEmptyConfig(self):
        s = self.s
        self.assertEqual(s.config, {'global': {'site_title': 'My Test Site', 'static': '/static'}})
        self.assertEqual(s.root, self.testdir)
        self.assertEqual(s.sourcedir, os.path.join(self.testdir, 'content'))
        self.assertEqual(s.destdir, os.path.join(self.testdir, 'site'))
        self.assertEqual(s.staticdir, os.path.join(self.testdir, 'static'))
        self.assertEqual(s.deststaticdir, os.path.join(self.testdir, 'site/static'))
        self.assertEqual(s.templatedir, os.path.join(self.testdir, 'templates'))
        self.assertEqual(len(s.content), 6)

        expected_files = [
            {
                'full_path': os.path.join(self.testdir, 'content', '2013-01-10-some-test-content.md'),
                'split_path': '/2013-01-10-some-test-content.md'
            },
            {
                'full_path': os.path.join(self.testdir, 'content', 'index.md'),
                'split_path': '/index.md'
            },
            {
                'full_path': os.path.join(self.testdir, 'content', 'sub/index.md'),
                'split_path': '/sub/index.md'
            },
            {
                'full_path': os.path.join(self.testdir, 'content', 'sub/sub/2013-01-20-some-sub-sub-cotnent.md'),
                'split_path': '/sub/sub/2013-01-20-some-sub-sub-cotnent.md'
            },
            {
                'full_path': os.path.join(self.testdir, 'content', 'sub/sub/index.md'),
                'split_path': '/sub/sub/index.md'
            },
            {
                'full_path': os.path.join(self.testdir, 'content', 'sub/2012-12-14-some-sub-content.md'),
                'split_path': '/sub/2012-12-14-some-sub-content.md'
            }]
        self.assertItemsEqual(s.content, expected_files)
