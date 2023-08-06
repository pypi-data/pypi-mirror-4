""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

from os import path, makedirs, system
import shutil
import datetime

from jinja2 import Environment, ChoiceLoader, FileSystemLoader
from werkzeug.contrib.cache import SimpleCache

from stanley.jinjaext import FragmentCacheExtension
from stanley.content import create_content, Post, InvalidContentTypeError
from stanley.filters import Filter


class Compiler(object):

    """
    Basic compiler class
    """

    def __init__(self, site):
        self.site = site

    def compile(self, content):
        raise AttributeError('compile has not been defined')


class Jinja2Compiler(Compiler):

    """
    Simple compiler that uses Jinja2 templates
    """

    def __init__(self, site, parser, *kwargs):
        Compiler.__init__(self, site)
        self.parser = parser
        cl = ChoiceLoader([FileSystemLoader(site.templatedir)])
        self.env = Environment(loader=cl, extensions=[FragmentCacheExtension])
        self.env.fragment_cache = SimpleCache()
        if 'global' in site.config:
            self.env.globals.update({
                'global': site.config.get('global')})
        self.env.globals.update({'datetime': datetime.datetime})

    def _generate_content_lists(self):
        """
        Loop over the site content and generate a list of content objects and
        a list of non content objects (e.g .txt. files)
        Returns a dict {'contents': [], 'noncontents': []}
        """
        contents = []
        noncontents = []
        for paths in self.site.content:
            try:
                content = create_content(self.parser, paths)
                contents.append(content)
                dst_file = path.join(self.site.destdir, content.filename)
                if not path.exists(path.dirname(dst_file)):
                    makedirs(path.dirname(dst_file))
            except InvalidContentTypeError:
                noncontents.append({
                        'full_path': paths.get('full_path'),
                        'split_path': paths.get('split_path')[1:]})

        return {'contents': contents, 'noncontents': noncontents}

    def compile(self, less):
        """
        Take the contents of the site and compie it into .html files
        Copy across all non markdown files as-is
        """
        noncontents, contents = self._generate_content_lists().values()
        contentfilter = Filter(filter(lambda x: isinstance(x, Post), contents))
        t = len(contents)
        built = []
        for content in contents:
            dst_file = path.join(self.site.destdir, content.filename)
            template_obj = self.env.get_template(content.template)
            data = content.templatedata
            data.update({'posts': contentfilter})
            compiled_content = template_obj.render(data)
            with open(dst_file, 'w+') as dst:
                dst.write(compiled_content)
                built.append(content.filename)

        for noncontent in noncontents:
            dst_file = path.join(self.site.destdir, noncontent.get('split_path'))
            shutil.copyfile(noncontent.get('full_path'), dst_file)

        if less is True:
            cmd = "lessc %s > %s -x"
            lesscnf = self.site.config.get('less')
            lesscom = cmd % (lesscnf.get('src'), lesscnf.get('dst'))
            system(lesscom)

        if path.exists(self.site.deststaticdir):
            shutil.rmtree(self.site.deststaticdir)
        shutil.copytree(self.site.staticdir, self.site.deststaticdir)

        return (built, t)
