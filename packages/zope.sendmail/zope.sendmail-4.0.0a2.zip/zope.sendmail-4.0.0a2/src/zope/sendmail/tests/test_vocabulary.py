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
"""Mail delivery names vocabulary test
"""
import unittest
from doctest import DocTestSuite
from zope.component.testing import setUp, tearDown

def test_suite():
    return unittest.TestSuite([
        DocTestSuite('zope.sendmail.vocabulary',
                     setUp=setUp, tearDown=tearDown),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
