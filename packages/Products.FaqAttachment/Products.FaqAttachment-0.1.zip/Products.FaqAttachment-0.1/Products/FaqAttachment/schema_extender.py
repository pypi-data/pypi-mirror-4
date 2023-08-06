# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField
try:
    from plone.app.blob.field import BlobField as BaseFileField
except ImportError:
    # no blob support (Plone 3 with no blob)
    from Products.Archetypes.Field import FileField as BaseFileField

from Products.Archetypes import atapi

from Products.FaqAttachment import messageFactory as _
from Products.FaqAttachment.interfaces import IFaqAttachmentLayer

class ExtensionFileField(ExtensionField, BaseFileField):
    """ derivative of blobfield for extending schemas """


class FaqAttachmentExtender(object):
    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IFaqAttachmentLayer

    fields = [
        ExtensionFileField('file',
            widget=atapi.FileWidget(
                label=_(u'Attachment'),
                description=_(u'file_help',
                              default=u"Provide an attachment for help people understanding the Faq"),
            ),
            required=False,
            primary=False,
            validators=('isNonEmptyFile'),
        ),

    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
