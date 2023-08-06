###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Password widget
$Id: select.py 3018 2012-08-06 13:50:52Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.i18n
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.select

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


class SelectWidget(z3c.form.browser.select.SelectWidget):
    """Select widget implementation."""

    zope.interface.implementsOnly(interfaces.ISelectWidget)

    klass = u'select'
    css = u'select'
    prompt = False


class MultiSelectWidget(SelectWidget):
    """Select widget implementation."""

    zope.interface.implementsOnly(interfaces.IMultiSelectWidget)

    prompt = False
    size = 5
    multiple = 'multiple'


class GroupSelectWidget(SelectWidget):
    """Select widget with optgroup support"""

    zope.interface.implementsOnly(interfaces.IGroupSelectWidget)

    def appendSubTerms(self, groupName, items, subTerms, count):
        """Append collected sub terms as optgroup subItems"""
        subItems = []
        for subTerm in subTerms:
            id = '%s-%i' % (self.id, count)
            content = zope.i18n.translate(subTerm.title,
                context=self.request, default=subTerm.title)
            subItems.append(
                {'id': id,
                 'value': subTerm.token,
                 'content': content,
                 'selected': self.isSelected(subTerm)})
        items.append({'isGroup': True,
                      'content': groupName,
                      'subItems': subItems})

    @property
    def items(self):
        if self.terms is None:
            # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'isGroup': False,
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        # setup optgroup and option items
        groupName = None
        subTerms = []
        for count, term in enumerate(self.terms):
            if term.isGroup:
                if groupName is not None and subTerms:
                    self.appendSubTerms(groupName, items, subTerms, count)
                     # set empty subTerms list
                    subTerms = []
                # set as next groupName
                groupName = zope.i18n.translate(term.title,
                    context=self.request, default=term.title)
            else:
                # collect sub item terms
                subTerms.append(term)

        # render the last collected sub terms with the latest groupName 
        if groupName is not None:
            self.appendSubTerms(groupName, items, subTerms, count)

        return items


# adapter
@zope.component.adapter(zope.schema.interfaces.IChoice, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def ChoiceWidgetDispatcher(field, request):
    """Dispatch widget for IChoice based also on its source."""
    return zope.component.getMultiAdapter((field, field.vocabulary, request),
                                          z3c.form.interfaces.IFieldWidget)


@zope.component.adapter(zope.schema.interfaces.IChoice,
                        zope.interface.Interface, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SelectFieldWidget(field, source, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CollectionSelectFieldWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, MultiSelectWidget(request))


@zope.component.adapter(
    zope.schema.interfaces.IUnorderedCollection,
    zope.schema.interfaces.IChoice, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


# get
def getSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))


def getMultiSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, MultiSelectWidget(request))


def getGroupSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, GroupSelectWidget(request))


# setup
def setUpSelectWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SelectWidget, **kw)


def setUpMultiSelectWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(MultiSelectWidget, **kw)


def setUpGroupSelectWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(GroupSelectWidget, **kw)
