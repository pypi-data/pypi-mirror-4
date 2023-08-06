###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Text widget
$Id: __init__.py 3162 2012-11-11 04:34:42Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

from p01.form.widget.widget import setUpWidget


# checkbox
from p01.form.widget.checkbox import getCheckBoxWidget
from p01.form.widget.checkbox import setUpCheckBoxWidget

from p01.form.widget.checkbox import getDivCheckBoxWidget
from p01.form.widget.checkbox import setUpDivCheckBoxWidget

from p01.form.widget.checkbox import getSingleCheckBoxWidget
from p01.form.widget.checkbox import setUpSingleCheckBoxWidget

from p01.form.widget.checkbox import getSingleDivCheckBoxWidget
from p01.form.widget.checkbox import setUpSingleDivCheckBoxWidget

from p01.form.widget.checkbox import getSingleCheckBoxWithoutLabelWidget
from p01.form.widget.checkbox import setUpSingleCheckBoxWithoutLabelWidget

# dictionary
from p01.form.widget.dictionary import getDictKeyValueWidget
from p01.form.widget.dictionary import setUpDictKeyValueWidget

# file
from p01.form.widget.file import getFileWidget
from p01.form.widget.file import setUpFileWidget

# password
from p01.form.widget.password import getPasswordWidget
from p01.form.widget.password import setUpPasswordWidget

from p01.form.widget.password import getPasswordConfirmationWidget
from p01.form.widget.password import setUpPasswordConfirmationWidget

# radio
from p01.form.widget.radio import getRadioWidget
from p01.form.widget.radio import setUpRadioWidget

from p01.form.widget.radio import getDivRadioWidget
from p01.form.widget.radio import setUpDivRadioWidget

# select
from p01.form.widget.select import getSelectWidget
from p01.form.widget.select import setUpSelectWidget

from p01.form.widget.select import getMultiSelectWidget
from p01.form.widget.select import setUpMultiSelectWidget

from p01.form.widget.select import getGroupSelectWidget
from p01.form.widget.select import setUpGroupSelectWidget

# text
from p01.form.widget.text import getTextWidget
from p01.form.widget.text import getHintWidget
from p01.form.widget.text import getPlaceholderWidget
from p01.form.widget.text import getPlaceholderHintWidget

from p01.form.widget.text import setUpTextWidget
from p01.form.widget.text import setUpHintWidget
from p01.form.widget.text import setUpPlaceholderWidget
from p01.form.widget.text import setUpPlaceholderHintWidget

# textlines
from p01.form.widget.textlines import getTextLinesWidget
from p01.form.widget.textlines import setUpTextLinesWidget

# textarea
from p01.form.widget.textarea import getTextAreaWidget
from p01.form.widget.textarea import setUpTextAreaWidget
