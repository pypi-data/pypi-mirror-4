Introduction
============

This package extends z3c.form and plone.z3cform for usage within PMR2
and related libraries.  Problems this package attempt to tackle are:

  - Ensure the correct root template is adapted when forms (and views/
    pages) are rendered, such that there will only be one class used for
    testing and production, without having to subclass for specific uses
    or make use of wrapper classes/methods.  It may be possible to
    support other frameworks by registering the root view to the desired
    layer.
  - CSRF (Cross-Site Request Forgery) prevention via the use of
    appropriate form authenticators, e.g. plone.protect for Plone.
  - Offer the same adaptable browser class (pages) to standard non-form
    views.
  - Forms with traversal subpaths.

Installation and usage
----------------------

Just add or modified the ``install_requires`` option into the setup
function in a typical ``setup.py``.   Example::

    from setuptools import setup
    
    setup(
        ...
        install_requires=[
            ...
            'pmr2.z3cform',
        ]
    )
