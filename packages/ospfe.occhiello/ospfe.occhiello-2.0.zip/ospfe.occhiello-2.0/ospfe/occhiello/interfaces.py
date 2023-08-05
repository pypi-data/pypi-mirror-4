# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from ospfe.occhiello import messageFactory as _

DEFAULT_TYPES = ('Document',
                 'Event'
                 'File',
                 'Image',
                 'News Item',
                 'Collection',
                 'Topic',
                 )

class IOcchielloLayer(Interface):
    """Marter interface for the Occhiello browser layer"""


class IOcchielloSettings(Interface):
    """
    Settings used in the control panel for Occhiello
    """
    
    enabled_types = schema.Tuple(
        title=_(u"Content types to apply half-title to"),
        required=False,
        default=DEFAULT_TYPES,
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.ReallyUserFriendlyTypes')
    )
