###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: text.py 3018 2012-08-06 13:50:52Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.text

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


JAVASCRIPT = """
<script type="text/javascript">
  $("#%s").j01Placeholder();
</script>
"""


class TextWidget(z3c.form.browser.text.TextWidget):
    """text widget Input type text widget implementation."""

    zope.interface.implementsOnly(interfaces.ITextWidget)

    klass = u'text'
    value = u''

    hint = None
    placeholder = None

    @property
    def css(self):
        """Returns a CSS layout wrapper class name"""
        if self.hint is not None:
            # use hint as css class if hint is given
            return u'hint'
        else:
            # use text as css class
            return 'text'

    def extract(self, default=z3c.form.interfaces.NO_VALUE):
        """Return NO_VALUE if value is placeholder """
        value = self.request.get(self.name, default)
        if self.placeholder == value:
            # return empty string
            return u''
        else:
            # return default or NO_VALUE
            return value

    @property
    def javascript(self):
        if self.placeholder is not None:
            return JAVASCRIPT % self.id


# get
@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getTextWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return z3c.form.widget.FieldWidget(field, TextWidget(request))


def getPlaceholderWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
    widget.placeholder = zope.i18n.translate(field.title, context=request)
    return widget


def getHintWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
    widget.hint = zope.i18n.translate(field.description, context=request)
    return widget


def getPlaceholderHintWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
    widget.placeholder = zope.i18n.translate(field.title, context=request)
    widget.hint = zope.i18n.translate(field.description, context=request)
    return widget


# setup
def setUpTextWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(TextWidget, **kw)


def setUpHintWidget(**kw):
    """Create widget with field.description as hint"""
    # widget condition
    assert kw.get('hint', None) is None
    def getAndSetupWidget(field, request):
        # return real widget
        widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
        widget.hint = zope.i18n.translate(field.description, context=request)
        for name, value in kw.items():
            setattr(widget, name, value)
        return widget
    return getAndSetupWidget


def setUpPlaceholderWidget(**kw):
    """Create widget with field.title as placeholder"""
    # widget condition
    assert kw.get('placeholder', None) is None
    def getAndSetupWidget(field, request):
        # return real widget
        widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
        widget.placeholder = zope.i18n.translate(field.title,
            context=request)
        for name, value in kw.items():
            setattr(widget, name, value)
        return widget
    return getAndSetupWidget


def setUpPlaceholderHintWidget(**kw):
    """Create widget with field.title as placeholder"""
    # widget condition
    assert kw.get('hint', None) is None
    assert kw.get('placeholder', None) is None
    def getAndSetupWidget(field, request):
        # return real widget
        widget = z3c.form.widget.FieldWidget(field, TextWidget(request))
        widget.hint = zope.i18n.translate(field.description, context=request)
        widget.placeholder = zope.i18n.translate(field.title,
            context=request)
        for name, value in kw.items():
            setattr(widget, name, value)
        return widget
    return getAndSetupWidget
