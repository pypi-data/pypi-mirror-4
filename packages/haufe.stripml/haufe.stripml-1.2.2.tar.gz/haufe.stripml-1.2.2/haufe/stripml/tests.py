# psf: ta=4, -*-Python-*-, vi: set et ts=4:
""" Testing

All of the tests can be found in the README.txt file.
"""

__docformat__ = 'restructuredtext'

import unittest
import doctest

def setUp(test):
    pass

def tearDown(test):
    pass

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt', setUp=setUp, tearDown=tearDown,
            optionflags = doctest.ELLIPSIS
            ),
        ))
