###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH
# All Rights Reserved.
#
###############################################################################
"""Wrapper setup

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.location
import zope.schema
from zope.schema.fieldproperty import FieldProperty

import z3c.form.interfaces
import z3c.form.action
import z3c.form.widget
import z3c.form.browser.widget


class ICSSButton(z3c.form.interfaces.IButton):
    """CSSButton"""

    css = zope.schema.Field(
        title=u'CSS class',
        description=u'CSS class',
        required=False)

class ICSSButtonAction(z3c.form.interfaces.IButtonAction):
    """CSSButton action"""

class ICSSButtonWidget(z3c.form.interfaces.IButtonWidget):
    """CSSButton widget"""


class CSSButton(zope.schema.Field):
    """A button with a custom css class attribute"""

    zope.interface.implements(ICSSButton)

    accessKey = FieldProperty(ICSSButton['accessKey'])
    actionFactory = FieldProperty(ICSSButton['actionFactory'])
    css = FieldProperty(ICSSButton['css'])

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # apply optional css, which get added in front of other classes
        if 'css' in kwargs:
            self.css = kwargs['css']
            del kwargs['css']
        # Extract button-specific arguments
        self.accessKey = kwargs.pop('accessKey', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super(CSSButton, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.title)


class CSSButtonWidget(z3c.form.browser.widget.HTMLInputWidget,
    z3c.form.widget.Widget):
    """Button which prepends and not appends css classes
    
    This button widget also uses the css attribute defined in buttons.

    """
    zope.interface.implementsOnly(ICSSButtonWidget)

    klass = u'button-widget'

    def addClass(self, klass):
        """We will prepend css classes and not append like z3c.form"""
        if not self.klass:
            # just a single class
            self.klass = unicode(klass)
        else:
            # prepend and not append new classes
            classes = klass.split() + self.klass.split()
            seen = {}
            unique = []
            for item in classes:
                if item in seen:
                    continue
                seen[item]=1
                unique.append(item)
            self.klass = u' '.join(unique)

    def update(self):
        # We do not need to use the widget's update method, because it is
        # mostly about ectracting the value, which we do not need to do.
        # get all css classes
        if not self.klass:
            self.klass = ''
        classes = self.klass.split()
        if self.required and 'required' not in classes:
            # append required at the end
            classes.apend('required')
        if self.field.css:
            # make sure items are not repeated and prepend css classes
            classes = self.field.css.split() + classes
        # make sure every class is unique
        seen = {}
        unique = []
        for item in classes:
            if item in seen:
                continue
            seen[item]=1
            unique.append(item)
        self.klass = u' '.join(unique)


class CSSButtonAction(z3c.form.action.Action, CSSButtonWidget,
    zope.location.Location):

    zope.interface.implements(ICSSButtonAction)
    zope.component.adapts(z3c.form.interfaces.IFormLayer, ICSSButton)

    def __init__(self, request, field):
        z3c.form.action.Action.__init__(self, request, field.title)
        CSSButtonWidget.__init__(self, request)
        self.field = field

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')

    # access css from button
    @property
    def css(self):
        return self.field.css


class CSSButtonActionHandler(z3c.form.action.ActionHandlerBase):
    zope.component.adapts(
        z3c.form.interfaces.IHandlerForm,
        zope.interface.Interface,
        zope.interface.Interface,
        ICSSButtonAction)

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)
