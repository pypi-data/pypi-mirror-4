##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Form classes
$Id: form.py 3166 2012-11-12 11:57:46Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.schema.interfaces import IField

import z3c.form.form
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IWidget
from z3c.form import button
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from p01.form import interfaces
_ = zope.i18nmessageid.MessageFactory('p01')


REDIRECT_STATUS_CODES = (301, 302, 303)


# offer built in layout support
extends = z3c.form.form.extends
applyChanges = z3c.form.form.applyChanges


class FormMixin(object):
    """Simple form mixin."""

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    template = getPageTemplate()
    layout = getLayoutTemplate()

    buttons = button.Buttons()

    # cached urls
    _contextURL = None
    # action/page ur
    _pageURL = None
    # next url
    nextURL = None

    # set this conditions in your action handler method if needed
    refreshWidgets = False
    # action condition may have changed after action execution
    refreshActions = False

    # support returning csv and pdf results
    downloadResult = None

    @property
    def action(self):
        """Take care on action url."""
        return self.pageURL

    @property
    def contextURL(self):
        """Setup and cache context URL"""
        if self._contextURL is None:
            self._contextURL = absoluteURL(self.context, self.request)
        return self._contextURL

    @property
    def pageURL(self):
        """Setup and cache context URL"""
        if self._pageURL is None:
            self._pageURL = '%s/%s' % (absoluteURL(self.context, self.request),
                self.__name__)
        return self._pageURL

    def update(self):
        super(FormMixin, self).update()
        # (new condition)
        if self.refreshWidgets:
            # default False
            self.updateWidgets()

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        self.update()

        if self.downloadResult is not None:
            # support returning csv and pdf results
            return self.downloadResult

        # don't render on redirect
        if self.request.response.getStatus() in REDIRECT_STATUS_CODES:
            return u''

        # now we only use the nextURL pattern and not the redirect status check,
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return u''
        return self.layout()


class DisplayForm(FormMixin, z3c.form.form.DisplayForm):
    """Form for displaying fields"""

    zope.interface.implements(interfaces.IDisplayForm)

    mode = DISPLAY_MODE
    ignoreRequest = True

    buttons = button.Buttons()


class Form(FormMixin, z3c.form.form.Form):
    """Simple form"""

    zope.interface.implements(interfaces.IForm)

    buttons = button.Buttons()


class AddForm(FormMixin, z3c.form.form.AddForm):
    """Add form."""

    zope.interface.implements(interfaces.IAddForm)

    buttons = button.Buttons()
    showCancel = True
    defaultValues = None

    def createAndAdd(self, data):
        obj = self.create(data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        # HEADSUP: The add method could return None if something fails. This
        # will implicit prevent to apply self._finishedAdd in doHandleAdd method
        return self.add(obj)

    def doHandleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # HEADSUP: mark only as finished if we get the new object
            self._finishedAdd = True
        return obj

    def doHandleCancel(self, action):
        self.ignoreRequest = True
        self.refreshActions = True
        self.refreshWidgets = True

    @button.buttonAndHandler(_('Add'), name='add')
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @button.buttonAndHandler(_('Cancel'), name='cancel',
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)

    def getDefaultValues(self):
        # put those default values into self.defaultValues

        # with z3c.form it's a NOGO, to just assign widget.value after update
        # because some widgets need updating after that and the update gets a
        # new value... the right way is to use an IValue(name='default') adapter
        pass

    def setDefaultValues(self):
        pass

    def updateWidgets(self):
        if self.request.method == "GET":
            # POST is a submit, we don't want to overwrite user's values?
            self.getDefaultValues()
        super(AddForm, self).updateWidgets()
        if self.request.method == "GET":
            # POST is a submit, we don't want to overwrite user's values?
            self.setDefaultValues()

    def renderAfterAdd(self):
        return self.template()

    def render(self):
        if self._finishedAdd:
            return self.renderAfterAdd()
        return super(AddForm, self).render()


class EditForm(FormMixin, z3c.form.form.EditForm):
    """Edit form"""

    zope.interface.implements(interfaces.IEditForm)

    showCancel = True

    buttons = button.Buttons()

    def doHandleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage
        return changes

    def doHandleCancel(self, action):
        self.ignoreRequest = True
        self.refreshActions = True
        self.refreshWidgets = True

    @button.buttonAndHandler(_('Apply'), name='apply')
    def handleApplyChanges(self, action):
        self.doHandleApply(action)

    @button.buttonAndHandler(_('Cancel'), name='cancel',
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


###############################################
# AddForm defaultValues support

class ValueProvider(object):
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


@zope.interface.implementer(IValue)
@zope.component.adapter(zope.interface.Interface, zope.interface.Interface,
                          interfaces.IAddForm, IField, IWidget)
def defaultValueProvider(context, request, form, field, widget):
    """return a default value for a field"""
    if form.defaultValues is None:
        return None

    name1 = widget.name
    try:
        v = form.defaultValues[name1]
    except KeyError:
        name2 = name1.split('.')[-1]
        try:
            v = form.defaultValues[name2]
        except KeyError:
            return None

    return ValueProvider(v)


class SearchForm(FormMixin, z3c.form.form.Form):
    """Search form."""

    zope.interface.implements(interfaces.ISearchForm)

    buttons = button.Buttons()

    def doHandleSearch(self, action):
        raise NotImplementedError('Subclass must implement doHandleSearch')

    @button.buttonAndHandler(_('Search'), name='search')
    def handleSearch(self, action):
        self.doHandleSearch(action)
