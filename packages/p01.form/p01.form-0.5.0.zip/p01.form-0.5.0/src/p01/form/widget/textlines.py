##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: textlines.py 3144 2012-10-10 21:56:27Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.textlines

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


class TextLinesWidget(z3c.form.browser.textlines.TextLinesWidget):
    """Textarea widget implementation."""

    zope.interface.implementsOnly(interfaces.ITextLinesWidget)

    klass = u'textlines'
    css = u'textlines'
    value = u''


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextLinesWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextLinesWidget(request))


# setup
def setUpTextLinesWidget(**kw):
    """Returns a widget getter method supporting given hint and placeholder"""
    return setUpWidget(TextLinesWidget, **kw)
