##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""

import zope.schema
import zope.interface

import z3c.form.interfaces


class IJSONRPCPage(zope.interface.Interface):
    """JSON-RPC page marker."""


class IJSONRPCTable(zope.interface.Interface):
    """JSON-RPC table marker."""


# jsbutton
class IJSButtons(z3c.form.interfaces.IButtons):
    """JS buttons."""

    def getInputEnterJavaScript(form, request):
        """Returns the input enter java script code if the inputEnterActionName
        name defines a button and the button condition is True.
        """


class IJSButton(z3c.form.interfaces.IButton):
    """JS javascript aware button."""

    def getJavaScript(action, request):
        """Returns the javascript code."""

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""


class IJSONRPCButton(IJSButton):
    """JSONRPC button"""

    urlGetter = zope.interface.Attribute("""URL getter method""")

    css = zope.interface.Attribute("""css""")

    callback = zope.schema.ASCIILine(
        title=u'Callback function name as string',
        description=u'Callback function name as string',
        default='',
        required=False)

    def getURL(self, form):
        """Returns the url based on urlGetter or the form url"""


class IJSButtonAction(z3c.form.interfaces.IButtonAction):
    """JS button Action."""

    javascript = zope.schema.Text(
        title=u'Javascript',
        description=(u'This attribute specifies the javascript part rendered '
                     u'directly after the button if given.'),
        default=None,
        required=False)


class IJSButtonWidget(z3c.form.interfaces.IButtonWidget):
    """JS button widget."""


class IJSONRPCHandler(zope.interface.Interface):

    def __call__(form, data):
        """Processes the action handler"""


class IJSONRPCActionHandler(z3c.form.interfaces.IActionHandler):

    def __call__():
        """Lookup and execute the action handler."""


# json rpc form
class IJSONRPCForm(zope.interface.Interface):
    """JSON-RPC base form mixin class."""

    inputEnterActionName = zope.schema.TextLine(
        title=(u'Button name where the input enter JS code get used'),
        description=(u'Button name where the input enter JS code get used'),
        required=False)

    inputEnterJavaScript = zope.schema.Text(
        title=u'Input enter javascript code',
        description=(u'This attribute specifies the javascript part rendered '
                     u'for bind input to keypress enter handler'),
        required=True)

    jsonRPCHandlers = zope.schema.Object(
        title=u"JSONRPC Handler Manager",
        schema=z3c.form.interfaces.ISelectionManager)

    refreshWidgets = zope.schema.Bool(
        title=u'Refresh widgets',
        description=(u'A flag, when set, causes form widgets to be updated '
                     u'again after action execution.'),
        default=False,
        required=True)


class IJSONRPCAddForm(IJSONRPCForm, z3c.form.interfaces.IAddForm):
    """JSON-RPC based add form."""


class IJSONRPCEditForm(IJSONRPCForm, z3c.form.interfaces.IEditForm):
    """JSON-RPC based edit form."""


class IJSONRPCSearchForm(IJSONRPCForm, z3c.form.interfaces.IForm):
    """JSON-RPC based search form."""
