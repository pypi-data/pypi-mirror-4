try:
    import unittest2 as unittest
except ImportError:
    import unittest

from datetime import date, timedelta

from stanley.filters import Filter


class TestFilter(unittest.TestCase):

    """
    Test the post filtering class tat filters posts for
    template tags
    """

    def testPosts(self):

        class mockPost(object):

            def __init__(self, publish_date, category, draft=False):
                self.publish_date = publish_date
                self.category = category
                self.draft = draft

        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)

        posttoday = mockPost(today, 'test1')
        postyesterday = mockPost(yesterday, '')
        posttomorrow = mockPost(tomorrow, 'test2')

        # should never appear in results
        posttomorrowdraft = mockPost(tomorrow, 'test2', True)

        posts = [posttoday, posttomorrow, postyesterday, posttomorrowdraft]

        posts_dateordered = [posttomorrow, posttoday, postyesterday]

        f = Filter(posts)
        self.assertEqual(f.posts(), posts_dateordered)
        self.assertEqual(f.posts(category=['test1']), [posttoday])
        self.assertEqual(f.posts(category=['test1', 'test2']), [posttomorrow, posttoday])
        self.assertEqual(f.posts(category=['test1', 'test2'], limit=1), [posttomorrow])
        self.assertEqual(f.posts(category=[''], limit=5), [postyesterday])
        self.assertEqual(f.posts(limit=2), [posttomorrow, posttoday])
        self.assertEqual(f.posts(limit=10), posts_dateordered)
