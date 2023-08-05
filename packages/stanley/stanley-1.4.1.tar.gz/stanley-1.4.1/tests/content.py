import os
import unittest

from datetime import datetime

from stanley import Compile
from stanley import ContentParseException
from stanley import Post
from stanley import Page
from stanley import Posts


class TestPost(unittest.TestCase):

    def testMagicGetter(self):
	post = Post(src_dir='/ths/is/src', src_file='2012-12-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content')
	self.assertEqual(post.one, 'foo')

    def testIsPost(self):
	self.assertTrue(Post.is_post_file('2012-12-12-a-filename.md'))
	self.assertTrue(Post.is_post_file('2012-12-12-a-filename-2012-11-10.md'))
	self.assertTrue(Post.is_post_file('1998-12-12-a.md'))

	self.assertFalse(Post.is_post_file('202-12-12-a-filename.md'))
	self.assertFalse(Post.is_post_file('202-12-12-a-filename.txt'))
	self.assertFalse(Post.is_post_file('202-12-12-a-filename.html'))
	self.assertFalse(Post.is_post_file('202-12-12filename.txt'))
	self.assertFalse(Post.is_post_file('202-12-12--filename.md'))
	self.assertFalse(Post.is_post_file('202-12-12_-filename.md'))

    def testProcessFilename(self):
	post = Post('cats/blog', '2012-12-01-this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	post.process_filename()
	self.assertEqual(post.slug, 'this-is-the-filename')
	self.assertEqual(post.filename, 'this-is-the-filename.html')
	self.assertEqual(post.publish_date,  datetime(2012, 12, 1, 0, 0))
	self.assertEqual(post.ext, '.md')
	self.assertEqual(post.content, '<p><em>mdcontent</em></p>')
	self.assertFalse(post.draft)

    def testPermalink(self):
	post = Post('/cats/blog', '2012-12-01-this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	self.assertEqual(post.permalink, '/cats/blog/this-is-the-filename')
	post = Post('cats/blog', '2012-12-01-this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	self.assertEqual(post.permalink, '/cats/blog/this-is-the-filename')

    def testTojinja2(self):
	post = Post(src_dir='/ths/is/src', src_file='2012-12-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content')
	self.assertEqual(post.tojinja2(), {
	    'category': '/ths/is/src',
	    'content': u'<p>This is content</p>',
	    'ext': '.md',
	    'filename': 'myfile.html',
	    'one': 'foo',
	    'permalink': '/ths/is/src/myfile',
	    'publish_date': datetime(2012, 12, 12, 0, 0),
	    'slug': 'myfile',
	    'template': 'test.html',
	    'two': 'bar'})


class TestPage(unittest.TestCase):

    def testMagicGetter(self):
	page = Page(src_dir='/ths/is/src', src_file='myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content')
	self.assertEqual(page.one, 'foo')

    def testProcessFilename(self):
	page = Page('cats/blog', 'this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	page.process_filename()
	self.assertEqual(page.slug, 'this-is-the-filename')
	self.assertEqual(page.filename, 'this-is-the-filename.html')
	self.assertEqual(page.ext, '.md')
	self.assertEqual(page.content, '<p><em>mdcontent</em></p>')
	self.assertFalse(page.draft)

    def testPermalink(self):
	page = Page('/cats/blog', 'this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	self.assertEqual(page.permalink, '/cats/blog/this-is-the-filename')
	page = Page('cats/blog', 'this-is-the-filename.md', {'template': 'test.html'}, '_mdcontent_')
	self.assertEqual(page.permalink, '/cats/blog/this-is-the-filename')

    def testTojinja2(self):
	page = Page(src_dir='/ths/is/src', src_file='myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content')
	self.assertEqual(page.tojinja2(), {
	    'content': u'<p>This is content</p>',
	    'ext': '.md',
	    'filename': 'myfile.html',
	    'one': 'foo',
	    'permalink': '/ths/is/src/myfile',
	    'slug': 'myfile',
	    'template': 'test.html',
	    'two': 'bar'})


class TestPosts(unittest.TestCase):

    def testFilters(self):
	posts_ = []
	posts_.append(Post(src_dir='/blog', src_file='2012-12-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar', 'draft': True}, content='This is content'))
	posts_.append(Post(src_dir='/blog/food', src_file='2012-12-21-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content'))
	posts_.append(Post(src_dir='', src_file='2012-10-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content'))
	posts_.append(Post(src_dir='/cats/dogs/humans', src_file='2012-09-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content'))
	posts_.append(Post(src_dir='/blog', src_file='2012-08-12-myfile.md', data={'template': 'test.html', 'one': 'foo', 'two': 'bar'}, content='This is content'))

	posts = Posts(posts_)
	self.assertEqual(posts.nodraft().result, [posts_[1], posts_[2], posts_[3], posts_[4]])
	self.assertEqual(posts.category('/blog').result, [posts_[0], posts_[4]])
	self.assertEqual(posts.limit(2).result, [posts_[0], posts_[1]])
	self.assertEqual(posts.limit(4).result, [posts_[0], posts_[1], posts_[2], posts_[3]])
	self.assertEqual(posts.limit(4).result, [posts_[0], posts_[1], posts_[2], posts_[3]])
	self.assertEqual(posts.orderby('publish_date', True).result, [posts_[1], posts_[0], posts_[2], posts_[3], posts_[4]])
