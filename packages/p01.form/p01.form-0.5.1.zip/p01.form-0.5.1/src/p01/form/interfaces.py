###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""interfaces

"""
__docformat__ = "reStructuredText"

import zope.schema
import zope.interface
import zope.i18nmessageid

import z3c.form.interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


# forms
class IForm(zope.interface.Interface):
    """Simple form"""

    refreshWidgets = zope.schema.Bool(
        title=u'Refresh widgets',
        description=(u'A flag, when set, causes form widgets to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)

    refreshActions = zope.schema.Bool(
        title=u'Refresh actions',
        description=(u'A flag, when set, causes form actions to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)


class IDisplayForm(IForm, z3c.form.interfaces.IDisplayForm):
    """Display Form"""


class IAddForm(IForm, z3c.form.interfaces.IAddForm):
    """Add form."""


class IEditForm(IForm, z3c.form.interfaces.IEditForm):
    """Edit form."""


class ISearchForm(IForm, z3c.form.interfaces.IForm):
    """Search form."""


# widgets
# text
class ITextWidget(z3c.form.interfaces.ITextWidget):
    """Text widget with placeholder and hint support"""

    hint = zope.schema.Text(
        title=u'Hint',
        description=u'Hint',
        default=None,
        required=False)

    placeholder = zope.schema.TextLine(
        title=u'Placeholder',
        description=u'Placeholder',
        default=None,
        required=False)


# checkbox
class ICheckBoxWidget(z3c.form.interfaces.ICheckBoxWidget):
    """Checbox widget."""


class ISingleCheckBoxWidget(ICheckBoxWidget,
    z3c.form.interfaces.ISingleCheckBoxWidget):
    """Single Checbox widget."""


# file
class IFileWidget(z3c.form.interfaces.IFileWidget):
    """File widget."""


# password
class IPasswordWidget(ITextWidget, z3c.form.interfaces.IPasswordWidget):
    """Password widget with placeholder and hint support"""


# password confirmation
class PasswordComparsionError(zope.schema.ValidationError):
    __doc__ = _("""Password doesn't compare with confirmation value""")


class IPasswordConfirmationWidget(z3c.form.interfaces.ITextWidget):
    """Password including confirmation field widget."""


# radio
class IRadioWidget(z3c.form.interfaces.IRadioWidget):
    """Radio widget."""


# select
class ISelectWidget(z3c.form.interfaces.ISelectWidget):
    """Select widget with ITerms option."""


class IMultiSelectWidget(ISelectWidget):
    """Multi select widget"""


class IGroupSelectWidget(ISelectWidget):
    """Select widget with optgroup support"""


# text lines
class ITextLinesWidget(z3c.form.interfaces.ITextLinesWidget):
    """Text lines widget."""


# textarea
class ITextAreaWidget(z3c.form.interfaces.ITextAreaWidget):
    """Text widget."""


# dictionary
class IDictKeyValueWidget(z3c.form.interfaces.ITextAreaWidget):
    """Dict with key:value values as textarea widget."""
