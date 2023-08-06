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
"""Demo Itnerfaces
"""
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.interfaces import IViewletManager
from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer
from z3c.formui.interfaces import IDivFormLayer, ICSS
from z3c.formwidget.ckeditor.interfaces import IJavaScript

class IDemoBrowserLayer(IBrowserRequest):
    """Demo Browser Layer"""

class IDemoBrowserSkin(IFormLayer,
                       IDivFormLayer,
                       IDemoBrowserLayer,
                       IPageletBrowserLayer):
    """Skin for demo browser."""


class ICSS(ICSS):
    """CSS viewlet manager."""

class IJavaScript(IJavaScript):
    """JavaScript viewlet manager."""
