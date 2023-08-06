Pages
=====

These were just simple rendering pages meant for wrapping by the layout
classes to be replaced by more standard Plone way of rendering 
templates.

Let's subclass one::

    >>> from pmr2.z3cform.tests.base import TestRequest
    >>> from pmr2.z3cform.page import SimplePage
    >>>
    >>> class TestPage(SimplePage):
    ...     template = lambda x: 'Hello'

Then render it::

    >>> context = self.portal
    >>> request = TestRequest()
    >>> page = TestPage(context, request)
    >>> print page()
    <h1 class="documentFirstHeading">Plone site</h1>
    <div id="content-core">
      <div>Hello</div>
    </div>

If we register this view on the main site, we should be able to render
this using the testbrowser.  This will then render the same page with
all the templates associated with Plone::

    >>> import zope.component
    >>> from Testing.testbrowser import Browser
    >>> zope.component.provideAdapter(TestPage, (None, None),
    ...     zope.publisher.interfaces.browser.IBrowserView,
    ...     name='pmr2z3cform-testpage')
    ... 
    >>> tb = Browser()
    >>> tb.open(context.absolute_url() + '/@@pmr2z3cform-testpage')
    >>> 'Plone - http://plone.org' in tb.contents
    True
    >>> '<div>Hello</div>' in tb.contents
    True

While traversal views are generally implementation specific, a quick
demonstration is still possible.  Try subclassing one::

    >>> from pmr2.z3cform.page import TraversePage
    >>>
    >>> class TestTraversePage(TraversePage):
    ...     _template = 'Subpath is: %s'
    ...     def template(self):
    ...          subpath = '/'.join(self.traverse_subpath)
    ...          return self._template % subpath

Manually simulate traversal and render the form::

    >>> context = self.portal
    >>> request = TestRequest()
    >>> page = TestTraversePage(context, request)
    >>> p = page.publishTraverse(request, 'a')
    >>> p = page.publishTraverse(request, 'b')
    >>> print page()
    <h1 class="documentFirstHeading">Plone site</h1>
    <div id="content-core">
      <div>Subpath is: a/b</div>
    </div>

Much like the SimplePage example, do the registration again::

    >>> zope.component.provideAdapter(TestTraversePage, (None, None),
    ...     zope.publisher.interfaces.browser.IBrowserView,
    ...     name='pmr2z3cform-testtraversepage')
    ... 
    >>> tb = Browser()
    >>> tb.open(context.absolute_url() + '/@@pmr2z3cform-testtraversepage' +
    ...     '/a/b/c/some_path')
    >>> 'Plone - http://plone.org' in tb.contents
    True
    >>> '<div>Subpath is: a/b/c/some_path</div>' in tb.contents
    True
