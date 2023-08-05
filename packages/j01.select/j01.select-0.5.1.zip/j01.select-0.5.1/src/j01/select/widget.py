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

import zope.interface

import z3c.form.browser.select
import z3c.form.interfaces
import z3c.form.widget

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


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, SelectWidget(request))

@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getSingleSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    widget = z3c.form.widget.FieldWidget(field, SelectWidget(request))
    widget.multiple = None
    return widget
