##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Common z3c.form test setups

$Id: __init__.py 3003 2012-08-04 13:27:46Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import os

import persistent
import zope.component
import zope.interface
import zope.schema
import zope.traversing.testing
from zope.container import contained
from zope.pagetemplate.interfaces import IPageTemplate
from zope.password.interfaces import IPasswordManager
from zope.password.password import PlainTextPasswordManager
from zope.publisher.browser import TestRequest
from zope.schema.fieldproperty import FieldProperty

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.field
import z3c.form.browser
import z3c.jsonrpc.testing
import z3c.macro.tales
import z3c.template.template
from z3c.template.interfaces import IContentTemplate

import j01.jsonrpc
from j01.jsonrpc import interfaces
from j01.jsonrpc import jsbutton
from j01.jsonrpc import jsform


class FormTestRequest(TestRequest):
    zope.interface.implements(z3c.form.interfaces.IFormLayer)


class IDemoContent(zope.interface.Interface):
    """Demo content interface."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title')

    description = zope.schema.TextLine(
        title=u'Description',
        description=u'The description')


class DemoContent(persistent.Persistent, contained.Contained):
    """Demo content."""
    zope.interface.implements(IDemoContent)

    title = FieldProperty(IDemoContent['title'])
    description = FieldProperty(IDemoContent['description'])


class DemoForm(jsform.JSONRPCEditForm):
    """Sample JSON form."""

    fields = z3c.form.field.Fields(IDemoContent)


def getPath(filename, package=None):
    if package is None:
        package = __file__
    return os.path.join(os.path.dirname(package), filename)


def setupJSONRPCFormDefaults():

    # setup absulutURL adapter
    zope.traversing.testing.setUp()
    zope.component.provideUtility(PlainTextPasswordManager(), IPasswordManager,
        'Plain Text')

    # setup form template
    zope.component.provideAdapter(
        z3c.template.template.TemplateFactory(
            getPath('layout.pt'), 'text/html'),
        (zope.interface.Interface, z3c.form.interfaces.IFormLayer),
        IContentTemplate)

    # setup button widgets
    zope.component.provideAdapter(
        z3c.form.widget.WidgetTemplateFactory(
            getPath('js_button_display.pt', j01.jsonrpc.__file__), 'text/html'),
        (None, None, None, None, interfaces.IJSButtonWidget),
        IPageTemplate, name=z3c.form.interfaces.DISPLAY_MODE)

    zope.component.provideAdapter(
        z3c.form.widget.WidgetTemplateFactory(
            getPath('js_button_input.pt', j01.jsonrpc.__file__), 'text/html'),
        (None, None, None, None, interfaces.IJSButtonWidget),
        IPageTemplate, name=z3c.form.interfaces.INPUT_MODE)

    # setup button action
    zope.component.provideAdapter(jsbutton.JSButtonAction,
        provides=z3c.form.interfaces.IButtonAction)

    # setup form adapters for jsonrpc request
    zope.component.provideAdapter(
        z3c.form.button.ButtonAction,
        (z3c.jsonrpc.interfaces.IJSONRPCRequest, z3c.form.interfaces.IButton),
        z3c.form.interfaces.IButtonAction)

    zope.component.provideAdapter(z3c.form.field.FieldWidgets,
        (z3c.form.interfaces.IFieldsForm,
         z3c.jsonrpc.interfaces.IJSONRPCRequest, zope.interface.Interface))

    zope.component.provideAdapter(
        z3c.form.browser.text.TextFieldWidget,
        adapts=(zope.schema.interfaces.ITextLine,
                z3c.jsonrpc.interfaces.IJSONRPCRequest))

    zope.component.provideAdapter(
        z3c.template.template.TemplateFactory(
            getPath('layout.pt'), 'text/html'),
        (zope.interface.Interface, z3c.jsonrpc.interfaces.IJSONRPCRequest),
        IContentTemplate)


###############################################################################
#
# Unittest setup
#
###############################################################################

from zope.pagetemplate.engine import Engine
from zope.pagetemplate.engine import _Engine
from zope.pagetemplate.engine import TrustedEngine
from zope.pagetemplate.engine import _TrustedEngine

def registerType(name, handler):
    Engine.registerType(name, handler)
    TrustedEngine.registerType(name, handler)


def clear():
    Engine.__init__()
    _Engine(Engine)
    TrustedEngine.__init__()
    _TrustedEngine(TrustedEngine)


try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    addCleanUp(clear)


def setUp(test):
    registerType('macro', z3c.macro.tales.MacroExpression)
    z3c.jsonrpc.testing.setUpTestAsModule(test, name='README')


def tearDown(test):
    # ensure that we cleanup everything
    zope.testing.cleanup.cleanUp()
    z3c.jsonrpc.testing.tearDownTestAsModule(test)
