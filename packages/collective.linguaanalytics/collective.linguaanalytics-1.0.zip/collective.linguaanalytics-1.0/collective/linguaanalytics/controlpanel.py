from zope import interface
from zope import schema
from zope import i18nmessageid

from plone.app.registry.browser import controlpanel as base
from plone.registry import field
_ = i18nmessageid.MessageFactory('collective.linguanalytics')


class ISettingsSchema(interface.Interface):
    """Settings for this addon"""

    activated = schema.Bool(title=_(u"Is activated"),
                            description=_(u"Uncheck to unactivate this addon"),
                            default=True)

    mapping = schema.List(title=_(u"URL - Code Google Analytics"),
                          default=[],
                          value_type=field.URI(title=_(u"URL|Code"),
                               description=_(u"http://mysite.com|UA-XXXXX-Y")))


class ControlPanelForm(base.RegistryEditForm):
    schema = ISettingsSchema
    label = _(u"Google analytics control panel")
    #TODO: validate all urls !!!!


class ControlPanelView(base.ControlPanelFormWrapper):
    form = ControlPanelForm
