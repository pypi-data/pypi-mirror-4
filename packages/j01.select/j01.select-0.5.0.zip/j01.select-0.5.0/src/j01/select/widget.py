##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: widget.py 3029 2012-08-26 03:47:14Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.traversing.browser import absoluteURL
from zope.component import hooks

import z3c.form.browser.select
from z3c.form import widget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import SequenceWidget
from z3c.form.widget import FieldWidget
from z3c.form import converter
from z3c.form.browser import widget

from j01.select import interfaces


j01_select_template = """
<script type="text/javascript">
  $("#%s").j01Select({%s
  });
</script>
"""


class SelectWidget(z3c.form.browser.select.SelectWidget):
    """Select input widget for HTML select element"""

    zope.interface.implementsOnly(interfaces.ISelectWidget)

    # you can override this in your custom widget factory
    klass = u'j01-select'
    css = u'j01-select'
    
    widgetExpression = '.j01SelectWidget'
    multiple = 'multiple'
    prependCloser = False
    closeAfterAddToken = True
    evenCSS = 'even'
    oddCSS = 'odd'

    @property
    def javaScript(self):
        lines = []
        append = lines.append
        # widget name
        append("\n    widgetName: '%s'" % self.name)
        # closeAfterAddToken
        if self.closeAfterAddToken:
            append("\n    closeAfterAddToken: true")
        else:
            append("\n    closeAfterAddToken: false")
        # prependCloser
        if self.prependCloser:
            append("\n    prependCloser: true")
        else:
            append("\n    prependCloser: false")
        # even/odd row alternate
        if self.evenCSS:
            append("\n    evenCSS: '%s'" % self.evenCSS)
        if self.oddCSS:
            append("\n    oddCSS: '%s'" % self.oddCSS)
        code = ','.join(lines)
        return j01_select_template % (self.id, code)


#@zope.component.adapter(zope.schema.interfaces.IList, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def getSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, SelectWidget(request))

@zope.interface.implementer(IFieldWidget)
def getSingleSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    widget = FieldWidget(field, SelectWidget(request))
    widget.multiple = None
    return widget
