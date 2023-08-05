"""Definition of the SmartLink content type
"""

import urlparse
from urllib import quote

from zope import interface
from zope.component import getUtility, queryUtility
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import AnnotationStorage

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.link import ATLink, ATLinkSchema
from Products.ATContentTypes.interface import IImageContent
from Products.ATReferenceBrowserWidget import ATReferenceBrowserWidget

from redturtle.smartlink import smartlinkMessageFactory as _
from redturtle.smartlink.interfaces import ISmartLink, ISmartLinked
from redturtle.smartlink.interfaces.utility import ILinkNormalizerUtility
from redturtle.smartlink.config import PROJECTNAME

from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig

LinkSchema = ATLinkSchema.copy() + atapi.Schema((

    # HIDDEN!
    atapi.StringField('remoteUrl',
        searchable=True,
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_url', default=u'URL'),
            visible={'view': 'invisible', 'edit': 'invisible' },
        )
    ),

    atapi.StringField("externalLink",
              searchable=True,
              required=False,
              widget=atapi.StringWidget(
                    label= _(u'label_smartlink_externallink', default='External link'),
                    description = _(u'help_smartlink_externallink',
                                    default=u"Enter the web address for a page which is not located on this server."),
                    i18n_domain='redturtle.smartlink',
                    size=50,
              )
    ),

    atapi.ReferenceField("internalLink",
                   default=None,
                   relationship="internal_page",
                   multiValued=False, 
                   widget=ATReferenceBrowserWidget.ReferenceBrowserWidget(
                        label= _(u'label_smartlink_internallink', default='Internal link'),
                        description = _(u'help_smartlink_internallink',
                                        default=(u"Browse to find the internal page to which you wish to link. "
                                                 u"If this field is used, then any entry in the external link field will be ignored. "
                                                 u"You cannot have both an internal and external link.")),
                        force_close_on_insert = True,
                        i18n_domain='redturtle.smartlink',
                    )
    ),

    # ******* Advanced tab *******
    
    atapi.StringField('anchor',
        required = False,
        searchable = False,
        default='',
        schemata="Advanced",
        widget = atapi.StringWidget(
            label = _(u'label_image_anchor', default=u'Internal anchor'),
            description = _(u'help_image_anchor',
                            default=(u'Used only when the link is internal to the site. '
                                     u'Use this field to obtain an internal link to a section of the target document')),
            i18n_domain='redturtle.smartlink',
            size = 30)
        ),


    atapi.ImageField('image',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = zconf.ATNewsItem.max_image_dimension,
        schemata="Advanced",
        sizes=None,
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkNewsImageMaxSize', V_REQUIRED)),
        widget = atapi.ImageWidget(
            description = _(u'help_smartlink_image',
                            default=u"Will be shown views that render content's images and in the link view itself"),
            label= _(u'label_smartlink_image', default=u'Image'),
            i18n_domain='redturtle.smartlink',
            show_content_type = False)
        ),

    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        schemata="Advanced",
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            i18n_domain='redturtle.smartlink',
            size = 40)
        ),

    atapi.ImageField('favicon',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        max_size = (16, 16),
        schemata="Advanced",
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkNewsImageMaxSize', V_REQUIRED)),
        widget = atapi.ImageWidget(
            description = _(u'help_smartlink_favicon',
                            default=(u'You can customize there the content icon. '
                                     u'You can use this for provide the icon of the remote site')),
            label= _(u'label_smartlink_favicon', default=u'Icon'),
            i18n_domain='redturtle.smartlink',
            show_content_type = False)
        ),


))

LinkSchema['title'].storage = atapi.AnnotationStorage()
LinkSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(LinkSchema, moveDiscussion=False)

class SmartLink(ATLink):
    """A link to an internal or external resource."""
    interface.implements(ISmartLink, IImageContent)

    meta_type = "ATLink"
    schema = LinkSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    internalLink = atapi.ATReferenceFieldProperty('internalLink')
    
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'size')
    def size(self):
        """Get size of the content
        """
        return self.get_size()

    security.declareProtected(permissions.View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method
        Size is given from the sum of the two image field
        """
        size = 0
        f = self.getField('image')
        if f is not None:
            size+=f.get_size(self)
        f = self.getField('favicon')
        if f is not None:
            size+=f.get_size(self)        
        return size

    security.declareProtected(permissions.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image
        elif name=='favicon':
            field = self.getField('favicon')
            image = field.getScale(self)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image            

        return ATLink.__bobo_traverse__(self, REQUEST, name)

    security.declareProtected(permissions.ModifyPortalContent, 'setExternalLink')
    def setExternalLink(self, value, **kwargs):
        """remote url mutator
        Use urlparse to sanify the url
        Also see http://dev.plone.org/plone/ticket/3296
        """
        if value:
            value = urlparse.urlunparse(urlparse.urlparse(value))
        self.getField('externalLink').set(self, value, **kwargs)
        self.setRemoteUrl(self.getRemoteUrl())

    security.declareProtected(permissions.ModifyPortalContent, 'setInternalLink')
    def setInternalLink(self, value, **kwargs):
        self.getField('internalLink').set(self, value, **kwargs)
        self.setRemoteUrl(self.getRemoteUrl())

    security.declareProtected(permissions.View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """Return the URL of the link from the appropriate field, internal or external."""
        # We need to check if the self object has the reference_catalog attribute.
        # It's an integration problem with p4a that call this method when we don't have an internal link.
        if hasattr(self, 'reference_catalog'):
            ilink = self.getInternalLink()
        else:
            ilink = None

        # If we are using an internal link
        if ilink:
            anchor = self.getAnchor() or ''
            if anchor and not anchor.startswith("#"):
                anchor = '#'+anchor
            smartlink_config = queryUtility(ISmartlinkConfig, name="smartlink_config")
            if smartlink_config:
                if smartlink_config.relativelink:            
                    object = self.getField('internalLink').get(self)
                    remote = '/'.join(object.getPhysicalPath())
                    return quote(remote + anchor, safe='?$#@/:=+;$,&%')
            remote = ilink.absolute_url() + anchor
        else:
            remote = self.getExternalLink()

        remote = getUtility(ILinkNormalizerUtility).toFrontEnd(remote)

        # If we still haven't remote value now, let's return the "normal" field value
        if not remote:
            remote = self.getField('remoteUrl').get(self)
        return quote(remote, safe='?$#@/:=+;$,&%')

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        if not remote_url:
            remote_url = kwargs.get('remote_url', None)
        self.update(externalLink = remote_url, **kwargs)

    security.declareProtected(permissions.View, 'post_validate')
    def post_validate(self, REQUEST, errors):
        """Check to make sure that either an internal or external link was supplied."""
        if not REQUEST.form.get('externalLink') and not REQUEST.form.get('internalLink'):
            xlink=REQUEST.get('externalLink', None)
            ilink=REQUEST.get('internalLink', None)
            if (not xlink and not ilink):
                errors['externalLink'] = _("error_externallink_internallink_required",
                                           default=u'Please provide the external URL, or fill the "Internal link" field')
                errors['internalLink'] = _("error_internallink_externallink_required",
                                           default=u'Please provide the internal link, or fill the "External link" field')
            return errors
        if REQUEST.form.get('externalLink') and REQUEST.form.get('internalLink'):
            errors['externalLink'] = _("error_internallink_externallink_doubled",
                                       default=u'You must select an internal link or enter an external link. You cannot have both.')
            return errors

    security.declarePrivate('_processForm')
    def _processForm(self, data=1, metadata=None, REQUEST=None, values=None):
        """BBB: I need to check old value before change it...
        I don't find a good place where to put this code. Zope3 events don't help me"""
        form = self.REQUEST.form
        target = self.getInternalLink()
        if target and target.UID()!=form.get('internalLink') and ISmartLinked.providedBy(target):
            interface.noLongerProvides(target, ISmartLinked)
        ATLink._processForm(self, data=data, metadata=metadata, REQUEST=REQUEST, values=values)

    security.declareProtected(permissions.View, 'getIcon')
    def getIcon(self, relative_to_portal=0):
        """If a favicon was provided, show it"""
        if not self.getFavicon():
            return ATLink.getIcon(self, relative_to_portal)

        utool = getToolByName(self, 'portal_url')
        if relative_to_portal:
            return self.absolute_url().replace(utool()+'/',"") + '/favicon'
        # Relative to REQUEST['BASEPATH1']
        res = utool(relative=1) + self.absolute_url().replace(utool(),"") + '/favicon'
        while res[:1] == '/':
            res = res[1:]
        return res


    security.declareProtected(permissions.View, 'getInternalLinkPath')
    def getInternalLinkPath(self):
        """Get database path to the internally linked content"""
        ilink = self.getInternalLink()
        if ilink:
            return '/'.join(ilink.getPhysicalPath())
        if not ilink and not self.getExternalLink():
            # Try this way... this seems the only way to get the referenced object when we are deleting
            # No event will help us... neither OFS.interfaces.IObjectWillBeRemovedEvent
            portal_url = getToolByName(self, 'portal_url')
            internalPath = self.getRemoteUrl().replace(getUtility(ILinkNormalizerUtility).toFrontEnd(portal_url()), '')
            if not internalPath.startswith('/' + portal_url.getPortalObject().getId()):
                internalPath = '/' + portal_url.getPortalObject().getId() + internalPath
            return internalPath
        return None
        

atapi.registerType(SmartLink, PROJECTNAME)
