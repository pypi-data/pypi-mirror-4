# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import argparse
import shutil

from twisted.web.server import Site as twistedsite
from twisted.web.static import File
from twisted.internet import reactor

from stanley.parser import parse_yaml
from stanley.site import Site
from stanley.compiler import Jinja2Compiler
from stanley import touch


def init(path):
    """
    Initialize a default site structure
    """
    basepath = os.path.dirname(path)
    if not os.path.exists(basepath):
        os.makedirs(basepath)
    if not os.path.exists(path):
        touch(path)
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
    s = Site(path)
    # clear existing contents from destination directory
    for root, dirs, files in os.walk(s.destdir + '/*'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    c = Jinja2Compiler(s, parse_yaml)
    return c.compile(less)


def server(path):
    """
    Run a server
    """
    resource = File(os.path.join(os.path.dirname(path), 'site'))
    factory = twistedsite(resource)
    reactor.listenTCP(8080, factory)
    reactor.run()


def sitemap():
    """
    Generate a google sitemap
    """
    pass


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
            help='Compile Les files to css (requires that Less is installed')

        args = parser.parse_args()

        if args.init is True:
            init(args.file)
        if args.server is True:
            server(args.file)
        elif args.build is True:
            print '\nBuilding %s' % args.file
            print u'----------------------------------------'
            (built, total) = build(args.file, args.less)
            sitemap()
            for f in built:
                print '* ' + f
            print u'----------------------------------------'
            print 'built %d of %d files' % (len(built), total)
            print u'----------------------------------------'
