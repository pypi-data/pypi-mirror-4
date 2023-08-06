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
"""Tests for the Interface Documentation Module
"""
import doctest
import re
import unittest
import zope.component
import zope.testing.module

import zope.component.testing
from zope.component.interfaces import IFactory
from zope.interface import implements, Interface
from zope.location import LocationProxy
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import IContainmentRoot

from zope.renderer.rest import ReStructuredTextSourceFactory
from zope.renderer.rest import IReStructuredTextSource
from zope.renderer.rest import ReStructuredTextToHTMLRenderer

from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 renamed the builtins dict.
    (re.compile('__builtin__'),
     r"builtins"),
    ])


def setUp(test):
    zope.component.testing.setUp()
    # Register Renderer Components
    zope.component.provideUtility(
        ReStructuredTextSourceFactory, IFactory,
        'zope.source.rest')
    # Cheat and register the ReST renderer as the STX one as well.
    zope.component.provideUtility(
        ReStructuredTextSourceFactory, IFactory,
        'zope.source.stx')
    zope.component.provideAdapter(
        ReStructuredTextToHTMLRenderer, provides=Interface)
    zope.testing.module.setUp(test, 'zope.apidoc.doctest')


def tearDown(test):
    zope.component.testing.tearDown()
    zope.testing.module.tearDown(test)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
                'classregistry.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE, checker=checker),
        doctest.DocFileSuite(
                'interface.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE, checker=checker),
        doctest.DocFileSuite(
                'component.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE, checker=checker),
        doctest.DocFileSuite(
                'presentation.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE, checker=checker),
        doctest.DocFileSuite(
                'utilities.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE, checker=checker),
        ))
