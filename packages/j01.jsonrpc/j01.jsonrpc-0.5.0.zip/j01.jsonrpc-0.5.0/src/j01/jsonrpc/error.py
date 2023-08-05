##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

import zope.interface
import zope.component
import zope.i18nmessageid
from zope.site import hooks
from zope.traversing.browser.absoluteurl import absoluteURL


import z3c.jsonrpc.error
from z3c.jsonrpc.interfaces import IJSONRPCRequest
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IErrorViewSnippet

_ = zope.i18nmessageid.MessageFactory('p01')


# z3c.jsonrpc JSONRPCErrorView
# XXX: implement a JSON-RPC login concept see comment below
#      The problem is, we probably can't traverse to the page where the JSON-RPC
#      method is available. This makes it hard to store a camefrom etc.
#      One solution could be to implement a JSON-RPC based login concept which
#      allows to stay on the current page and provide a login process, after a
#      successful login the user could do what he does before the unauthorized
#      exception was raised because we did not change the current page in any
#      way.

class Unauthorized(z3c.jsonrpc.error.JSONRPCErrorView):
    """Unauthorized error view which forces to redirect to the loginForm.html
    page. 

    This is probably not the best concept because we will loose the
    original page and what we tried to do.

    Note: use your own Unauthorized error view if you don't need to redirect to
    <site>/loginForm.html page.
    
    Also make sure every JS implementation can handle response.error and
    response.data.nextURL. See j01.jsonrpc javascript as a sample.
    """

    code = -32000
    message = u'Unauthorized'

    @property
    def data(self):
        # setup a redirect url
        site = hooks.getSite()
        nextURL = '%s/@@loginForm.html' % absoluteURL(site, self.request)
        return {'nextURL': nextURL}

    def __call__(self):
        """Must return itself.
        
        This allows us to use the error view in setResult if ZopePublication
        is adapting an error view to error and request and calls them.
        """
        # do not call unauthorized, it's useless since it will only setup a
        # redirect. JSON-RPC doens't provide such a redirect
        return self


# z3c.form IErrorViewSnippet
class JSONErrorViewSnippet(object):
    """Error view snippet."""
    zope.component.adapts(zope.schema.ValidationError, None, IJSONRPCRequest, 
        None, None, None)
    zope.interface.implements(IErrorViewSnippet)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.error.doc()

    def render(self):
        return self.message

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class JSONValueErrorViewSnippet(JSONErrorViewSnippet):
    """An error view for ValueError raised by widget validation."""
    zope.component.adapts(ValueError, None, IJSONRPCRequest, None, None, None)
    
    @property
    def message(self):
        errMsg = _('The system could not process the given value.')
        return zope.i18n.translate(errMsg, context=self.request)

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()

    def render(self):
        return self.message
