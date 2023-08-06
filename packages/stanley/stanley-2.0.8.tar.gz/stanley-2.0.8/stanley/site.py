# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import re
import shutil
import datetime

from os import walk, system
from os.path import join, basename, splitext, exists

from jinja2 import Environment, ChoiceLoader, FileSystemLoader
from werkzeug.contrib.cache import SimpleCache

from stanley.jinjaext import FragmentCacheExtension
from stanley.content import Page, Post
from stanley.filters import Filter
from stanley import fs


class ContentNotFoundException(Exception):
    pass


class Site(object):

    def __init__(self, config, parser):
        self.config = config
        self.parser = parser
        self.posts = []
        self.pages = []

        cl = ChoiceLoader([FileSystemLoader(self.config.templatedir)])
        self.env = Environment(loader=cl, extensions=[FragmentCacheExtension])
        self.env.fragment_cache = SimpleCache()

        try:
            self.env.globals.update({'global': getattr(self.config, "global")})
        except AttributeError:
            pass
        self.env.globals.update({'datetime': datetime.datetime})

    def _copynoncontent(self, src, upath):
        dst = join(self.config.destdir, upath)
        shutil.copyfile(src, dst)

    def _build_content_lists(self):
        postpattern = '^[0-9]{4}-[0-1][0-9]-[0-3][0-9]-+[a-zA-Z]+.*\.md$'
        self.posts = []
        self.pages = []
        for r, s, f in walk(self.config.sourcedir):
            for filename in f:
                src = join(r, filename)
                base = basename(src)
                ext = splitext(base)[1]
                upath = fs.upath([self.config.sourcedir, src])
                if ext != '.md':
                    self._copynoncontent(src, upath)
                elif re.match(postpattern, base) is not None:
                    p = Post(self.parser, src, upath)
                    self.posts.append(p)
                else:
                    p = Page(self.parser, src, upath)
                    self.pages.append(p)

    def get_content_by_url(self, url):
        for c in self.posts + self.pages:
            if c.permalink[1:] == url:
                return c
        raise ContentNotFoundException

    def get_content_filter(self):
        """ Get basic front matter data and title etc for all posts
        This is used in server mode to generate data for the posts filter
        without having to build the whole site on every page refresh

        @return Filter"""
        self._build_content_lists()
        return Filter(self.posts)

    def compile(self, content, content_filter):
        template_obj = self.env.get_template(content.template)
        data = content.templatedata
        data.update({'posts': content_filter})
        compiled_content = template_obj.render(data)
        return compiled_content.encode('ascii', 'xmlcharrefreplace')

    def build(self, less=False):
        self._build_content_lists()
        content_filter = Filter(self.posts)
        for content in self.posts + self.pages:
            dst_file = join(self.config.destdir, content.filename)
            compiled_content = self.compile(content, content_filter)
            fs.mkdirs(dst_file)
            with open(dst_file, 'w+') as dst:
                dst.write(compiled_content)

        if less is True:
            cmd = "lessc %s > %s -x"
            lesscnf = self.config.less
            lesscom = cmd % (lesscnf.get('src'), lesscnf.get('dst'))
            system(lesscom)

        if exists(self.config.deststaticdir):
            shutil.rmtree(self.config.deststaticdir)
        shutil.copytree(self.config.staticdir, self.config.deststaticdir)
