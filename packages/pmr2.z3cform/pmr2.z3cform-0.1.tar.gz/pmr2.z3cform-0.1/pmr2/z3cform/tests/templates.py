import os.path
import z3c.form.interfaces
from zope.publisher.browser import BrowserView
from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.z3cform.tests.base import IPMR2TestRequest

path = lambda p: os.path.join(os.path.dirname(__file__), p)

standalone_form_factory = ZopeTwoFormTemplateFactory(path('form.pt'),
        form=z3c.form.interfaces.IForm,
        request=IPMR2TestRequest,
    )
