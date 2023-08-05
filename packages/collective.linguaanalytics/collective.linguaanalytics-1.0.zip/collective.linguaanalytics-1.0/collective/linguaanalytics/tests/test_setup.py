import unittest2 as unittest
from collective.linguaanalytics.tests import base
from plone.browserlayer import utils


class TestSetup(base.IntegrationTestCase):
    """We tests the setup (install) of the addons. You should check all
    stuff in profile are well activated (browserlayer, js, content types, ...)
    """

    def test_browserlayer(self):
        from collective.linguaanalytics.interfaces import ILayer
        layers = utils.registered_layers()
        self.assertIn(ILayer, layers)


class TestUninstall(base.IntegrationTestCase):
    """Test if the addon uninstall well"""

    def setUp(self):
        super(TestUninstall, self).setUp()
        qi = self.portal['portal_quickinstaller']
        qi.uninstallProducts(products=['collective.linguaanalytics'])

    def test_uninstall_browserlayer(self):
        from collective.linguaanalytics.interfaces import ILayer
        layers = utils.registered_layers()
        self.assertNotIn(ILayer, layers)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
