""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import yaml


def parse_yaml(src_file):
    with open(src_file, 'r') as f:
        blocks = f.read().split('---')
        if len(blocks) is not 3:
            raise Exception("Content file could not be parsed")
        front_matter = yaml.load(blocks[1])
        content = blocks[2].strip()

    return {'front_matter': front_matter, 'content': content}
