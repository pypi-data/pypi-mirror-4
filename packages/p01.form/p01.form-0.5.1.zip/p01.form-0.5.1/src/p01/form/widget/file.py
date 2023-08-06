###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""file upload widget

$Id: file.py 3018 2012-08-06 13:50:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema.interfaces

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.file

from p01.form import interfaces
from p01.form.layer import IFormLayer
from p01.form.widget.widget import setUpWidget


class FileWidget(z3c.form.browser.file.FileWidget):
    """Input type text widget implementation."""

    zope.interface.implementsOnly(interfaces.IFileWidget)

    klass = u'file'
    css = u'file'

    # Filename and headers attribute get set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form.
    headers = None
    filename = None


# get
@zope.component.adapter(zope.schema.interfaces.IBytes, IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getFileWidget(field, request):
    """IFieldWidget factory for IPasswordWidget."""
    return z3c.form.widget.FieldWidget(field, FileWidget(request))


# setup
def setUpFileWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(FileWidget, **kw)
