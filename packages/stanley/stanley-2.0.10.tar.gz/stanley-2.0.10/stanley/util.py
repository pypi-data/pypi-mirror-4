# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import argparse

from flask import Flask

from stanley.parser import parse_yaml
from stanley.site import Site, ContentNotFoundException
from stanley.config import Config
from stanley import fs


def init(path):
    """
    Initialize a default site structure
    """
    basepath = os.path.dirname(path)
    if not os.path.exists(basepath):
        os.makedirs(basepath)
    if not os.path.exists(path):
        fs.touch(path)
    if not os.path.exists(os.path.join(basepath, 'content')):
        os.mkdir(os.path.join(basepath, 'content'))

    if not os.path.exists(os.path.join(basepath, 'site')):
        os.mkdir(os.path.join(basepath, 'site'))

    if not os.path.exists(os.path.join(basepath, 'templates')):
        os.mkdir(os.path.join(basepath, 'templates'))

    if not os.path.exists(os.path.join(basepath, 'static')):
        os.mkdir(os.path.join(basepath, 'static'))


def build(path, less):
    """
    Take the content and build into static html pages
    """
    c = Config(path)
    s = Site(c, parse_yaml)
    # clear existing contents from destination directory
    try:
        fs.rmdir(c.destdir)
    except AttributeError:
        pass
    fs.mkdirs(c.destdir)
    s.build(less)


def runserver(config_path):
    """
    Run a server
    """
    config = Config(config_path)
    site = Site(config, parse_yaml)
    app = Flask(import_name=__name__, static_folder=config.staticdir, static_url_path='/static', template_folder=config.templatedir, instance_path=config.root)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        content_filter = site.get_content_filter()
        try:
            content = site.get_content_by_url(path)
            return site.compile(content, content_filter)
        except ContentNotFoundException:
            return 'requested content "%s" could not be found' % path, 404
    app.run(debug=True)


class Cli(object):

    """
    The CLI command runner
    """

    def run(self):
        """
        Take CLI arguments and do stuff
        """

        parser = argparse.ArgumentParser(description='Manage your sites')

        parser.add_argument('--init', '-i',
                    action='store_true',
                    help='Initialize a site')

        parser.add_argument('--build', '-b',
                    action='store_true',
                    help='Initialize a site')

        parser.add_argument('--server', '-s',
                    action='store_true',
                    help='Run a basic server to view site')

        parser.add_argument('--file', '-f',
                    action='store',
                    help='Specifies the path to the config file',
                    required=True)

        parser.add_argument('--less', '-l',
            action='store_true',
            help='Compile LESS files to css (requires that Less is installed')

        args = parser.parse_args()

        if args.init is True:
            init(os.path.abspath(args.file))
        if args.server is True:
            runserver(os.path.abspath(args.file))
        elif args.build is True:
            print '\nBuilding %s' % os.path.abspath(args.file)
            print u'----------------------------------------'
            build(os.path.abspath(args.file), args.less)
