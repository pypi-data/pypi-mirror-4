# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import yaml


class InvalidContentException(Exception):
    pass


def parse_yaml(src_file):
    with open(src_file, 'r') as f:
        blocks = f.read().split('---', 2)
        if len(blocks) is not 3:
            raise InvalidContentException("Content file could not be parsed %s" % src_file)
        front_matter = yaml.load(blocks[1])
        content = blocks[2].strip()

    return {'front_matter': front_matter, 'content': unicode(content, 'utf-8')}
