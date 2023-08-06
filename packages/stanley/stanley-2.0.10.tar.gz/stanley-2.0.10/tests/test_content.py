import os
import datetime

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from stanley.content import Post
from stanley.parser import parse_yaml


class TestContent(unittest.TestCase):

    def setUp(self):
        self.fixtures = os.path.join(os.path.dirname(__file__), '_test')

    def testPost(self):
        splitpath = os.path.join('2013-01-10-some-test-content.md')
        path = os.path.join(self.fixtures, 'content', splitpath)
        templatedata = {
            'category': '',
            'content': u'<h1>Content Title</h1>\n<p>This is some content Lorem ipsum dolor sit amet, <em>consectetur</em></p>',
            'draft': False,
            'filename': 'some-test-content.html',
            'permalink': '/some-test-content.html',
            'pic': 'someotherpic.jpg',
            'publish_date': datetime.datetime(2013, 1, 10, 0, 0),
            'slug': 'some-test-content',
            'template': 'blog.html',
            'title': 'Some Test Content'}
        p = Post(parse_yaml, path, splitpath)

        self.assertEqual(p.publish_date, datetime.datetime(2013, 1, 10, 0, 0))
        self.assertEqual(p.template, 'blog.html')
        self.assertEqual(p.content, u'<h1>Content Title</h1>\n<p>This is some content Lorem ipsum dolor sit amet, <em>consectetur</em></p>')
        self.assertEqual(p.draft, False)
        self.assertEqual(p.permalink, '/some-test-content.html')
        self.assertEqual(p.templatedata, templatedata)
        self.assertEqual(p.category, '')
        self.assertEqual(p.slug, 'some-test-content')
        self.assertEqual(p.ext, '.md')

        # test that fromt matter data is accessible as if it were an attribute of the instance
        self.assertEqual(p.pic, 'someotherpic.jpg')

    def testPostSubFolder(self):
        " Sub folder content must have a category "
        splitpath = os.path.join('sub', '2012-12-14-some-sub-content.md')
        path = os.path.join(self.fixtures, 'content', splitpath)
        p = Post(parse_yaml, path, splitpath)

        self.assertEqual(p.category, 'sub')
        self.assertEqual(p.slug, 'some-sub-content')
        self.assertEqual(p.ext, '.md')
