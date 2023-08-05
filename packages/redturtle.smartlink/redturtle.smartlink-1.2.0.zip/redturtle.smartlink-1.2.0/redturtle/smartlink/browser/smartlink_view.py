# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

class SmartLinkView(BrowserView):
    """View for Smart Link"""
    
    def getInternalLink(self):
        context = self.context
        if context.getInternalLink():
            return context.getInternalLink()
        if context.getInternalLinkPath():
            return context.restrictedTraverse(context.getInternalLinkPath(), None)
