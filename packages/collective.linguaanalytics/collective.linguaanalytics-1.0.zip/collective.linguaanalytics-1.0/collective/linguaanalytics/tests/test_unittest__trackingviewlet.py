from collective.linguaanalytics.tests import base, utils
from collective.linguaanalytics.viewlets import analytics


class UnitTestAnalyticsTrackingViewlet(base.UnitTestCase):
    """unittest for the viewlet"""

    def setUp(self):
        super(UnitTestAnalyticsTrackingViewlet, self).setUp()
        init = analytics.AnalyticsTrackingViewlet
        self.viewlet = init(utils.FakeContext(), None, None, None)

    def test_init(self):
        init = analytics.AnalyticsTrackingViewlet
        viewlet = init(utils.FakeContext(), None, None, None)
        self.assertTrue(hasattr(viewlet, '_settings'))
        self.assertTrue(hasattr(viewlet, '_code'))
        self.assertTrue(hasattr(viewlet, '_navigation_root_url'))

    def test_available(self):
        #no settings
        self.assertTrue(not self.viewlet.available())

        #add working settings
        self.viewlet._settings = utils.FakeSettings()
        self.viewlet._navigation_root_url = 'http://nohost/plone'
        self.assertTrue(self.viewlet.available())

        #unactivate
        self.viewlet._settings.activated = False
        self.assertTrue(not self.viewlet.available())
        self.viewlet._settings.activated = True

        #remove mapping
        self.viewlet._settings.mapping = []
        self.viewlet._code = None
        self.assertTrue(not self.viewlet.available())

    def test_getTrackingWebProperty(self):
        self.viewlet._settings = utils.FakeSettings()
        self.viewlet._navigation_root_url = 'http://nohost/plone'
        code = self.viewlet.getTrackingWebProperty()
        self.assertTrue(code == "UA-xxxxxx-x")

        self.viewlet._code = "Foo"
        code = self.viewlet.getTrackingWebProperty()
        self.assertTrue(code == "Foo")
        self.viewlet._code = None

        #test bad url
        self.viewlet._navigation_root_url = 'http://notmapped/plone'
        code = self.viewlet.getTrackingWebProperty()
        self.assertTrue(code is None)

    def test_mapping(self):
        self.viewlet._settings = utils.FakeSettings()
        self.viewlet._settings.mapping = ['http://nohost|UA-xxxxxx-x',
                                          'http://nohost.fr|UA-yyyyyy-y',
                                          'BAD',
                                          None]
        mapping = self.viewlet.mapping
        self.assertTrue(mapping.get('http://nohost') == 'UA-xxxxxx-x')
        self.assertTrue(mapping.get('http://nohost.fr') == 'UA-yyyyyy-y')
        self.assertTrue(len(mapping) == 2)
