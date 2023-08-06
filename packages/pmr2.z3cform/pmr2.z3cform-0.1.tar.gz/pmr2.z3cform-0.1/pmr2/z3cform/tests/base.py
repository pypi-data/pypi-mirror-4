import hmac

import zope.interface
import zope.component
from zope.annotation import IAnnotations
import z3c.form.testing

from plone.browserlayer.utils import register_layer
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import _getUserName
from plone.protect.authenticator import sha

from Testing import ZopeTestCase as ztc

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup, onteardown


@onsetup
def setup():
    import pmr2.z3cform
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', pmr2.z3cform)
    zcml.load_config('testing.zcml', pmr2.z3cform.tests)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.z3cform')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.z3cform',))


class IPMR2TestRequest(zope.interface.Interface):
    """
    Marker for PMR2 test request
    """


class TestRequest(z3c.form.testing.TestRequest):
    """
    Customized TestRequest to mimic missing actions.
    """

    # IAnnotations applied by plone.z3cform test case.
    zope.interface.implements(IAnnotations, IPMR2TestRequest)
    def __init__(self, *a, **kw):
        super(TestRequest, self).__init__(*a, **kw)
        self.environ = {}
        if self.form:
            self.method = 'POST'
            self._set_authenticator()

    def __setitem__(self, key, value):
        self.form[key] = value

    def __getitem__(self, key):
        try:
            return super(TestRequest, self).__getitem__(key)
        except KeyError:
            return self.form[key]

    def _set_authenticator(self):
        manager = zope.component.queryUtility(IKeyManager)
        if not manager:
            # Since the key manager is not installed, authenticator 
            # should not be working anyway.
            return
        secret = manager.secret()
        user = _getUserName()
        auth = hmac.new(secret, user, sha).hexdigest()
        self['_authenticator'] = auth

    def getApplicationURL(self):
        # XXX compatibility with the more strict redirection introduced
        # with zope.publisher-3.12, http.redirect's untrusted attribute.
        return 'http://nohost:80'


class DocTestCase(ptc.FunctionalTestCase):
    """
    Modify the test case to inject our layer into the request.
    """

    def setUp(self):
        super(DocTestCase, self).setUp()
        register_layer(IPMR2TestRequest, 'pmr2.z3cform.tests')

    def tearDown(self):
        super(DocTestCase, self).tearDown()
