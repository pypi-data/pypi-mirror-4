##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from zope.testing import setupstack
import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import unittest

def test_funky_option_types():
    """
    We can supply unicode and int option values and they're stringified:

    >>> import zc.metarecipe.testing
    >>> buildout = zc.metarecipe.testing.Buildout()
    >>> recipe = zc.metarecipe.Recipe(buildout, '', {})
    >>> recipe['s'] = dict(o1=1, o2=u'foo', o3='bar')
    [s]
    o1 = 1
    o2 = foo
    o3 = bar

    Other types are not OK:

    >>> recipe['x'] = dict(o1=1.0)
    Traceback (most recent call last):
    ...
    TypeError: Invalid type: <type 'float'> for x:o1, 1.0

    """

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.txt',
            setUp=setupstack.setUpDirectory, tearDown=setupstack.tearDown,
            ),
        doctest.DocTestSuite(),
        ))

