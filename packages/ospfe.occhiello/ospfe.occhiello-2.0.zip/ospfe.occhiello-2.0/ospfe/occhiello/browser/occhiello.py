# -*- coding: utf-8 -*-

from plone.memoize.instance import memoize
from plone.app.layout.viewlets import common

class OcchielloViewlet(common.ViewletBase):
    """Display the occhiello viewlet"""
    
    @memoize
    def _occhiello(self):
        return self.context.getField('occhiello')
    
    @property
    def occhiello(self):
        return self._occhiello().get(self.context)
    
    def available(self):
        return self._occhiello() and self._occhiello().get(self.context)
