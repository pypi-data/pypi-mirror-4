import unittest
import os

import datetime

from stanley.parser import parse_yaml
from stanley.content import create_content


class TestSite(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.testdir = os.path.join(os.path.dirname(__file__), '_test')

    def testAttributes(self):
        expected_content = u'''<h1>Content Title</h1>\n<p>This is some content Lorem ipsum dolor sit amet, <em>consectetur</em></p>'''

        full_path = os.path.join(self.testdir, 'content/2013-01-10-some-test-content.md')
        split_path = '/2013-01-10-some-test-content.md'
        c = create_content(parse_yaml, {'full_path': full_path, 'split_path': split_path})
        self.assertEqual(c.data, {'pic': 'someotherpic.jpg', 'template': 'blog.html', 'title': 'Some Test Content'})
        self.assertEqual(c.content, expected_content.strip())
        self.assertEqual(c.category, '')
        self.assertEqual(c.filename, 'some-test-content.html')
        self.assertEqual(c.draft, False)
        self.assertEqual(c.permalink, '/some-test-content.html')
        self.assertEqual(c.template, 'blog.html')
        self.assertEqual(c.publish_date, datetime.datetime(2013, 1, 10, 0, 0))
        self.assertEqual(c.templatedata.keys(), [
            'category',
            'permalink',
            'title',
            'pic',
            'filename',
            'content',
            'draft',
            'template',
            'publish_date',
            'slug'])

    def testCategory(self):
        full_path = os.path.join(self.testdir, 'content/sub/2012-12-14-some-sub-content.md')
        split_path = '/sub/2012-12-14-some-sub-content.md'
        c = create_content(parse_yaml, {'full_path': full_path, 'split_path': split_path})
        self.assertEqual(c.category, 'sub')
        self.assertEqual(c.filename, 'sub/some-sub-content.html')
        self.assertEqual(c.permalink, '/sub/some-sub-content.html')
