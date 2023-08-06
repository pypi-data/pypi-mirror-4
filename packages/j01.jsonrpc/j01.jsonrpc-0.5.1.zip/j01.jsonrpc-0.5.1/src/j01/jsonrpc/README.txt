======
README
======

JSON-RPC form processing
------------------------

This package offers forms whihc are able to process via JSON-RPC and other
usefull JSON-RPC methods.

  >>> from pprint import pprint
  >>> import zope.interface
  >>> from zope.interface import alsoProvides
  >>> from z3c.form.interfaces import IFormLayer
  >>> import z3c.form.testing
  >>> import j01.jsonrpc.testing

Now we can setup a content container and content object in our site:

  >>> site  = getRootFolder()
  >>> content = j01.jsonrpc.testing.DemoContent()
  >>> site['content'] = content

Now we can call the method from our JSONRPC view but first setup form support:

  >>> z3c.form.testing.setupFormDefaults()
  >>> j01.jsonrpc.testing.setupJSONRPCFormDefaults()
  >>> formRequest = j01.jsonrpc.testing.FormTestRequest()
  >>> alsoProvides(formRequest, IFormLayer)

Now test the JSON-RPC edit form:

  >>> demoEditForm = j01.jsonrpc.testing.DemoForm(content, formRequest)
  >>> demoEditForm.__name__ = u'demoEditForm'
  >>> demoEditForm.update()
  >>> print demoEditForm.render()
  <form action="http://127.0.0.1/content/demoEditForm" method="post" enctype="multipart/form-data" class="edit-form" name="form" id="form">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>&ndash; required
        </div>
      <div>
            <div id="form-widgets-title-row" class="row required">
                <div class="label">
                  <label for="form-widgets-title">
                    <span>Title</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-title" name="form.widgets.title" class="text-widget required textline-field" value="" type="text" />
  </div>
            </div>
            <div id="form-widgets-description-row" class="row required">
                <div class="label">
                  <label for="form-widgets-description">
                    <span>Description</span>
                    <span class="required">*</span>
                  </label>
                </div>
                <div class="widget">
      <input id="form-widgets-description" name="form.widgets.description" class="text-widget required textline-field" value="" type="text" />
  </div>
            </div>
      </div>
    </div>
    <div>
      <div class="buttons">
        <input type="button" id="form-buttons-applyChanges" name="form.buttons.applyChanges" class="j01Button-widget button-field" value="Apply" />
  <script type="text/javascript">
              $('#form').on('click', '#form-buttons-applyChanges', function(){
                  var data = $('#form').j01FormToArray('applyChanges');
                  proxy = getJSONRPCProxy('http://127.0.0.1/content/demoEditForm');
                  proxy.addMethod('j01FormProcessor', j01RenderContent);
                  proxy.j01FormProcessor(data);
                  return false;
              });
              </script>
        <input type="button" id="form-buttons-cancel" name="form.buttons.cancel" class="j01Button-widget button-field" value="Cancel" />
  <script type="text/javascript">
              $('#form').on('click', '#form-buttons-cancel', function(){
                  var data = $('#form').j01FormToArray('cancel');
                  proxy = getJSONRPCProxy('http://127.0.0.1/content/demoEditForm');
                  proxy.addMethod('j01FormProcessor', j01RenderContent);
                  proxy.j01FormProcessor(data);
                  return false;
              });
              </script>
      </div>
    </div>
  </form>

As you can see the buttons get rendered including come javascript code. This
code will call the form prcessing part. Let's try to send some JSON-RPC form
varaible back to the server. but first we need to register the view as an 
adapter:

Let's show how we can register a jsonrpc view for the container:
(The container class needs permission configuration too)

  >>> from zope.configuration import xmlconfig
  >>> import z3c.jsonrpc
  >>> import zope.security
  >>> import zope.component
  >>> import zope.publisher
  >>> import zope.browserpage
  >>> context = xmlconfig.file('meta.zcml', z3c.jsonrpc)
  >>> context = xmlconfig.file('meta.zcml', zope.security, context)
  >>> context = xmlconfig.file('meta.zcml', zope.component, context)
  >>> context = xmlconfig.file('meta.zcml', zope.publisher, context)
  >>> context = xmlconfig.file('meta.zcml', zope.browserpage, context)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c"
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:browser="http://namespaces.zope.org/browser">
  ...     <class class="j01.jsonrpc.testing.DemoContent">
  ...       <allow
  ...           interface="j01.jsonrpc.testing.IDemoContent"
  ...           />
  ...     </class>
  ...   <browser:page
  ...       name="demoForm"
  ...       for="j01.jsonrpc.testing.IDemoContent"
  ...       class="j01.jsonrpc.testing.DemoForm"
  ...       permission="zope.Public"
  ...       layer="z3c.jsonrpc.testing.IJSONRPCTestLayer"
  ...       />
  ...   <z3c:jsonrpc
  ...       for="j01.jsonrpc.testing.DemoForm"
  ...       class="j01.jsonrpc.jsonrpc.J01FormProcessor"
  ...       permission="zope.Public"
  ...       methods="j01FormProcessor"
  ...       layer="z3c.jsonrpc.testing.IJSONRPCTestLayer"
  ...       />
  ... </configure>
  ... """, context)

  >>> import z3c.jsonrpc.publisher
  >>> from zope.interface import classImplements
  >>> from z3c.jsonrpc.testing import IJSONRPCTestSkin
  >>> classImplements(z3c.jsonrpc.testing.IJSONRPCTestSkin, IFormLayer)

  >>> import os
  >>> import z3c.form.tests
  >>> import z3c.template.template
  >>> editFormTemplate = os.path.join(os.path.dirname(z3c.form.tests.__file__),
  ...     'simple_edit.pt')
  >>> editTemplateFactory = z3c.template.template.TemplateFactory(
  ...     editFormTemplate, 'text/html')

We register the factory on a view interface and a layer.

  >>> import z3c.template.interfaces
  >>> import z3c.jsonrpc.interfaces
  >>> zope.component.provideAdapter(editTemplateFactory,
  ...     (zope.interface.Interface, z3c.jsonrpc.interfaces.IJSONRPCRequest),
  ...     z3c.template.interfaces.IContentTemplate)

  >>> from z3c.jsonrpc.testing import JSONRPCTestProxy
  >>> proxy = JSONRPCTestProxy('http://globalmgr:globalmgrpw@127.0.0.1/++skin++JSONRPCTestSkin/content/demoForm')
  >>> data = {'j01FormHandlerName':'applyChanges',
  ...         'form.widgets.title': u'Foo',
  ...         'form.widgets.description': u'Bar',
  ...         'form.buttons.applyChanges': u'Apply'}
  >>> result = proxy.j01FormProcessor(**data)
  >>> pprint(result)
    {u'content': u'<!DOCTYPE html PUBLIC...</html>\n',
     u'contentTargetExpression': None,
     u'nextHash': u'None',
     u'nextURL': u'',
     u'scrollToExpression': None,
     u'scrollToOffset': None,
     u'scrollToSpeed': None}

  >>> print result['contentTargetExpression'] is None
  True

  >>> print result['content']
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">
    <body>
      <form action=".">
        <div class="row">
          <label for="form-widgets-title">Title</label>
      <span id="form-widgets-title" class="text-widget required textline-field">Foo</span>
  </div>
        <div class="row">
          <label for="form-widgets-description">Description</label>
      <span id="form-widgets-description" class="text-widget required textline-field">Bar</span>
  </div>
        <div class="action">
  <input id="form-buttons-applyChanges" name="form.buttons.applyChanges" class="submit-widget jsonrpcbutton-field" value="Apply" type="submit" />
  </div>
        <div class="action">
  <input id="form-buttons-cancel" name="form.buttons.cancel" class="submit-widget jsonrpcbutton-field" value="Cancel" type="submit" />
  </div>
      </form>
    </body>
  </html>
