from zope import interface
from collective.googleanalytics.interfaces.browserlayer import IAnalyticsLayer

from collective.linguaanalytics.controlpanel import \
    ISettingsSchema  # @UnusedImport


class ILayer(interface.Interface, IAnalyticsLayer):
    """Marker interface that defines a Zope 3 browser layer."""
