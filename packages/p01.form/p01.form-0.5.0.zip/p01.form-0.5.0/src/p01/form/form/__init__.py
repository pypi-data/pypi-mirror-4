##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Form classes
$Id: __init__.py 3085 2012-09-10 08:58:40Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import z3c.form.form


# reference for simpler import
extends = z3c.form.form.extends
applyChanges = z3c.form.form.applyChanges

from p01.form.form.form import FormMixin
from p01.form.form.form import DisplayForm
from p01.form.form.form import Form
from p01.form.form.form import AddForm
from p01.form.form.form import EditForm
from p01.form.form.form import SearchForm
