# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """

import os
import shutil


def touch(f):
    " Create an empty file "
    open(f, 'w+').close()


def rmdir(d):
    " Recursively remove a directory "
    if not os.path.isdir(d):
        raise AttributeError('Path is not s directory')
    shutil.rmtree(d, ignore_errors=True)


def rm(path):
    " Remove a file "
    os.unlink(path)


def upath(paths):
    """ returns the right/unique portion of path[1] once the common prefix
    has been removed """
    replaceme = os.path.commonprefix(paths)
    newpath = paths[1].replace(replaceme, '')
    if newpath.startswith(os.sep):
        return newpath[1:]
    return newpath


def mkdirs(path):
    """ Create directories in a path
    assumes files have an extension """
    if os.path.basename(path) != '' and os.path.splitext(path)[1] != '':
        path = os.path.dirname(path)
    if not os.path.exists(path):
        os.makedirs(path)
