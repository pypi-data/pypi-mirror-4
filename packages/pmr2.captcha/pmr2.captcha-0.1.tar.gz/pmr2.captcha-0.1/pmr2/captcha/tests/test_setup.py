from unittest import TestSuite, makeSuite

from plone.browserlayer.layer import mark_layer
from zope.app.publication.zopepublication import BeforeTraverseEvent

from pmr2.testing.base import TestCase


class TestProductInstall(TestCase):

    def afterSetUp(self):
        self.addProfile('pmr2.captcha:default')
        event = BeforeTraverseEvent(self.portal, self.portal.REQUEST)
        mark_layer(self.portal, event)

    def testLayerApplied(self):
        from pmr2.captcha.interfaces import ICaptchaLayer
        self.assertTrue(ICaptchaLayer.providedBy(self.portal.REQUEST))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
