from unittest import TestSuite, makeSuite

from plone.browserlayer.layer import mark_layer
from zope.app.publication.zopepublication import BeforeTraverseEvent

from Products.PloneTestCase import PloneTestCase as ptc


class TestProductInstall(ptc.PloneTestCase):

    def afterSetUp(self):
        self.addProfile('pmr2.z3cform:default')
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)

    def testLayerApplied(self):
        from pmr2.z3cform.interfaces import IFormLayer
        self.assertTrue(IFormLayer.providedBy(self.portal.REQUEST))

    def testLayerOrder(self):
        from plone.app.z3cform.interfaces import IPloneFormLayer
        from pmr2.z3cform.interfaces import IFormLayer

        layers = self.portal.REQUEST.__provides__.__iro__
        # The marker layer for pmr2.z3cform must be higher than the 
        # default plone form layer.
        self.assertTrue(
            layers.index(IFormLayer) < layers.index(IPloneFormLayer))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
