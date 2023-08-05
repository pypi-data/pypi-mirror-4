###############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: tests.py 3162 2012-11-11 04:34:42Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest

from z3c.form import testing

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('dictionary.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite('password.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
