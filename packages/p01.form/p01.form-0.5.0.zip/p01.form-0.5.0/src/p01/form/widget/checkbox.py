##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Checkbox widget with div tag separation
$Id: checkbox.py 3162 2012-11-11 04:34:42Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface

import z3c.form.widget
import z3c.form.browser.checkbox

from p01.form import interfaces
from p01.form.widget.widget import setUpWidget


class CheckBoxWidget(z3c.form.browser.checkbox.CheckBoxWidget):
    """Input type checkbox widget implementation using div instead of span tag.
    """

    zope.interface.implementsOnly(interfaces.ICheckBoxWidget)

    klass = u'checkbox'
    css = u'checkbox'


class DivCheckBoxWidget(CheckBoxWidget):
    """CheckBoxWidget using a div wrapper for option tags"""


class SingleCheckBoxWidget(z3c.form.browser.checkbox.SingleCheckBoxWidget):
    """Input type checkbox widget implementation using div instead of span tag.
    """

    zope.interface.implementsOnly(interfaces.ISingleCheckBoxWidget)

    klass = u'checkbox'
    css = u'checkbox'


class SingleDivCheckBoxWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget using a div wrapper for option tags"""


class SingleCheckBoxWithoutLabelWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget widget without label.
    
    This widget is usabel in a table cell where you provide a table header
    and don't like to repeat the checkbox label in each cell
    """

    klass = u'single-checkbox-without-label'


# get
def getCheckBoxWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, CheckBoxWidget(request))


def getDivCheckBoxWidget(field, request):
    """IFieldWidget factory for DivCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, DivCheckBoxWidget(request))


def getSingleCheckBoxWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, SingleCheckBoxWidget(request))


def getSingleDivCheckBoxWidget(field, request):
    """IFieldWidget factory for SingleDivCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, SingleDivCheckBoxWidget(request))


def getSingleCheckBoxWithoutLabelWidget(field, request):
    """IFieldWidget factory for SingleDivCheckBoxWidget."""
    widget = z3c.form.widget.FieldWidget(field,
        SingleCheckBoxWithoutLabelWidget(request))
    widget.label = u'' # don't show the label (twice)
    return widget


# setup
def setUpCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(CheckBoxWidget, **kw)


def setUpDivCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(DivCheckBoxWidget, **kw)


def setUpSingleCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleCheckBoxWidget, **kw)


def setUpSingleDivCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleDivCheckBoxWidget, **kw)


def setUpSingleCheckBoxWithoutLabelWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleCheckBoxWithoutLabelWidget, **kw)
