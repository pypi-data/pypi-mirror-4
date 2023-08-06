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
"""Demo Interfaces
"""
import os
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from z3c.form import field
from z3c.formui import form
from z3c.formwidget.ckeditor import richtext, ckeditor

FAVICON_PATH = os.path.join(os.path.dirname(__file__), 'favicon.ico')

class FavIcon(object):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'image/x-icon')
        with open(FAVICON_PATH, 'rb') as img:
            return img.read()

class IArticle(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=u'Title'
        )

    teaser = richtext.RichText(
        title=u'Teaser'
        )

    body = richtext.RichText(
        title=u'Body'
        )


@zope.interface.implementer(IArticle)
class Article(object):

    title = FieldProperty(IArticle['title'])
    body = FieldProperty(IArticle['body'])


ARTICLE = Article()
ARTICLE.title = u'CKEditor Demo'
ARTICLE.body = u'This is <b>the</b> CKEditor demo.'


MinimalCKEditorWidget = ckeditor.CKEditorFieldWidgetFactory(
    {'toolbar': 'Basic', 'uiColor': '#9AB8F3'})


class DemoForm(form.EditForm):

    label = u'Edit CKEditor Article'
    fields = field.Fields(IArticle)
    fields['teaser'].widgetFactory = MinimalCKEditorWidget

    def getContent(self):
        return ARTICLE
