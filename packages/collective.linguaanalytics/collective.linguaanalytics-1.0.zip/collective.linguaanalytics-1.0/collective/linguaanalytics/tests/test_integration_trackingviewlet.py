from collective.linguaanalytics.tests import base
from collective.linguaanalytics.viewlets import analytics
from zope.schema.interfaces import WrongContainedType


class IntegrationTestAnalyticsTrackingViewlet(base.IntegrationTestCase):
    """unittest for the viewlet"""

    def setUp(self):
        super(IntegrationTestAnalyticsTrackingViewlet, self).setUp()
        init = analytics.AnalyticsTrackingViewlet
        self.request = self.layer['request']
        self.viewlet = init(self.portal, self.request, None, None)

    def test_init(self):
        init = analytics.AnalyticsTrackingViewlet
        viewlet = init(self.portal, self.request, None, None)
        self.assertTrue(hasattr(viewlet, '_settings'))
        self.assertTrue(hasattr(viewlet, '_code'))
        self.assertTrue(hasattr(viewlet, '_navigation_root_url'))

    def test_available(self):
        #no mapping
        self.assertTrue(not self.viewlet.available())

        #add working mapping
        self.viewlet.settings.mapping = ['http://nohost/plone|UA-xxxxxx-x']
        self.assertTrue(self.viewlet.available())

        #unactivate
        self.viewlet.settings.activated = False
        self.assertTrue(not self.viewlet.available())
        self.viewlet.settings.activated = True

    def test_getTrackingWebProperty(self):
        self.viewlet.settings.mapping = ['http://nohost/plone|UA-xxxxxx-x']
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
        self.viewlet.settings.mapping = ['http://nohost|UA-xxxxxx-x',
                                         'http://nohost.fr|UA-yyyyyy-y']
        self.assertRaises(WrongContainedType,
                          self.viewlet.settings.__setattr__,
                          'mapping',
                          [None])
        self.assertRaises(WrongContainedType,
                          self.viewlet.settings.__setattr__,
                          'mapping',
                          ['BAD'])
        mapping = self.viewlet.mapping
        self.assertTrue(mapping.get('http://nohost') == 'UA-xxxxxx-x')
        self.assertTrue(mapping.get('http://nohost.fr') == 'UA-yyyyyy-y')
        self.assertTrue(len(mapping) == 2)
