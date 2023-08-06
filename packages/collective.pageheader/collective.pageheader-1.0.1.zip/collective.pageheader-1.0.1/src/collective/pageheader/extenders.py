# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender

from Products.Archetypes import atapi
from plone.app.blob.field import ImageField

from collective.pageheader.interfaces import IPageHeaderEnabled
from collective.pageheader.interfaces import ILayer
from collective.pageheader import _

PAGEHEADER_FIELDNAME = 'pageheader_image'


class PageHeaderImageField(ExtensionField, ImageField):
    """ image field """


class BaseExtender(object):

    fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class Extender(BaseExtender):
    adapts(IPageHeaderEnabled)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = ILayer

    fields = [
        PageHeaderImageField(
            PAGEHEADER_FIELDNAME,
            widget=atapi.ImageWidget(
                label=_(u"Page Header Image"),
                description=_(u"An image to be used as the header of the page. "
                              u"If none provided the one from the parent will be used if present.")
            ),
            validators=('isNonEmptyFile'),
            sizes={
                'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
            },
        ),
    ]
