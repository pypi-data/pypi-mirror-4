##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Base Components test setup

$Id: tests.py 129508 2013-02-20 03:40:24Z srichter $
"""
__docformat__ = "reStructuredText"
import doctest
import re
import unittest
from zope.testing import renormalizing
from zope.testing.doctestunit import DocFileSuite, pprint

checker = renormalizing.RENormalizing([
    # Python 2 unicode strings add a "u".
    (re.compile("u('.*?')"),
     r"\1"),
    # Python 3 renamed type to class.
    (re.compile("<type "),
     r"<class "),
    ])


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     globs={'pprint': pprint}, checker=checker
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
