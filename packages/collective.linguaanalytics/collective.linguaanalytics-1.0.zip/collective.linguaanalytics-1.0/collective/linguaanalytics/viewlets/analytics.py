from zope import component

from plone.registry.interfaces import IRegistry

from collective.googleanalytics.viewlets import tracking
from collective.linguaanalytics import interfaces


class AnalyticsTrackingViewlet(tracking.AnalyticsTrackingViewlet):
    """Override this one"""

    def __init__(self, context, request, view, manager):
        super(AnalyticsTrackingViewlet, self).__init__(context, request, view,
                                                       manager)
        self._settings = None
        self._code = None
        self._navigation_root_url = None

    def getTrackingWebProperty(self):
        """
        Returns the Google web property ID for the selected tracking profile,
        or an empty string if no tracking profile is selected.
        """
        if self._code is None:
            mapping = self.mapping
            url = self.navigation_root_url()
            self._code = mapping.get(url)
        return self._code

    def available(self):
        """
        Checks to see whether the viewlet should be rendered based on the role
        of the user and the selections for excluded roles in the configlet.
        """
        if not self.settings:
            return False
        isActivated = self.settings.activated
        hasCode = bool(self.getTrackingWebProperty())
        #TODO: add excluded role
        return isActivated and hasCode

    @property
    def settings(self):
        if not self._settings:
            registry = component.queryUtility(IRegistry)

            if registry:
                s = registry.forInterface(interfaces.ISettingsSchema,
                                          check=False)
                self._settings = s

        return self._settings

    def navigation_root_url(self):

        if not self._navigation_root_url:
            portal_state = component.queryMultiAdapter((self.context,
                                                      self.request),
                                                     name="plone_portal_state")
            self._navigation_root_url = portal_state.navigation_root_url()

        return self._navigation_root_url

    @property
    def mapping(self):
        mapping = {}
        url_codes = self.settings.mapping
        for url_code in url_codes:
            if not url_code:
                continue
            if not '|' in url_code:
                continue
            url, code = url_code.split('|')
            mapping[url] = code
        return mapping
