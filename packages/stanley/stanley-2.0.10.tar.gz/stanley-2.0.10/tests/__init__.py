import os.path
try:
    import unittest2 as unittest
except ImportError:
    import unittest


def get_tests():
    start_dir = os.path.dirname(__file__)
    return unittest.TestLoader().discover(start_dir, pattern="*.py")
