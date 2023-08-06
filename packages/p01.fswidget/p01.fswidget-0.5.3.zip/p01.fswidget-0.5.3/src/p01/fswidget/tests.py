###############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: tests.py 3713 2013-04-08 10:25:34Z adam.groszer $
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'cleanupfilename.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        ),
    ))
