import os
import re

import markdown

from datetime import datetime


class ContentDataAttributeError(AttributeError):
    pass


class Content:
    """

    Parent class for content types i.e. Page & Post

    """

    POSTSPLIT = '^([0-9]{4}-[0-1][0-9]-[0-3][0-9])-+([a-zA-Z]+.*)(\.md)$'
    POSTMATCH = '^[0-9]{4}-[0-1][0-9]-[0-3][0-9]-+[a-zA-Z]+.*\.md$'

    template = None
    src_dir = None
    src_file = None
    content = None
    slug = None
    filename = None
    ext = None
    permalink = None
    draft = False
    data = None

    def __init__(self, src_dir='', src_file='', data={}, content=''):
	""" The src_dir argument is the path to the filename without the
	original source. """
	if 'template' not in data:
	    msg = '"template" is required in "%s"' % src_file
	    raise ContentDataAttributeError(msg)

	self.template = data.get('template')
	self.src_file = src_file
	self.src_dir = src_dir
	self.data = data
	self.process_filename()
	self.content = markdown.markdown(content)
	if 'draft' in data and data['draft'] is True:
	    self.draft = True
	self.permalink = self.set_permalink()

    def tojinja2(self):
        """ Prepare attributes to be passed to a Jinja template """
        filterlam = lambda (k, v): k not in ['data', 'src_dir', 'src_file']
        attributes = dict(filter(filterlam, self.__dict__.items()))
        attributes.update(self.data)
        return attributes

    def set_permalink(self):
        link = os.path.join(self.src_dir, self.slug)
        if link[0] != '/':
            return'/' + link
        return link

    @staticmethod
    def is_post_file(src):
        return re.match(Content.POSTMATCH, os.path.basename(src)) is not None

    def __getattr__(self, name, *args):
        """ Enable acess to attributes in data as if they were attributes of
        of this object. This makes templateing easier and ensures that data
        attributes from the front matter take precedence. """
        if name in self.data:
            return self.data.get(name)
        elif name in self.__dict__:
            return self.__dict__.get(name)

        raise AttributeError('Post has no attribute %s' % name)


class Post(Content):
    """

    Class that represents an individual post, als defines constants for
    patttern mathcing and spitting post filenames, and accessing post
    attributes

    """

    category = None
    publish_date = None

    def __init__(self, src_dir='', src_file='', data={}, content=''):
	""" The src_dir argument is the path to the filename without the
	original source. """
	Content.__init__(self, src_dir, src_file, data, content)
	self.category = self.src_dir

    def process_filename(self):
        """ Get publish_date, slug and dst filename for a post """
        splits = re.split(Content.POSTSPLIT, self.src_file)
        self.publish_date = datetime.strptime(splits[1], '%Y-%m-%d')
        self.slug = splits[2]
        self.filename = self.slug + '.html'
        self.ext = splits[3]


class Page(Content):
    """

    Represents a static page (i.e. not a post)

    """

    template = None
    src_dir = None
    src_file = None
    content = None
    slug = None
    filename = None
    ext = None
    permalink = None
    draft = False
    data = None

    def process_filename(self):
        """ slug and dst filename for a post """
        self.slug, self.ext = os.path.splitext(self.src_file)
        self.filename = self.slug + '.html'


class Posts:
    """

    Holds array of post objects and defines methods to filter and return
    subsets. This drives the listing of posts in the templates.

    Usage:
    ---------
    {% for post in posts.bycategory('blog').limit(5).result %}
    ... template block ...
    {% endfor %}

    """

    result = []

    def __init__(self, posts):
        self.result = posts

    def category(self, category):
        filter_ = lambda x: x.category == category
        return Posts(filter(filter_, self.result))

    def orderby(self, field, reverse):
        key = lambda k: getattr(k, field)
        return Posts(sorted(self.result, key=key, reverse=reverse))

    def limit(self, max):
	if len(self.result) < 1:
	    return Posts([])
	return Posts(self.result[0:max])

    def nodraft(self):
	filter_ = lambda x: x.draft is False
	return Posts(filter(filter_, self.result))
