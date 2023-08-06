Forms
=====

Forms in PMR2 are built on top of z3c.forms.  There are certain changes
we made to allow this library to better fit into our use cases.  There
are a couple modifications, the first being the enforcement of request
method, and the other is CSRF (Cross-site Request Forgery) protection.

First we import some base classes and create a test form class::

    >>> import zope.interface
    >>> import zope.schema
    >>> import z3c.form.field
    >>> from z3c.form.testing import TestRequest
    >>> from pmr2.z3cform.tests import base
    >>> from pmr2.z3cform.form import AddForm
    >>>
    >>> class IDummy(zope.interface.Interface):
    ...     id = zope.schema.DottedName(title=u'id')
    ...
    >>> class Dummy(object):
    ...     zope.interface.implements(IDummy)
    ...     def __init__(self, id_):
    ...         self.id = id_
    ...
    >>> class TestAddForm(AddForm):
    ...     fields = z3c.form.field.Fields(IDummy)
    ...     def create(self, data):
    ...         return Dummy(data['id'])
    ...     def add_data(self, ctxobject):
    ...         ctxobject.id = self._data['id']
    ...     def add(self, obj):
    ...         self.context.append(obj)
    ...     def nextURL(self):
    ...         return ''  # unnecessary.

First thing to demonstrate is is the request method verification.  Forms
that manipulate data must not be activated by a simple GET request::

    >>> context = []
    >>> request = TestRequest(form={
    ...     'form.widgets.id': 'test',
    ...     'form.buttons.add': '1',
    ... })
    >>> request.method = 'GET'
    >>> form = TestAddForm(context, request)
    >>> result = form()
    Traceback (most recent call last):
    ...
    Unauthorized: Unauthorized()
    >>> context == []
    True

On the other hand, POST requests will not trigger the permission error::

    >>> request.method = 'POST'
    >>> form = TestAddForm(context, request)
    >>> form.disableAuthenticator = True
    >>> result = form()
    >>> print context[0].id
    test

However, notice that the security authenticator is disabled.  What this
provide is the check for a CSRF prevention token that must be part of a
request.  Now try the above with the check enabled, as it will be by
default::

    >>> context = []
    >>> request.method = 'POST'
    >>> form = TestAddForm(context, request)
    >>> result = form()
    Traceback (most recent call last):
    ...
    Unauthorized: Unauthorized()
    >>> context == []
    True

If the token is provided, as part of a normal form submission process
using a form rendered by this site, the token will be included within
a hidden input field.  In the case of Plone, this token is provided by
an authenticator view.  If we include the generated token the form
will be submitted properly::

    >>> context = []
    >>> authed_request = base.TestRequest(form=request.form)
    >>> authed_request.method = 'POST'
    >>> '_authenticator' in authed_request.form
    True
    >>> form = TestAddForm(context, authed_request)
    >>> result = form()
    >>> print context[0].id
    test
