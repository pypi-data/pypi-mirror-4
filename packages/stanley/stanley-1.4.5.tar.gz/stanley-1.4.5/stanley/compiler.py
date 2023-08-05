# -*- coding: utf-8 -*-
"""
    stanley
    ~~~~~~~~~
    Flat file cms/blog tool

    :copyright: (c) 2013 by Glen Swinfield <glen.swinfield@gmail.com>

"""

import os
import yaml
import shutil
from jinja2 import Environment, ChoiceLoader, FileSystemLoader

from stanley import Page, Post, Posts


class TemplateException(Exception):
    """
    Thrown when template cannot be found
    """
    pass


class NoTemplateSpecified(TemplateException):
    """
    Thrown when a content file has no template specified in it's front_matter
    """
    pass


class ContentException(Exception):
    pass


class ContentParseException(ContentException):
    pass


class Compile:
    """

    Methods for taking a project directory and compiling into flat html

    """

    rootdir = None
    sourcedir = None
    destdir = None
    staticdir = None
    jinja2env = None
    config = None

    def __init__(self, config_file):
        self.config_file = config_file
        self.rootdir = project_root = os.path.dirname(config_file)
        self.sourcedir = os.path.join(project_root, 'content')
        self.destdir = os.path.join(project_root, 'site')
        self.staticdir = os.path.join(project_root, 'static')
        self.config = self.set_config()
        self.set_jinja2env()
        self.jinja2env.globals.update(self.config)

    def set_jinja2env(self):
        """ Create Jinja2 Environment with template loaded """
        self.jinja2env = Environment(loader=ChoiceLoader([
            FileSystemLoader(os.path.join(self.rootdir, 'templates'))]))

    def set_config(self):
        """ Parse YAML config file """
        with open(self.config_file, 'r') as config:
	    config = yaml.load(config.read())
	    if config is not None:
		return config
	    else:
		return {}

    def parse_file_content(self, filecontent):
        """ Get front_matter and content from a post file content """
        blocks = filecontent.split('---')
        if len(blocks) is not 3:
            raise ContentParseException("Content file could not be parsed")
        front_matter = yaml.load(blocks[1])
        return {'data': front_matter, 'content': blocks[2].strip()}

    def create_post(self, postpath):
        """ Create a Post object from a post file. """
        src_dir = os.path.dirname(postpath).replace(self.sourcedir, '')
        src_file = os.path.basename(postpath)
        with open(postpath, 'r') as f:
            contents = self.parse_file_content(f.read())
        return Post(
            src_dir=src_dir,
            src_file=src_file,
            data=contents.get('data'),
            content=contents.get('content'))

    def create_page(self, pagepath):
        """ Create a Page object from a post file. """
        src_dir = os.path.dirname(pagepath).replace(self.sourcedir, '')
        src_file = os.path.basename(pagepath)
        with open(pagepath, 'r') as f:
            contents = self.parse_file_content(f.read())
        return Page(
            src_dir=src_dir,
            src_file=src_file,
            data=contents.get('data'),
            content=contents.get('content'))

    def prepare(self):
        """ Clears out the output directory ready for the site to be
        re-compiled into it """
        for root, dirs, files in os.walk(self.destdir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    def get_all_files(self):
        """ Get a list of all of the files in the source directory. """
        filelist = []
        for root, sub_folders, files in os.walk(self.sourcedir):
            for filename in files:
                filelist.append(os.path.join(root, filename))
        return filelist

    def generate_site(self):
        """ Compile the flat html site and copy static files. """
        self.prepare()

        is_post = lambda x: Post.is_post_file(x)
        posts = map(self.create_post, filter(is_post, self.get_all_files()))

        is_page = lambda x: not Post.is_post_file(x)
        pages = map(self.create_page, filter(is_page, self.get_all_files()))

        self.jinja2env.globals.update({
            'posts': Posts(posts)
        })

        for item in posts + pages:
            if len(item.src_dir) > 0 and item.src_dir[0] == '/':
                src_dir = item.src_dir[1:]
            else:
                src_dir = item.src_dir
            dst_file = os.path.join(self.destdir, src_dir, item.filename)

            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file))

            template = self.jinja2env.get_template(item.template)
            with open(dst_file, 'w+') as dst:
                dst.write(template.render(item.tojinja2()))

        staticdst = os.path.join(self.destdir, 'static')
        if os.path.exists(staticdst):
            shutil.rmtree(staticdst)
        shutil.copytree(self.staticdir, staticdst)
        return self.jinja2env.globals.get('posts')
