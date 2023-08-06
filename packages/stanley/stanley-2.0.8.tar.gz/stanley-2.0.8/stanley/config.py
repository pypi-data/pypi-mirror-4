# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import yaml


class Config(object):

    """
    Represents a site's configuration.
    """

    def __init__(self, config_file):
        try:
            with open(config_file, 'r') as f:
                self._parameters = yaml.load(f.read())
        except IOError:
            self._parameters = {}
        self._root = os.path.dirname(config_file)
        self._sourcedir = os.path.join(self.root, 'content')
        self._staticdir = os.path.join(self.root, 'static')
        self._destdir = os.path.join(self.root, 'site')
        self._deststaticdir = os.path.join(self._destdir, 'static')
        self._templatedir = os.path.join(self.root, 'templates')

    @property
    def parameters(self):
        " Returns a dictionary of config parameters. "
        return self._parameters

    @property
    def root(self):
        " Returns the absolute path to the project root directory. "
        return self._root

    @property
    def sourcedir(self):
        " Returns an absolute path to the content/source directory. "
        return self._sourcedir

    @property
    def staticdir(self):
        " Returns an absolute path to the staic files directory. "
        return self._staticdir

    @property
    def destdir(self):
        " Returns an absolute path to the destination/site directory. "
        return self._destdir

    @property
    def deststaticdir(self):
        " Return an absolute path to the static folder inside the destdir. "
        return self._deststaticdir

    @property
    def templatedir(self):
        " Returns an absolute path to the templates directory. "
        return self._templatedir

    def __getattr__(self, name):
        if name in self._parameters:
            return self._parameters.get(name)
        raise AttributeError('Config has no attribute %s' % name)
