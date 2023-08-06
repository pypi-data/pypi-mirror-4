# -*- coding: utf-8 -*-

from zope.component import getUtility
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from redturtle.smartlink.interfaces.link import ISmartLink
from redturtle.smartlink.interfaces.utility import ILinkNormalizerUtility
from redturtle.smartlink import smartlinkMessageFactory as _

class FixFakeInternalLinkView(BrowserView):
    """
    A view that looks for all Smart Link content types defined as external link
    but that contain URL's that point to internal contents.
    """
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._status = []


    def __call__(self):
        request = self.request
        request.set('disable_border', True)
        
        if request.form.get('path', []):
            self._fixURLs()
        return self.index()


    def _fixURLs(self):
        paths = self.request.form['path']
        context = self.context
        for path in paths:
            obj = context.restrictedTraverse(path, None)
            if obj:
                linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
                # use getRemoteUrl below, not getExternalLink; in this way we can fix
                # also links that loose all internal/external information
                remote = linkNormalizerUtility.toCurrent(obj.getRemoteUrl())
                linked = self.findInternalByURL(remote)
                if linked:
                    obj.edit(internalLink=linked.UID(),
                             externalLink='')
                    self._status.append({'msg': _('link_fixed_message',
                                                  default=u'External link fixed: ${origin} now links ${linked}',
                                                  mapping={'origin': obj.absolute_url_path(),
                                                           'linked': linked.absolute_url_path()}),
                                         'type': 'info'})
                else:
                    self._status.append({'msg': _('link_fixed_not_found_message',
                                                  default=u'Cannot find internal content at ${linked}',
                                                  mapping={'linked': remote}),
                                         'type': 'error'})
            else:
                self._status.append({'msg': _('link_fixed_not_found_message',
                                              default=u'Cannot find internal content at ${linked}',
                                              mapping={'linked': path}),
                                     'type': 'error'})
        return paths
    
    @property
    def status(self):
        return self._status or None


    def findInternalByURL(self, url):
        """
        Given a valid site URL, return the linked internal content, if any
        """
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        if url.startswith('resolveuid/') or url.startswith('/resolveuid/'):
            uid = url[url.find('resolveuid/')+11:]
            brain = catalog(UID=uid)
            return brain and brain[0].getObject() or None
        portal_url = getToolByName(context, 'portal_url')
        site_url = portal_url()
        portal = portal_url.getPortalObject()
        path = url.replace(site_url, '', 1)
        brain = catalog(path={'query': "/%s%s" % (portal.getId(), path),
                              'depth': 0})
        return path and brain and brain[0].getObject() or None


    def getFakeLinks(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        portal_url = getToolByName(self.context, 'portal_url')()
        links = catalog(object_provides=ISmartLink.__identifier__,
                        sort_on='sortable_title')
        linkNormalizerUtility = getUtility(ILinkNormalizerUtility)
        results = []
        for x in links:
            obj = x.getObject()
            # Sometimes you can loose all internal/external data, but the original
            # remoteUrl value always keep the up-to-date copy of the URL
            external_link = obj.getExternalLink() or \
                        (not obj.getInternalLink() and obj.getField('remoteUrl').get(obj))
            if external_link:
                external_link = linkNormalizerUtility.toCurrent(external_link)
                if external_link.startswith(portal_url) \
                            or external_link.startswith('resolveuid/') \
                            or external_link.startswith('/resolveuid/'):
                    internalObj = self.findInternalByURL(external_link)
                    results.append({'path': '/'.join(obj.getPhysicalPath()),
                                    'title': obj.Title(),
                                    'absolute_url_path': obj.absolute_url_path(), 
                                    'url': obj.absolute_url(),
                                    'external_link': external_link,
                                    'internal_obj': internalObj,
                                    })
        return results
