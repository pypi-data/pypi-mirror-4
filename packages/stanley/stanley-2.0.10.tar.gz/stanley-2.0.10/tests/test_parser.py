import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from stanley.parser import parse_yaml, InvalidContentException


class TestParser(unittest.TestCase):

    def setUp(self):
        self.fixtures = os.path.join(os.path.dirname(__file__), '_fixtures')

    def testExceptionOnUnparsable(self):
        testfile = os.path.join(self.fixtures, 'noblocks.md')
        self.assertRaises(InvalidContentException, parse_yaml, testfile)

    def testParse(self):
        testfile = os.path.join(self.fixtures, 'valid.md')
        expected = {
            'content': u'# Content Title\n\nThis is some content Lorem ipsum dolor sit amet, _consectetur_',
            'front_matter': {'pic': 'someotherpic.jpg',
            'template': 'blog.html',
            'title': 'Some Test Content'}
        }
        self.assertEqual(parse_yaml(testfile), expected)
