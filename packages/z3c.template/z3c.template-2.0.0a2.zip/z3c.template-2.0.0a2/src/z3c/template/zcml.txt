==================
Template directive
==================

Show how we can use the template directive. Register the meta configuration for
the directive.

  >>> import sys
  >>> from zope.configuration import xmlconfig
  >>> import z3c.template
  >>> context = xmlconfig.file('meta.zcml', z3c.template)


PageTemplate
------------

We need a custom content template

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> content_file = os.path.join(temp_dir, 'content.pt')
  >>> with open(content_file, 'w') as file:
  ...     _ = file.write('''<div>content</div>''')

and a interface

  >>> import zope.interface
  >>> class IView(zope.interface.Interface):
  ...     """Marker interface"""

and a view class:

  >>> from zope.publisher.browser import TestRequest
  >>> @zope.interface.implementer(IView)
  ... class View(object):
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request
  >>> request = TestRequest()
  >>> view = View(object(), request)

Make them available under the fake package ``custom``:

  >>> sys.modules['custom'] = type(
  ...     'Module', (),
  ...     {'IView': IView})()

and register them as a template within the ``z3c:template`` directive:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:template
  ...       template="%s"
  ...       for="custom.IView"
  ...       />
  ... </configure>
  ... """ % content_file, context=context)

Let's get the template

  >>> import zope.component
  >>> from z3c.template.interfaces import IContentTemplate
  >>> template = zope.component.queryMultiAdapter(
  ...     (view, request),
  ...     interface=IContentTemplate)

and check them:

  >>> from z3c.template.template import ViewPageTemplateFile
  >>> isinstance(template, ViewPageTemplateFile)
  True
  >>> isinstance(template.content_type, str)
  True

  >>> print(template(view))
  <div>content</div>


Layout template
---------------

Define a layout template

  >>> layout_file = os.path.join(temp_dir, 'layout.pt')
  >>> with open(layout_file, 'w') as file:
  ...     _ = file.write('''<div>layout</div>''')

and register them as a layout template within the ``z3c:layout`` directive:

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:layout
  ...       template="%s"
  ...       for="custom.IView"
  ...       />
  ... </configure>
  ... """ % layout_file, context=context)

Let's get the template

  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> layout = zope.component.queryMultiAdapter((view, request),
  ...     interface=ILayoutTemplate)

and check them:

  >>> isinstance(layout, ViewPageTemplateFile)
  True
  >>> isinstance(layout.content_type, str)
  True

  >>> print(layout(view))
  <div>layout</div>


Context-specific template
-------------------------

Most of views have some object as their context and it's ofter very
useful to be able register context-specific template. We can do that
using the ``context`` argument of the ZCML directive.

Let's define some content type:

  >>> class IContent(zope.interface.Interface):
  ...     pass
  >>> @zope.interface.implementer(IContent)
  ... class Content(object):
  ...     pass

  >>> sys.modules['custom'].IContent = IContent

Now, we can register a template for this class. Let's create one and
register:

  >>> context_file = os.path.join(temp_dir, 'context.pt')
  >>> with open(context_file, 'w') as file:
  ...     _ = file.write('''<div>i'm context-specific</div>''')

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:template
  ...       template="%s"
  ...       for="custom.IView"
  ...       context="custom.IContent"
  ...       />
  ... </configure>
  ... """ % context_file, context=context)

We can now lookup it using the (view, request, context) discriminator:

  >>> content = Content()
  >>> view = View(content, request)

  >>> template = zope.component.queryMultiAdapter((view, request, content),
  ...     interface=IContentTemplate)

  >>> print(template(view))
  <div>i'm context-specific</div>

The same will work with layout registration directive:

  >>> context_layout_file = os.path.join(temp_dir, 'context_layout.pt')
  >>> with open(context_layout_file, 'w') as file:
  ...     _ = file.write('''<div>context-specific layout</div>''')
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:layout
  ...       template="%s"
  ...       for="custom.IView"
  ...       context="custom.IContent"
  ...       />
  ... </configure>
  ... """ % context_layout_file, context=context)

  >>> layout = zope.component.queryMultiAdapter((view, request, content),
  ...     interface=ILayoutTemplate)

  >>> print(layout(view))
  <div>context-specific layout</div>


Named template
--------------

Its possible to register template by name. Let us register a pagelet with the
name edit:

  >>> editTemplate = os.path.join(temp_dir, 'edit.pt')
  >>> with open(editTemplate, 'w') as file:
  ...     _ = file.write('''<div>edit</div>''')

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:template
  ...       name="edit"
  ...       template="%s"
  ...       for="custom.IView"
  ...       />
  ... </configure>
  ... """ % editTemplate, context=context)

And call it:

  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> template = zope.component.queryMultiAdapter(
  ...     (view, request),
  ...     interface=IContentTemplate, name='edit')

  >>> print(template(view))
  <div>edit</div>


Custom template
---------------

Or you can define own interfaces and register templates for them:

  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> class IMyTemplate(IPageTemplate):
  ...     """My template"""

Make the template interface available as a custom module class.

  >>> sys.modules['custom'].IMyTemplate = IMyTemplate

Dfine a new template

  >>> interfaceTemplate = os.path.join(temp_dir, 'interface.pt')
  >>> with open(interfaceTemplate, 'w') as file:
  ...     _ = file.write('''<div>interface</div>''')

  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:template
  ...       template="%s"
  ...       for="custom.IView"
  ...       provides="custom.IMyTemplate"
  ...       />
  ... </configure>
  ... """ % interfaceTemplate, context=context)

Let's see if we get the template by the new interface:

  >>> from z3c.template.interfaces import ILayoutTemplate
  >>> template = zope.component.queryMultiAdapter((view, request),
  ...     interface=IMyTemplate,)

  >>> print(template(view))
  <div>interface</div>


Cleanup
-------

Now we need to clean up the custom module.

  >>> del sys.modules['custom']
