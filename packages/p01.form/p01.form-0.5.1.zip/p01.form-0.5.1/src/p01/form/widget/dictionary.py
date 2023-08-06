###############################################################################
#
# Copyright 2012 by refline (Schweiz) AG, CH-5630 Muri
#
###############################################################################
"""
$Id: dictionary.py 3162 2012-11-11 04:34:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import z3c.form.widget
import z3c.form.converter
import z3c.form.browser.widget
import z3c.form.browser.textarea

from p01.form import interfaces


class DictKeyValueWidget(z3c.form.browser.textarea.TextAreaWidget):
    """Input type text widget implementation for dict with key/value values."""

    zope.interface.implementsOnly(interfaces.IDictKeyValueWidget)

    klass = u'dict-key-value-widget textarea-widget'
    value = u''

    label = None

    def update(self):
        super(DictKeyValueWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


# converter
class DictKeyValueConverter(z3c.form.converter.BaseDataConverter):
    """Data converter for IDictKeyValueWidget."""

    zope.component.adapts(
        zope.schema.interfaces.IDict, interfaces.IDictKeyValueWidget)

    def toWidgetValue(self, value):
        """Convert from text lines to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return u''
        elif value is None:
            # in case we use missing_value = {}
            return u''
        res = u''
        for k, v in value.items():
            res += u'%s:%s\n' % (k, v)
        return res

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if not len(value):
            return self.field.missing_value

        # find key type
        keyType = self.field.key_type._type
        if keyType is None:
            keyType = unicode
        if isinstance(keyType, tuple):
            keyType = keyType[0]

        # find value type
        valueType = self.field.value_type._type
        if isinstance(valueType, tuple):
            valueType = valueType[0]

        mapping = {}
        for entry in value.splitlines():
            if not entry:
                # ignore leading and ending empty linebreaks
                continue
            k, v = entry.split(':')
            mapping[keyType(k.strip())] = valueType(v.strip())
        return mapping


def getDictKeyValueWidget(field, request):
    """IFieldWidget factory for DictKeyValueWidget."""

    return z3c.form.widget.FieldWidget(field, DictKeyValueWidget(request))


def setUpDictKeyValueWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(DictKeyValueWidget, **kw)
