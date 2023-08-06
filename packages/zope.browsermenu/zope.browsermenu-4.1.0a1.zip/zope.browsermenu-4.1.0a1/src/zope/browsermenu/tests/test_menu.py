##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Browser Menu Item Tests
"""
import doctest
import pprint
import re
import unittest
from zope.testing import cleanup, renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 changed builtins name.
    (re.compile('__builtin__'),
     r"builtins"),
    # Python 3 renamed type to class.
    (re.compile('<type'),
     r"<class"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.configuration.exceptions.ConfigurationError"),
     r"ConfigurationError"),
    ])

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             setUp=lambda test:cleanup.setUp(),
                             tearDown=lambda test:cleanup.tearDown(),
                             globs={'pprint': pprint.pprint},
                             checker=checker,
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))
