# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class LinkRedirectView(BrowserView):
    """Simulate what the link_redirect_view.py script does for ATLink"""

    def __call__(self, request=None, response=None):
        context = self.context
        ptool = getToolByName(context, 'portal_properties')
        mtool = getToolByName(context, 'portal_membership')

        redirect_links = getattr(ptool.site_properties, 'redirect_links', False)
        can_edit = mtool.checkPermission('Modify portal content', context)

        if redirect_links and not can_edit:
            return context.REQUEST.RESPONSE.redirect(context.getRemoteUrl())
        else:
            return context.restrictedTraverse('@@smartlink_view')()
