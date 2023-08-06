import zope.schema
import zope.interface
import zope.publisher.interfaces
from plone.app.z3cform.interfaces import IPloneFormLayer

from pmr2.z3cform.i18n import MessageFactory as _


class IFormLayer(IPloneFormLayer):
    """\
    Marker interface for the customized forms.
    """


class IPublishTraverse(zope.publisher.interfaces.IPublishTraverse):
    """\
    Our specialized traversal class with specifics defined.
    """

    traverse_subpath = zope.schema.List(
        title=_(u'Traverse Subpath'),
        description=_(u'A list of traversal subpaths that got captured.'),
    )


class IAuthenticatedForm(zope.interface.Interface):
    """\
    Interface for authenticated forms.
    """

    disableAuthenticator = zope.schema.Bool(
        title=_('Disable Authenticator'),
        description=_('Disable CSRF protection authenticator.'),
        default=False,
        required=True,
    )

    def authenticate():
        """\
        Authenticate request.
        """


class IPage(zope.interface.Interface):
    """\
    Interface for a page.
    """
