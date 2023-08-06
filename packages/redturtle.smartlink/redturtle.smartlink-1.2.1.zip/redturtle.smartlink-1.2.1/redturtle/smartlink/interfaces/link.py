# -*- coding: utf-8 -*-

from zope.interface import Interface
from Products.ATContentTypes.interface import IATLink

class ISmartLink(IATLink):
    """A link to an internal or external resource."""

class ISmartLinked(Interface):
    """Marker interface for content that are referenced (smart-linked) by Smart Link content"""
