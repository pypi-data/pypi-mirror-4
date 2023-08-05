import os
import unittest
import shutil

from datetime import datetime

from stanley import Compile
from stanley import ContentParseException
from stanley import Post
from stanley import Page
from stanley import Posts


class TestCompile(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/compileTest')  # use fixtures dir as project root
        self.comp = Compile(os.path.join(self.fixtures_dir, 'config.yml'))
        self.dst_dir = os.path.join(self.fixtures_dir, 'site')
        self.src_dir = os.path.join(self.fixtures_dir, 'content')
        self.static = os.path.join(self.dst_dir, 'static')
        for root, dirs, files in os.walk(self.dst_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def testGetAllFiles(self):
        files = self.comp.get_all_files()
        expected = [
            os.path.join(self.src_dir, '2012-03-12-another-test-file.md'),
            os.path.join(self.src_dir, '2012-12-11-this-is-a-test-file.md'),
            os.path.join(self.src_dir, 'index.md'),
            os.path.join(self.src_dir, 'blog/index.md'),
            os.path.join(self.src_dir, 'blog/blog_sub/index.md')]

        self.assertEqual(files, expected)

    def testParseFileContent(self):
        expectedNoContent = {
            'content': '',
            'data': {
            'permalink': 'http://atest.com',
            'title': 'This is the title',
            'template': 'test.html'}
        }
        expectedContent = {
            'content': 'This is some content',
            'data': {'permalink': 'http://atest.com',
            'title': 'This is the title',
            'template': 'test.html'}
        }
        with open(os.path.join(self.src_dir, '2012-12-11-this-is-a-test-file.md'), 'r') as f1:
            self.assertEqual(self.comp.parse_file_content(f1.read()), expectedNoContent)

        with open(os.path.join(self.src_dir, '2012-03-12-another-test-file.md'), 'r') as f2:
            self.assertEqual(self.comp.parse_file_content(f2.read()), expectedContent)

    def testGenerateSite(self):
        self.comp.generate_site()

	# posts generated properly
	for post in self.comp.jinja2env.globals.get('posts').result:
	    self.assertTrue(os.path.exists(os.path.join(self.fixtures_dir, 'site', post.src_dir, post.filename)))

	# static files generated
	self.assertTrue(os.path.exists(os.path.join(self.fixtures_dir, 'site/index.html')))

	# no unexpected files
	expected = []
	for root, dirs, files in os.walk(self.dst_dir):
	    for f in files:
		expected.append(os.path.join(root, f))

	self.assertEqual(7, len(expected), "5 + 2 css/js files")

        self.assertTrue(os.path.exists(self.static))
        self.assertTrue(os.path.exists(os.path.join(self.static, 'css/nice.css')))
        self.assertTrue(os.path.exists(os.path.join(self.static, 'js/nice.js')))


class TestCompileExceptions(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.fixtures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/exceptionsTest')  # use fixtures dir as project root
        self.comp = Compile(os.path.join(self.fixtures_dir, 'config.yml'))
        self.dst_dir = os.path.join(self.fixtures_dir, 'site')
        self.src_dir = os.path.join(self.fixtures_dir, 'content')
        for root, dirs, files in os.walk(self.dst_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def testDataFrom(self):
        with self.assertRaises(ContentParseException):
            self.comp.parse_file_content('asfasfJUNK8789')
