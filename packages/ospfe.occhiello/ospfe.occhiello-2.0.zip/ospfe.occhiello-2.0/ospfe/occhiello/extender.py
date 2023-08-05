# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import adapts
from zope.component import queryUtility

from plone.memoize.instance import memoize

from plone.registry.interfaces import IRegistry

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IBaseObject

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from ospfe.occhiello import messageFactory as _
from ospfe.occhiello.interfaces import IOcchielloLayer
from ospfe.occhiello.interfaces import IOcchielloSettings

class ExtensionStringField(ExtensionField, atapi.StringField):
    """ derivative of string for extending schemas """


class OcchielloExtender(object):
    adapts(IBaseObject)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IOcchielloLayer

    fields = [
        ExtensionStringField('occhiello',
            widget=atapi.StringWidget(
                label=_(u"Half title"),
                description=u"",
            ),
            required=False,
            searchable=True,
        ),
    ]

    def __init__(self, context):
        self.context = context

    @property
    @memoize
    def enabled_types(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IOcchielloSettings, check=False)
        return settings.enabled_types

    def getFields(self):
        if self.context.portal_type in self.enabled_types:
            return self.fields
        return []

    def getOrder(self, schematas):
        """Occhiello must be in the first schemata, before title
        """
        if self.context.portal_type in self.enabled_types:
            default = schematas["default"]
            default.remove('occhiello')
            default.insert(default.index('title'), 'occhiello')
        return schematas
