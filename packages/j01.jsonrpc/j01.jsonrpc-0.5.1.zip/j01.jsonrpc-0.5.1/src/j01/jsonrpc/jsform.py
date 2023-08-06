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
__docformat__ = "reStructuredText"

import sys
import urllib

import zope.interface
import zope.component
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces import NotFound

import z3c.form.interfaces
import z3c.form.field
import z3c.form.form
from z3c.jsonrpc.interfaces import IMethodPublisher
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from j01.jsonrpc import interfaces
from j01.jsonrpc import jsbutton

_ = zope.i18nmessageid.MessageFactory('p01')


REDIRECT_STATUS_CODES = (301, 302, 303)


class JSONRPCHandlers(object):
    """A manager for handling JSONRPC request handlers."""

    def __init__(self):
        # setup name, handler container
        self._data = {}

    def addHandler(self, name, handler):
        self._data[name] = handler

    def get(self, name, default=None):
        return self._data.get(name, default)

    def __call__(self):
        handler = self.form.jsonRPCHandlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)

    def copy(self):
        handlers = JSONRPCHandlers()
        for name, handler in self._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IButtonHandlers"""
        if not isinstance(other, JSONRPCHandlers):
            raise NotImplementedError
        handlers = self.copy()
        for name, handler in other._data.items():
            handlers.addHandler(name, handler)
        return handlers

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data.keys())


class JSONRPCHandler(object):
    """JSONRPC handler."""

    zope.interface.implements(interfaces.IJSONRPCHandler)

    def __init__(self, func):
        self.func = func

    def __call__(self, form, data):
        return self.func(form, data)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.func.__name__)


class JSONRPCActionHandler(object):
    """JSONRPC handler executer.

    This adapter makes it possible to execute JSONRPCHandler.
    """

    zope.interface.implements(interfaces.IJSONRPCActionHandler)
    zope.component.adapts(
        interfaces.IJSONRPCForm,
        zope.interface.Interface,
        zope.interface.Interface,
        interfaces.IJSButtonAction)

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action

    def __call__(self):
        handler = self.form.jsonRPCHandlers.get(self.action.__name__)
        if handler is None:
            return
        return handler(self.form, self.action)


def jsonRPCHandler(*args, **kwargs):
    """A decorator for defining an JSONRPC request handler.

    This handler can be used like:

    @jsform.jsonRPCHandler('save')
    def doSomething(self, data):
        return u'Hello World'

    """
    def createHandler(func):
        if args:
            __name__ = args[0]
        else:
            __name__ = kwargs.get('name', func.__name__)
        handler = JSONRPCHandler(func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('jsonRPCHandlers', JSONRPCHandlers())
        handlers.addHandler(__name__, handler)
        return handler
    return createHandler


def jsonRPCButtonHandler(button, *args, **kwargs):
    """A decorator for defining an JSONRPC request handler using a button.

    This handler can be used like:

    @jsform.jsonRPCButtonHandler(ISaveFormButtons['save'], foo='bar')
    def doSomething(self, data):
        return u'Hello World'

    The foo attribute with the value bar get applied to the given button. This
    let us customize buttons attributes e.g. override the callback with
    something like: callback='callThis'

    Note, the difference compared with the z3c.form button handler
    implementation. We use the data as argument and not the handler action in
    the decorated method.

    Note, since we use the improved JSONRPC request handler, we can also access
    the given arguments of a form submit in the request or request.form
    variable.

    Note, don't forget JSONRPC based on xmlhttp requests are not able to handle
    file uploads. z3c.jsonrpcproxy is based on xmlhttp like (m)any other JSON
    library.

    """
    if args:
        __name__ = args[0]
    else:
        __name__ = kwargs.get('name', button.__name__)
    for k, v in kwargs.items():
        if k == 'name':
            continue
        # apply additional attributes
        setattr(button, k, v)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', jsbutton.JSButtons())
    f_locals['buttons'] += jsbutton.JSButtons(button)
    # create a handler
    def createHandler(func):
        handler = JSONRPCHandler(func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('jsonRPCHandlers', JSONRPCHandlers())
        handlers.addHandler(__name__, handler)
        return handler
    return createHandler


def extends(*args, **kwargs):
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    if not kwargs.get('ignoreFields', False):
        f_locals['fields'] = z3c.form.field.Fields()
        for arg in args:
            f_locals['fields'] += getattr(arg, 'fields', z3c.form.field.Fields())
    if not kwargs.get('ignoreButtons', False):
        f_locals['buttons'] = jsbutton.JSButtons()
        for arg in args:
            f_locals['buttons'] += getattr(arg, 'buttons', jsbutton.JSButtons())
    if not kwargs.get('ignoreHandlers', False):
        f_locals['jsonRPCHandlers'] = JSONRPCHandlers()
        for arg in args:
            f_locals['jsonRPCHandlers'] += getattr(arg,
                'jsonRPCHandlers', JSONRPCHandlers())


class JSONRPCFormMixin(object):
    """JSONRPC form mixin providing IJSONRPCForm

    Note: the IJSONRPCForm interfaces makes sure that a pagelet
    (content provider) adapter is available by default. This is usefull if you
    instanciate such classes without to lookup them as adapters registred
    with the pagelet directive.
    """

    zope.interface.implements(interfaces.IJSONRPCForm)

    template = getPageTemplate()
    layout = getLayoutTemplate()

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    # cached urls
    _contextURL = None
    _pageURL = None

    # override widget prefix if you need to load different forms using the same
    # field names in one single page.
    prefixWidgets = 'widgets'

    # override button prefix if you need to load different forms using the same
    # button in one single page.
    prefixButtons = 'buttons'

    # allows to skip action and widget processing. This is sometimes required
    # for JSON-RPC forms
    skipActions = False
    skipWidgets = False

    # allows to fetch a status message from an url set by redirect. Set this to
    # None or a different name if you don't like to support such status
    # messages e.g. foo.html?status=foobar. Note: such status message must
    # be urlencoded
    statusAttrName = 'status'

    # set this conditions in your action handler method if needed
    # widgets normaly not change their value
    refreshWidgets = False
    # action condition may have changed after action execution
    refreshActions = False

    inputEnterActionName = None # see inputEnterJavaScript

    # JSON-RPC javascript callback arguments
    # content target expression where the result get rendered in. By default
    # the built-in argument ``#content`` get used
    contentTargetExpression = None

    # optional scrollTo expression where the callback method will scroll to
    # after rendering. The default implementation uses offset().top. Feel free
    # to implement a custom j01CallbackRegistry method which uses another
    # concept instead of add more callback arguments
    scrollToExpression = None
    scrollToOffset = None
    scrollToSpeed = None

    # the next URL where the jsonrpc callback method will redirect to using
    # window.location.href = response.nextURL
    nextURL = None
    # the nextHash will update the url witout to redirect
    nextHash = None

    buttons = jsbutton.JSButtons()

    jsonRPCHandlers = JSONRPCHandlers()

    def publishTraverse(self, request, name):
        view = zope.component.queryMultiAdapter((self, request), name=name)
        if view is None or not IMethodPublisher.providedBy(view):
            raise NotFound(self, name, request)
        return view

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

    @property
    def inputEnterJavaScript(self):
        """Enter button click handler.

        You can define an action handler name which get called on enter button
        call in your form like:

        inputEnterActionName = 'myHandlerName'

        Note: you need to include the inputEnter javascript in your template
        within:

        <script type="text/javascript"
                tal:content="view/inputEnterJavaScript">
        </script>
        """
        return self.buttons.getInputEnterJavaScript(self, self.request)

# XXX: implement this hook in z3c.form
    def updateActions(self):
        if self.prefixButtons is not None:
            # overrride button prefix before update actions
            self.buttons.prefix = self.prefixButtons
        super(JSONRPCFormMixin, self).updateActions()

# XXX: implement this hook in z3c.form
    def updateWidgets(self, prefix=None):
        if prefix is None and self.prefixWidgets is not None:
            prefix = self.prefixWidgets
        super(JSONRPCFormMixin, self).updateWidgets(prefix)

# XXX: implement this hook in z3c.form
    def executeActions(self):
        """Dispatch actions.execute call"""
        self.actions.execute()

# XXX: implement this hook in z3c.form
    def update(self):
        """Update form

        The default z3c.form calles the following methods in update:

        self.updateWidgets()
        self.updateActions()
        self.actions.execute()
        if self.refreshActions:
            self.updateActions()

        We implemented the following coditions:

        - skipWidgets
        - skipActions
        - refreshActions (also supported by z3c.form)
        - refreshWidgets

        This allows us to prepare the JSONRPC call setup and gives more
        controll for complex form setup. Also see J01FormProcessor in
        j01/jsform/jsonrpc.py

        """
        if not self.skipWidgets:
            # default False
            self.updateWidgets()

        if not self.skipActions:
            # default False
            self.updateActions()
            self.executeActions()

        if self.refreshActions:
            # default False
            self.updateActions()

        if self.refreshWidgets:
            # default False
            self.updateWidgets()

        if self.statusAttrName is not None:
            # get and set status given from url
            status = self.request.get(self.statusAttrName)
            if status:
                self.status = status

    def setNextURL(self, url, status):
        """Helper for set a nextURL including a status message

        Note: the status message must be an i18n message which will get
        translated later as status message.

        If you don't use a status message just use self.nextURL = myURL and
        don't use this method.

        """
        self.nextURL = '%s?%s' % (url, urllib.urlencode({'status':status}))

    def render(self):
        if self.nextURL is not None:
            return None
        return self.template()

    def __call__(self):
        # don't render on redirect
        if self.request.response.getStatus() in REDIRECT_STATUS_CODES:
            return u''
        self.update()
        # we only use the nextURL pattern and not the redirect status check
        # in our JSON-RPC method call. But this __call__ method get only used
        # if no JSON-RPC call is involved. So let's setup the redirect.
        if self.nextURL is not None:
            self.request.response.redirect(self.nextURL)
            return u''
        return self.layout()


class JSONRPCForm(JSONRPCFormMixin, z3c.form.form.Form):
    """JSONRPC form mixin."""

    buttons = jsbutton.JSButtons()


class JSONRPCEditForm(JSONRPCFormMixin, z3c.form.form.EditForm):
    """JSONRPC edit form."""

    zope.interface.implements(interfaces.IJSONRPCEditForm)

    showCancel = True
    buttons = jsbutton.JSButtons()

    def doHandleApplyChanges(self, action):
        # Note we, use the data from the request.form
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
        self.updateActions()
        self.updateWidgets()

    @jsonRPCButtonHandler(jsbutton.IJSONRPCButtons['applyChanges'])
    def handleApplyChanges(self, action):
        self.doHandleApplyChanges(action)

    @jsonRPCButtonHandler(jsbutton.IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)


class JSONRPCAddForm(JSONRPCFormMixin, z3c.form.form.AddForm):
    """JSONRPC add form."""

    zope.interface.implements(interfaces.IJSONRPCAddForm)

    showCancel = True
    buttons = jsbutton.JSButtons()

    def doHandleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def doHandleCancel(self, data):
        self.ignoreRequest = True
        self.updateActions()
        self.updateWidgets()

    @jsonRPCButtonHandler(jsbutton.IJSONRPCButtons['add'])
    def handleAdd(self, action):
        self.doHandleAdd(action)

    @jsonRPCButtonHandler(jsbutton.IJSONRPCButtons['cancel'],
        condition=lambda form: form.showCancel)
    def handleCancel(self, action):
        self.doHandleCancel(action)

    def renderAfterAdd(self):
        return super(JSONRPCAddForm, self).render()

    def render(self):
        if self._finishedAdd:
            return self.renderAfterAdd()
        return super(JSONRPCAddForm, self).render()


class JSONRPCSearchForm(JSONRPCFormMixin, z3c.form.form.Form):
    """JSONRPC search form."""

    zope.interface.implements(interfaces.IJSONRPCSearchForm)

    buttons = jsbutton.JSButtons()
    inputEnterActionName = 'search'

    def doHandleSearch(self, action):
        raise NotImplementedError('Subclass must implement doHandleSearch')

    @jsonRPCButtonHandler(jsbutton.IJSONRPCButtons['search'])
    def handleSearch(self, action):
        self.doHandleSearch(action)
