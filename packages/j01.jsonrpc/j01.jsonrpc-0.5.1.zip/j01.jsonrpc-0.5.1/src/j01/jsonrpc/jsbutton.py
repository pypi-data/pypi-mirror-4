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

import zope.component
import zope.interface
import zope.location
import zope.i18nmessageid

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IButtonAction
from z3c.form.widget import Widget
from z3c.form.widget import FieldWidget
from z3c.form import action
from z3c.form import button
from z3c.form.browser.widget import addFieldClass
from z3c.form.browser.widget import HTMLInputWidget

from j01.jsonrpc import interfaces

_ = zope.i18nmessageid.MessageFactory('p01')


# IJSButtons
class JSButtons(button.Buttons):
    """Button manager."""

    zope.interface.implements(interfaces.IJSButtons)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter java script code if the inputEnterActionName
        name defines a button and the button condition is True.
        """
        # find and return the form submit javascript
        button = self.get(form.inputEnterActionName)
        # note button AND condition could be None
        if button is not None:
            if button.condition is None or (button.condition is not None and \
                button.condition(form)):
                return button.getInputEnterJavaScript(form, request)


class JSButtonWidget(HTMLInputWidget, Widget):
    """A json rpc submit button of a form."""
    zope.interface.implementsOnly(interfaces.IJSButtonWidget)

    klass = u'j01Button-widget button-field'

    def addClass(self, klass):
        """We will prepend css classes and not append like z3c.form"""
        if not self.klass:
            # just a single class
            self.klass = unicode(klass)
        else:
            # prepend and not append new classes
            classes = klass.split() + self.klass.split()
            seen = {}
            unique = []
            for item in classes:
                if item in seen:
                    continue
                seen[item]=1
                unique.append(item)
            self.klass = u' '.join(unique)

    def update(self):
        # We do not need to use the widget's update method, because it is
        # mostly about ectracting the value, which we do not need to do.
        # get all css classes
        if not self.klass:
            self.klass = ''
        classes = self.klass.split()
        if self.required and 'required' not in classes:
            # append required at the end
            classes.apend('required')
        if self.field.css:
            # make sure items are not repeated and prepend css classes
            classes = self.field.css.split() + classes
        # make sure every class is unique
        seen = {}
        unique = []
        for item in classes:
            if item in seen:
                continue
            seen[item]=1
            unique.append(item)
        self.klass = u' '.join(unique)


class JSButtonAction(action.Action, JSButtonWidget,
    zope.location.Location):
    """A button action specifically for JS buttons."""
    zope.interface.implements(interfaces.IJSButtonAction)
    zope.component.adapts(IFormLayer, interfaces.IJSButton)

    _javascript = None

    def __init__(self, request, field):
        action.Action.__init__(self, request, field.title)
        JSButtonWidget.__init__(self, request)
        self.field = field

    def isExecuted(self):
        j01FormHandlerName = self.request.get('j01FormHandlerName')
        if j01FormHandlerName and self.name.endswith(j01FormHandlerName):
            return True
        else:
            # also support non JSONRPC request concept for urls like
            # <page-url>?form.buttons.foobar=1
            return self.name in self.request

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')

    @property
    def javascript(self):
        return self.field.getJavaScript(self, self.request)

    # access css from button
    @property
    def css(self):
        return self.field.css


# IJSButton
class JSButton(button.Button):
    """JS button.
    
    This is the basic implementation and only shows an alert message. Use this
    class for implement your own custom buttons.
    """

    zope.interface.implements(interfaces.IJSButton)

    urlGetter = None
    css = None

    def __init__(self, *args, **kwargs):
        # apply optional urlGetter
        if 'urlGetter' in kwargs:
            self.urlGetter = kwargs['urlGetter']
            del kwargs['urlGetter']
        # apply optional css, which get added in front of other classes
        if 'css' in kwargs:
            self.css = kwargs['css']
            del kwargs['css']
        super(JSButton, self).__init__(*args, **kwargs)

    def getURL(self, form, request):
        """Returns the url based on urlGetter or the form url"""
        if self.urlGetter is not None:
            return self.urlGetter(form)
        else:
            return form.pageURL

    def getInputEnterJavaScript(self, form, request):
        raise NotImplementedError(
            "Subclass must implement getInputEnterJavaScript method")

    def getJavaScript(self, action, request):
        raise NotImplementedError(
            "Subclass must implement getJavaScript method")


# form processing button
class JSONRPCButton(JSButton):
    """Generic form submit button which can submit form data and render the
    response content into the page with JSONRPC.
    
    Redirect is also supported if the form will set a nextURL. Or you can
    define a location where the content should get rendered by define a
    contentTargetExpression in your page/form.

    The getInputEnterJavaScript method get called if you set the buttons
    action handler name as inputEnterActionName value e.g:
    
    inputEnterActionName = 'applyChanges'
    
    Don't forget to include the inputEnterJavaScript part in your form
    template if you use an inputEnterActionName e.g.:
    
    <script type="text/javascript"
            tal:content="view/inputEnterJavaScript"> </script>

    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js >= 1.7.0
    - j01.jsonrpc.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.
   
    Note: file uploads can't get handeled by JSON-RPC or ajax. You have to
    use an iframe. See j01.dialog for built in iframe support.
    """

    zope.interface.implements(interfaces.IJSONRPCButton)

    callback = 'j01RenderContent'

    def __init__(self, *args, **kwargs):
        # apply optional callback
        if 'callback' in kwargs:
            self.callback = kwargs['callback']
            del kwargs['callback']
        super(JSONRPCButton, self).__init__(*args, **kwargs)

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        # replace dotted id with '\\.' See jquery.com for details
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    var data = $('#%s').j01FormToArray('%s');
                    proxy = getJSONRPCProxy('%s');
                    proxy.addMethod('j01FormProcessor', %s);
                    proxy.j01FormProcessor(data);
                    return false;
                }
            });
            """ % (formId, formId, self.__name__, url, self.callback)

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').on('click', '#%s', function(){
                var data = $('#%s').j01FormToArray('%s');
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01FormProcessor', %s);
                proxy.j01FormProcessor(data);
                return false;
            });
            """ % (formId, action.id, formId, self.__name__, url, self.callback)


# simple content loader button
class JSONRPCContentButton(JSONRPCButton):
    """Button which will load and render content via JSON-RPC without processing
    the form.

    The callback method j01RenderContent is responsible for render the given
    content to the target defined by contentTargetExpression

    The optional urlGetter method can get used for define the url where the
    form content get loaded. By default the urlGetter uses the built in pageURL.

    This button requires the following javascript files:

    - z3c.xmlhttp.js
    - z3c.jsonrpcproxy.js
    - jquery.js >= 1.7.0
    - j01.jsonrpc.js

    NOTE: The form using this button must contain the form tag. If the form
    tag doesn't get rendered within each new request, the button click handler
    will get applied more then once to the form and doesn't work.

    """

    def getInputEnterJavaScript(self, form, request):
        """Returns the input enter JavaScript code."""
        # replace dotted id with '\\.' See jquery.com for details
        formId = form.id.replace('.', '\\\.')
        url = self.getURL(form, request)
        return """
            $('#%s').on('keypress', 'input', function(){
                if(!e){e = window.event;}
                key = e.which ? e.which : e.keyCode;
                if (key == 13) {
                    proxy = getJSONRPCProxy('%s');
                    proxy.addMethod('j01LoadContent', %s);
                    proxy.j01LoadContent();
                    return false;
                }
            });
            """ % (formId, url, self.callback)

    def getJavaScript(self, action, request):
        """Returns the button javascript code"""
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').on('click', '#%s', function(){
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01LoadContent', %s);
                proxy.j01LoadContent();
                return false;
            });
            """ % (formId, action.id, url, self.callback)


class JSONRPCClickButton(JSONRPCButton):
    """Click button
    
    If the edit form does not contain the form tag (partial content in a large
    form), we need to use another pattern then the default .on('click', ..)
    handler. Otherwise we whould (re)apply everytime the edit button get loaded
    without to remove them from the form tag. This is because the form contains
    the delegated event handler if we sould use the .on('click',...) handler.
    
    This button uses a simple click handler which will get removed including
    it's click handler if the button get removed.

    IMPORTANT: If you use more then one JSONRPC form in one page you need to
    use different widget and button prefixes. Otherwise the button click
    handler get blocked if the same buttonis used in loaded open forms.
    The widget prefix is important if you use the same form field names in 2
    different forms loaded in the same page.

    The widget prefix will get changed by define a prefixWidgets property
    and the buttons prefix will get changed by define a prefixButtons property.
    See the improved updateWidgets and updateActions methods in JSONRPCForm

    """

    def getInputEnterJavaScript(self, form, request):
        # not supported yet
        return ""

    def getJavaScript(self, action, request):
        # replace dotted id with '\\.' See jquery.com for details
        formId = action.form.id.replace('.', '\\\.')
        url = self.getURL(action.form, request)
        return """
            $('#%s').click(function(){
                var data = $('#%s').j01FormToArray('%s');
                proxy = getJSONRPCProxy('%s');
                proxy.addMethod('j01FormProcessor', %s);
                proxy.j01FormProcessor(data);
                return false;
            });
            """ % (action.id, formId, self.__name__, url, self.callback)


def canDelete(form):
    if hasattr(form, 'supportsDelete'):
        return form.supportsDelete
    return True


class IJSONRPCButtons(zope.interface.Interface):

    add = JSONRPCButton(
        title=_(u'Add')
        )

    applyChanges = JSONRPCButton(
        title=_(u'Apply')
        )

    delete = JSONRPCButton(
        title=_(u'Delete'),
        condition=canDelete
        )

    search = JSONRPCButton(
        title=_(u'Search')
        )

    cancel = JSONRPCButton(
        title=_(u'Cancel')
        )
