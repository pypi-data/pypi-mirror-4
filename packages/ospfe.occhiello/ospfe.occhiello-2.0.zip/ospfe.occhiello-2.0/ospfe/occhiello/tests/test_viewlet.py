# -*- coding: utf-8 -*-

import unittest

from zope import interface
from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from ospfe.occhiello.interfaces import IOcchielloLayer
from ospfe.occhiello.testing import OCCHIELLO_INTEGRATION_TESTING

from ospfe.occhiello.interfaces import IOcchielloSettings

class TestQueryView(unittest.TestCase):

    layer = OCCHIELLO_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        request = self.layer['request']
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        interface.alsoProvides(request, IOcchielloLayer)
        request.set('ACTUAL_URL', 'http://nohost/plone/page')
        portal.invokeFactory(type_name='Document', id='page', title='A page')
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(IOcchielloSettings, check=False)
    
    def test_field_present(self):
        portal = self.layer['portal']
        fields = [field.getName() for field in portal.page.Schema().fields()]
        self.assertTrue('occhiello' in fields)

    def test_field_on_edit(self):
        portal = self.layer['portal']
        self.assertTrue('<input type="text" name="occhiello"' in portal.page.base_edit())

    def test_viewlet_display(self):
        portal = self.layer['portal']
        self.assertFalse('<p class="occhiello">' \
                    in portal.page())
        portal.page.edit(occhiello='The lazy dog...')
        self.assertTrue('<p class="occhiello">The lazy dog...</p>' \
                    in portal.page())
        self.settings.enabled_types = tuple()
        self.assertFalse('<p class="occhiello">' \
                    in portal.page())

