# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import re
import shutil
import datetime

from os import walk, system, makedirs
from os.path import join, basename, splitext, commonprefix, exists, dirname

from jinja2 import Environment, ChoiceLoader, FileSystemLoader
from werkzeug.contrib.cache import SimpleCache

from stanley.jinjaext import FragmentCacheExtension
from stanley.content import Page, Post
from stanley.filters import Filter


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

    def _copynoncontent(self, src, cp):
        dst = join(self.config.destdir, src.replace(cp, ''))[1:]
        shutil.copyfile(src, dst)

    def _build_content_lists(self):
        postpattern = '^[0-9]{4}-[0-1][0-9]-[0-3][0-9]-+[a-zA-Z]+.*\.md$'
        for r, s, f in walk(self.config.sourcedir):
            for filename in f:
                src = join(r, filename)
                base = basename(src)
                ext = splitext(base)[1]
                cp = commonprefix([src, self.config.sourcedir])
                if ext != '.md':
                    self._copynoncontent(src, cp)
                elif re.match(postpattern, base) is not None:
                    p = Post(self.parser, src, src.replace(cp, ''))
                    self.posts.append(p)
                else:
                    p = Page(self.parser, src, src.replace(cp, ''))
                    self.pages.append(p)

    def build(self, less=False):
        self._build_content_lists()
        contentfilter = Filter(self.posts)
        for content in self.posts + self.pages:
            dst_file = join(self.config.destdir, content.filename)
            template_obj = self.env.get_template(content.template)
            data = content.templatedata
            data.update({'posts': contentfilter})
            compiled_content = template_obj.render(data)
            if not exists(dirname(dst_file)):
                makedirs(dirname(dst_file))
            with open(dst_file, 'w+') as dst:
                dst.write(compiled_content.encode('ascii', 'xmlcharrefreplace'))

        if less is True:
            cmd = "lessc %s > %s -x"
            lesscnf = self.config.less
            lesscom = cmd % (lesscnf.get('src'), lesscnf.get('dst'))
            system(lesscom)

        if exists(self.config.deststaticdir):
            shutil.rmtree(self.config.deststaticdir)
        shutil.copytree(self.config.staticdir, self.config.deststaticdir)
