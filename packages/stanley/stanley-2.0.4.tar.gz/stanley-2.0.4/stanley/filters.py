# -*- coding: utf-8 -*-
""" Stanley Flat File Blog Tool
    ---------------------------
    author: Glen Swinfield <glen.swinfied@gmail.com>
    license: see LICENSE """


class Filter(object):

    """
    Filter and order set of content objects
    """

    def __init__(self, posts):
        self._posts = posts

    def posts(self, limit=None, category=None):
        posts = filter(lambda p: not p.draft, self._posts)
        posts = sorted(posts, key=lambda x: x.publish_date, reverse=True)
        if category is not None:
            posts = filter(lambda x: x.category in category, posts)

        if len(posts) < 1:
            return []

        if limit is not None:
            return posts[0:limit]

        return posts
