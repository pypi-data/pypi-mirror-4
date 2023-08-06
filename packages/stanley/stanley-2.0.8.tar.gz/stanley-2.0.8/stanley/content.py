    # -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import re

import markdown
from datetime import datetime


class InvalidContentTypeError(AttributeError):
    pass


class AttributeInvalidForContentTypeError(AttributeError):
    pass


class Content(object):

    """

    Abstract, extend and implement parse_filename()

    """

    def __init__(self, parser, full_path='', split_path=''):
        parsed = parser(full_path)
        self.data = parsed.get('front_matter')
        if 'template' not in self.data:
            msg = '"template" is required in "%s"' % full_path
            raise AttributeError(msg)
        self._content = parsed.get('content')
        self.src_file = full_path
        self.parse_filename()
        self._category = os.path.dirname(split_path)
        cat_and_slug = os.path.join(self.category, self.slug)
        if 'ext' in self.data:
            self.filename = cat_and_slug + self.data.get('ext')
        else:
            self.filename = cat_and_slug + '.html'

    @property
    def template(self):
        return self.data.get('template')

    @property
    def content(self):
        return markdown.markdown(self._content)

    @property
    def draft(self):
        return 'draft' in self.data and self.data['draft'] is True

    @property
    def permalink(self):
        " Permalinks always begin with a slash "
        return '/' + self.filename

    @property
    def templatedata(self):
        " Prepare attributes to be passed to a template. "
        d = self.data
        d.update({
            'permalink': self.permalink,
            'content': self.content,
            'draft': self.draft,
            'category': self.category,
            'filename': self.filename,
            'slug': self.slug
            })
        return d

    @property
    def category(self):
        if self._category.startswith('/'):
            return self._category[1:]
        return self._category

    def parse_filename(self):
        " To be implemented by concrete class. "
        raise AttributeError('parse_filename has not been implemented')

    def __getattr__(self, name, *args):
        """ Enable acess to attributes in data as if they were attributes of
        of this object. This makes templateing easier and ensures that data
        attributes from the front matter take precedence. """
        if name in self.data:
            return self.data.get(name)

        raise AttributeError('Post has no attribute %s' % name)


class Post(Content):

    """

    Represents a datetime stamped post

    """

    DATESPLIT = '^([0-9]{4}-[0-1][0-9]-[0-3][0-9])-+([a-zA-Z]+.*)(\.md)$'

    def parse_filename(self):
        splits = re.split(self.DATESPLIT, os.path.basename(self.src_file))
        self._publish_date = datetime.strptime(splits[1], '%Y-%m-%d')
        self.slug = splits[2]
        self.ext = splits[3]

    @property
    def publish_date(self):
        return self._publish_date

    @property
    def templatedata(self):
        " Prepare attributes to be passed to a template. "
        d = Content.templatedata.__get__(self)
        d.update({'publish_date': self.publish_date})
        return d


class Page(Content):

    """

    Represents a page - has no timestamp/publsh_date

    """

    def parse_filename(self):
        self.slug, self.ext = os.path.splitext(os.path.basename(self.src_file))

    @property
    def publish_date(self):
        raise AttributeInvalidForContentTypeError
