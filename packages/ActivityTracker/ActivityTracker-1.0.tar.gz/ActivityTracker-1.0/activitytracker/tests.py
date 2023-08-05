import unittest
import doctest

optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


def test_suite():
    modules = []
    for x in 'base', 'cli', 'plugins.orgmode':
        modules.append(__import__('activitytracker.' + x, {}, {}, x))
    return unittest.TestSuite([doctest.DocTestSuite(x, optionflags=optionflags)
                               for x in modules])
