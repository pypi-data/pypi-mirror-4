###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: widget.py 3004 2012-08-06 02:01:18Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.i18n

import z3c.form.widget


def setUpWidget(factory, **kw):
    """Returns a widget factory getter method supporting kw arguments
    
    The widget also supports hint and placeholder including translation

    """
    # widget condition
    hint = kw.pop('hint', None)
    placeholder = kw.pop('placeholder', None)
    def getAndSetupWidget(field, request):
        # return real widget
        widget = z3c.form.widget.FieldWidget(field, factory(request))
        if hint is not None:
            widget.hint = zope.i18n.translate(hint, context=request)
        if placeholder is not None:
            widget.placeholder = zope.i18n.translate(placeholder,
                context=request)
        for name, value in kw.items():
            setattr(widget, name, value)
        return widget
    return getAndSetupWidget
