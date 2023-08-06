import os.path

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform import templates

path = lambda p: os.path.join(os.path.dirname(__file__), 'templates', p)


class PlainMainMacros(templates.Macros):
    """\
    Trying to make life easier for general testing
    """

    index = ViewPageTemplateFile(path('plain-main-macros.pt'))


class PloneMainMacros(templates.Macros):
    """\
    The main macros, including templates.
    """

    index = ViewPageTemplateFile(path('plone-main-macros.pt'))
