""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import yaml


class Site(object):
    """
    Represents a site. Generates content objects from filestructure
    """
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            f = open(config_file, 'w+')
            f.close()
        self.config = config_file
        self._root = os.path.dirname(config_file)
        self._content = []
        for root, sub_folders, files in os.walk(self.sourcedir):
            for filename in files:
                source = os.path.join(root, filename)
                self._content.append({
                    'full_path': source,
                    'split_path': source.replace(self.sourcedir, '')})

    @property
    def config(self):
        " Returns a dictionary of config parameters. "
        return self._config

    @config.setter
    def config(self, value):
        """
        Takes an absolute path to a YAML file and parses it into a
        dictionary.
        """
        with open(value, 'r') as f:
            self._config = yaml.load(f.read())
            if self._config is None:
                self._config = {}

    @property
    def root(self):
        " Returns the absolute path to the project root directory. "
        return self._root

    @property
    def sourcedir(self):
        " Returns an absolute path to the content/source directory. "
        return os.path.join(self.root, 'content')

    @property
    def staticdir(self):
        " Returns an absolute path to the staic files directory. "
        return os.path.join(self.root, 'static')

    @property
    def destdir(self):
        " Returns an absolute path to the destination/site directory. "
        return os.path.join(self.root, 'site')

    @property
    def deststaticdir(self):
        " Return an absolute path to the static folder inside the destdir. "
        return os.path.join(self.destdir, 'static')

    @property
    def templatedir(self):
        " Returns an absolute path to the templates directory. "
        return os.path.join(self.root, 'templates')

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content.append(value)
