from zope.interface import Interface
from zope import schema
from redturtle.smartlink import smartlinkMessageFactory as _
from zope.interface import invariant, Invalid

from plone.app.controlpanel.interfaces import IPloneControlPanelForm

class ISmartLinkControlPanelForm(IPloneControlPanelForm):
    """Interface for configuration panel inside SmartLink"""


class ILinkNormalizerUtility(Interface):
    """Utility for transform URLs to make them using valid internal hostnames"""

    def toFrontEnd(remote):
        """Transform an URL to the proper frontend ones"""
    
    def toCurrent(remote):
        """Tranform an URL to a compatible type, like the current ones"""

class ISmartlinkConfig(Interface):

    relativelink = schema.Bool(
        title=_(u"Relative links"),
        description=_(u'help_relativelink',
                      default=(u'If selected, all internal links in the site will store URLs relative to the portal root, '
                               u'rather than absolute save the complete absolute ones. '
                               u'For example: no "http://myhost/plone/foo" but "/plone/foo"')),
        required=False
    )

    frontend_main_link = schema.TextLine(
        title=_(u"Front-end main URL"),
        description=_(u'help_frontend_main_link',
                      default=(u'Put there the site main URL you want to expone to visitors. '
                               u'All Smart Link that starts with the current URL of the portal '
                               u'will be transformed to use this URL.')),
        default=u'',
        required=False
    )

    backendlink = schema.List(
        title=_(u"Back-end URLs"),
        description=_(u'help_backendlink',
                      default=(u'Put there all your possible back-office URLs you want to transform. '
                               u'URLs there must be unique')),
        value_type=schema.TextLine(),
        default=[],
        unique=True,
        required=False
    )
    
    frontendlink = schema.List(
        title=_(u"Front-end URLs"),
        description=_(u'help_frontendlink',
                      default=u'Fill there URLs in which you want to change the relative back-end ones.'),
        value_type=schema.TextLine(),
        default=[],
        unique=False,
        required=False
    )
    
    @invariant
    def otherFilledIfSelected(smartlink):
        if len(smartlink.frontendlink) != len(smartlink.backendlink):
            raise Invalid(_(u"Front-end link must correspond to a single back-end link"))
    