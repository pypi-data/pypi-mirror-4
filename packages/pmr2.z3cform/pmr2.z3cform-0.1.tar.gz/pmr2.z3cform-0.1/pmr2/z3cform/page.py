import zope.interface
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.browser import BrowserPage

from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.z3cform.interfaces import IPublishTraverse, IPage
from pmr2.z3cform.templates import path


page_factory = ZopeTwoFormTemplateFactory(path('page.pt'), form=IPage)


class SimplePage(BrowserPage):
    """\
    A simple view generator/page/template class.
    """

    zope.interface.implements(IPage)
    index = None
    template = None
    omit_index = False

    @property
    def url_expr(self):
        # URL expression for this view.
        return '%s/@@%s' % (self.context.absolute_url(), self.__name__)

    @property
    def url_subpath(self):
        # URL expression for the subpath.
        return ''

    @property
    def label(self):
        label = getattr(self.context, 'title_or_id', None)
        if callable(label):
            return label()

    def update(self):
        pass

    def render(self):
        if self.omit_index:
            if self.template is None:
                return ''

            if callable(self.template):
                return self.template()

            # XXX really should be callable...
            return template

        # render content template
        if self.index is None:
            index = zope.component.getMultiAdapter((self, self.request),
                IPageTemplate)
            return index(self)

        return self.index()


    def __call__(self, *a, **kw):
        self.update()
        return self.render()


class TraversePage(SimplePage):
    """\
    A simple page class that supports traversal.
    """

    zope.interface.implements(IPublishTraverse)

    def __init__(self, *a, **kw):
        super(TraversePage, self).__init__(*a, **kw)
        if not self.request.environ.get('pmr2.traverse_subpath', None):
            self.request.environ['pmr2.traverse_subpath'] = []

    @property
    def url_subpath(self):
        return '/'.join(tuple(self.traverse_subpath))

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self

    def _get_traverse_subpath(self):
        return self.request.environ['pmr2.traverse_subpath']

    def _set_traverse_subpath(self, value):
        self.request.environ['pmr2.traverse_subpath'] = value

    traverse_subpath = property(_get_traverse_subpath, _set_traverse_subpath)
