###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: textarea.py 3018 2012-08-06 13:50:52Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.textarea

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


class TextAreaWidget(z3c.form.browser.textarea.TextAreaWidget):
    """Textarea widget implementation."""

    zope.interface.implementsOnly(interfaces.ITextAreaWidget)

    klass = u'textarea'
    css = u'textarea'
    value = u''


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextAreaWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextAreaWidget(request))


# setup
def setUpTextAreaWidget(**kw):
    """Returns a widget getter method supporting given hint and placeholder"""
    return setUpWidget(TextAreaWidget, **kw)
