# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.blob.field import ImageField as BlobImageField

from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from redturtle.smartlink.interfaces import ISmartLink
from redturtle.smartlink.content.link import LinkSchema

class ExtensionBlobField(ExtensionField, BlobImageField):
    """ derivative of blobfield for extending schemas """


class SmartLinkExtender(object):
    adapts(ISmartLink)
    implements(ISchemaExtender)

    fields = [

        ExtensionBlobField('image',
            required = False,
            languageIndependent = True,
            max_size = zconf.ATNewsItem.max_image_dimension,
            schemata="Advanced",
            sizes= None,
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkNewsImageMaxSize', V_REQUIRED)),
            widget=atapi.ImageWidget(
                label=LinkSchema['image'].widget.label,
                description=LinkSchema['image'].widget.description,
                i18n_domain=LinkSchema['favicon'].widget.i18n_domain,
                show_content_type = LinkSchema['favicon'].widget.show_content_type,
            ),
        ),
              
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
