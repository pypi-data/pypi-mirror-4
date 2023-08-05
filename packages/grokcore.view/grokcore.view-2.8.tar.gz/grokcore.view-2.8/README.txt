This package provides support for writing browser pages for Zope
and registering them directly in Python (without ZCML).

.. contents::

Setting up ``grokcore.view``
============================

This package is essentially set up like the `grokcore.component`_
package, please refer to its documentation for details.  The
additional ZCML line you will need is::

  <include package="grokcore.view" file="meta.zcml" />
  <include package="grokcore.view" />

Put the first line somewhere near the top of your root ZCML file (but
below the line where you include ``grokcore.component``'s
configuration) and the second line somewhere next to your other
dependency includes.


Examples
========

Simple browser page
-------------------

A browser page is implemented by subclassing the
``grokcore.view.View`` baseclass.  At a minimum, a browser page must
have

1. an associated template (or implement the ``render`` method for direct
   control)

2. a context that it's registered for as a view

3. a name (which is, if not specified explicitly, the class's name in
   lower case characters).

A browser page that does not use a template but just outputs some
computed data also subclasses the ``grokcore.view.View`` baseclass.
At a minimum, such a view must have

1. a render() method

2. a context that it's registered for as a view

3. a name (which is, if not specified explicitly, the class's name in
   lower case characters).

For example, the following class defines a view that's registered for
all objects and simply prints "Hello World!"::

  import grokcore.view
  import zope.interface

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)

      def render(self):
          self.response.setHeader("Content-Type", "text/plain")
          return "Hello World!"

Here we've made use of the implicit name feature.  This class will be
available as the ``hello`` view for all objects.  So for instance,
you'll be able to invoke it with URLs like::

  http://localhost/some/obj/hello

We could also have spelled this out explicitly::

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)
      grokcore.view.name('hello')

      ...

Browser page with template
--------------------------

Of course, more than often a view should render HTML which you would
construct using some sort of templating engine.  ``grokcore.view``
comes with built-in support for Zope's PageTemplate engine.  By
convention, PageTemplate templates end with the ``.pt`` extension.

So let our ``Hello`` view render HTML instead of plain text, we remove
the ``render()`` method from the class and instead we create a
template, e.g. like so::

  <html>
  <body>
    <p>Hello <span tal:replace="request/principal/title" />!</p>
  </body>
  </html>

This will greet a logged in user with his or her actual name.

Such a template-using page is a subclass of ``grokcore.view.View``::

  import grokcore.view
  import zope.interface

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)


To associate the template with the view, we have to put it in a
certain place.  Let's say the ``Hello`` view class from above was in
an ``app.py`` module.  Then we create an ``app_templates`` directory
next to it and place the template file in there (the name of this
directory can be customized with the ``templatedir`` directive, see
below).  The file name can be anything as long as the extension is
``.pt``.  However, we can again make use of a convention here.  If we
name the template like the class (except in lower case characters),
then the template and the class are associated automatically.  If not,
we would have to use the ``template`` directive on the view class to
spell out the name of the template file explicitly.

To cut a long story short, if we named it ``app_templates/hello.pt``,
it would be found automatically.

Static resources
----------------

Browser pages often need additional static resources like CSS and JavaScript
files. These can be conveniently placed into a directory called ``static`` in
the package that contains the view code. When this directory exists it will
automatically be registered as a resource directory. It then is available as
the ``static`` variable in all views of this package and you can refer to files
inside this directory like so::

  <img src="hello.png" tal:attributes="src static/hello.png" />

DirectoryResource
-----------------

In addition to the very convenient "static resources", one can use more
explicitly configured and flexible DirectoryResource components.
DirectoryResource component allow for differentiating resources based on layers
and names and provide a way to register resources in one package and make use
of these resources in another package's views::

  class FooResource(grokcore.view.DirectoryResource):
      grokcore.view.path('foo')

Or with an explicit name::

  class BarResource(grokcore.view.DirectoryResource):
      grokcore.view.name('bar')
      grokcore.view.path('bar')

Registered for a layer::

  class BazResource(grokcore.view.DirectoryResource):
      grokcore.view.layer(ISomeLayer)
      grokcore.view.path('baz/qux')

Layers and skins
----------------

To define a browser layer, simply extend the ``IBrowserRequest``
interface::

  class IGreenLayer(grokcore.view.IBrowserRequest):
      pass

If you then wanted to define a skin, simply inherit from all the layer
interfaces that should be in the skin and use the ``skin()`` directive
to give the layer a name::

  class IGreenSkin(IGreenLayer, grokcore.view.IDefaultBrowserLayer):
      grokcore.view.skin('Green')

To place a view on a layer, simply use the ``layer`` directive::

  class Hello(grokcore.view.View):
      grokcore.view.context(zope.interface.Interface)
      grokcore.view.layer(IGreenLayer)

      ...


API overview
============

Base classes
------------

``View``
    Base class for browser pages.  Use the ``context`` directive to
    specify the view's context.  Use the ``name`` directive to set the
    view's name; if not used, the view's name will be the class's name
    in lower case characters.  You may also use the ``template``
    directive to specify the name of the template file that should be
    associated with the view as well as the ``layer`` directive to
    specify which layer it should be on if not the default layer.
    Implement the ``render`` method to forgo looking up a template
    and show the result of calling the render method instead.

View API
--------

``grokcore.view.View`` is a regular Zope browser page, so it behaves
exactly like a regular browser page from the outside.  It provides a
bit more to the developer using it as a base class, though:

``context``
    The view's context object.  This can be discriminated by using the
    ``context`` directive on the view class.

``request``
    The request object, typically provides ``IBrowserRequest``.

``response``
    The response object, typically provides ``IHTTPResponse``.

``static``
    Directory resource representing the package's ``static`` directory or None
    if no such directory was found during grokking.

``redirect(url)``
    Redirect to the given URL.

``url(obj=None, name=None, data=None)``
    Constructs a URL:

    * If no arguments are given, the URL to the view itself is
      constructed.

    * If only the ``obj`` argument is given, the URL to that object is
      constructed.

    * If both ``obj`` and ``name`` arguments are supplied, construct
      the URL to the object and append ``name`` (presumably the name
      of a view).

    Optionally, ``data`` can be a dictionary whose contents is added to
    the URL as a query string.

Method for developers to implement:

``update(**kw)``
    This method will be called before the view's associated template
    is rendered.  If you therefore want to pre-compuate values for the
    template, implement this method.  You can save the values on
    ``self`` (the view object) and later access them through the
    ``view`` variable from the template.  The method can take
    arbitrary keyword parameters which are filled from request values.

``render(**kw)`` 
    Return either an encoded 8-bit string or a unicode string.  The method can
    take arbitrary keyword parameters which are filled from request values.
    If not implemented, a template is looked up in the template dir instead.


Directives
----------

``templatedir(dirname)``
     Module-level directive that tells the template machinery which
     directory to look in for templates that should associated with
     views in a particular module.  If not used, it defaults to
     ``<module_name>_templates``.

``template(filename_wo_ext)``
    Class-level directive that specifies the name a template file
    that's associated with a view class, *without* the file extension.
    If not used, it defaults to the class's name in lower case
    characters.

``layer(layer_interface)``
    Class-level directive that defines which layer the view is
    registered on.  If not used, it defaults to the
    ``IDefaultBrowserLayer``.

``skin(skin_name)``
    Directive used on a layer interface to register it as skin using a
    human-readable name (``skin_name``).

``path(relative_or_absolute_path)``
    Directove used in a DirectoryResource registration to point to a non-
    package directory(hierarchy) containing resources like images, css files,
    etc.

Other
-----

``url(request, obj, name=None, data=None)``
    Generate the URL to an object, with an optional view name
    attached.  The ``data`` argument can be a dictionary whose
    contents is converted into the a query string that's appended to
    the URL.

``PageTemplate(template_code)``
    Create an inline PageTemplate object.

``PageTemplateFile(filename)``
    Create a PageTemplate object from a file.

``IBrowserRequest``
    Browser request interface from ``zope.publisher``.

``IDefaultBrowserLayer``
    Default layer for browser components from ``zope.publisher``.


In addition, the ``grokcore.view`` package exposes the
`grokcore.component`_ and `grokcore.security`_ APIs.

.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component
.. _grokcore.security: http://pypi.python.org/pypi/grokcore.security
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view

