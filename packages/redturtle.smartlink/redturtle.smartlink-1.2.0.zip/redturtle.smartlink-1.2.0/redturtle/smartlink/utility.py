# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import queryUtility
from redturtle.smartlink.interfaces.utility import ISmartlinkConfig, ILinkNormalizerUtility
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite


def rn_config_adapter(context):
    """Form Adapter"""
    return queryUtility(ISmartlinkConfig, name="smartlink_config", context=context)


class SmartlinkConfig(SimpleItem):
    """Smartlink Utility"""
    implements(ISmartlinkConfig)
    frontend_main_link = FieldProperty(ISmartlinkConfig['frontend_main_link'])
    relativelink = FieldProperty(ISmartlinkConfig['relativelink'])
    frontendlink = FieldProperty(ISmartlinkConfig['frontendlink'])
    backendlink = FieldProperty(ISmartlinkConfig['backendlink'])


class LinkNormalizerUtility(object):
    """ See ILinkNormalizerUtility
    """
    implements(ILinkNormalizerUtility)

    def toFrontEnd(self, remote):
        smartlink_config = queryUtility(ISmartlinkConfig, name="smartlink_config")
        portal = getSite()
        remote = remote or ''
        if smartlink_config:
            backendlinks = getattr(smartlink_config, 'backendlink', [])
            frontend_main_link = getattr(smartlink_config, 'frontend_main_link', '')

            # Unified front-end link
            if frontend_main_link:
                portal_url = getToolByName(portal, 'portal_url')()
                if remote.startswith(portal_url):
                    remote = remote.replace(portal_url, frontend_main_link)
            # Advanced back-end/front-end configuration
            else:
                for backendlink in backendlinks:
                    blink = backendlink[-1]=='/' and backendlink[:-1] or backendlink
                    blink = blink.encode('utf-8')
                    if remote.startswith(blink):
                        frontendlinks = smartlink_config.frontendlink
                        frontendlink = frontendlinks[backendlinks.index(backendlink)]
                        frontendlink = frontendlink[-1]=='/' and frontendlink[:-1] or frontendlink
                        remote = remote.replace(blink, frontendlink)
                        break
        return str(remote)


    def toCurrent(self, remote):
        smartlink_config = queryUtility(ISmartlinkConfig, name="smartlink_config")
        portal = getSite()
        remote = remote or ''
        portal_url = getToolByName(portal, 'portal_url')()
        if smartlink_config:
            frontendlinks = getattr(smartlink_config, 'frontendlink', [])
            frontend_main_link = getattr(smartlink_config, 'frontend_main_link', '')

            # Unified front-end link
            if frontend_main_link:
                if remote.startswith(frontend_main_link):
                    remote = remote.replace(frontend_main_link, portal_url)
            # Advanced back-end/front-end configuration
            else:
                for frontendlink in frontendlinks:
                    flink = frontendlink[-1]=='/' and frontendlink[:-1] or frontendlink
                    flink = flink.encode('utf-8')
                    if remote.startswith(flink):
                        backendlinks = smartlink_config.backendlink
                        backendlink = backendlinks[frontendlinks.index(frontendlink)]
                        backendlink = backendlink[-1]=='/' and backendlink[:-1] or backendlink
                        if backendlink.startswith(portal_url):
                            remote = remote.replace(flink, backendlink)
                            break
        return str(remote)
