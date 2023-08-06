##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""CKEditor widget test setup
"""
import doctest
import os.path
import unittest
import zope.component
import zope.interface
import zope.schema
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form import widget, testing
from z3c.formwidget.ckeditor import ckeditor, interfaces

def setUp(test):
    # Setup z3c.form basic setup
    testing.setUp(test)
    testing.setupFormDefaults()
    # CKEditor setup
    template = os.path.join(os.path.dirname(__file__), 'ckeditor_input.pt')
    factory = widget.WidgetTemplateFactory(
        template, widget=interfaces.ICKEditorWidget)
    zope.component.provideAdapter(factory, name='input')
    zope.component.provideAdapter(ckeditor.CKEditorFieldWidget)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp, tearDown=testing.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))
