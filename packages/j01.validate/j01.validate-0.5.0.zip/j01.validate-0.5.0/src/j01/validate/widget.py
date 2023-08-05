##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.browser import text

from j01.validate import interfaces


# TextWidget
class JSONTextWidget(text.TextWidget):
    """TextWidget with JSON validation ."""
    zope.interface.implementsOnly(interfaces.IJSONTextWidget)

    klass = u'text j01Validate'
    css = u'j01-validate'

@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def getJSONTextWidget(field, request):
    """IFieldWidget factory for IJSONTextWidget."""
    return FieldWidget(field, JSONTextWidget(request))
