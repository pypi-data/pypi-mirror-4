# -*- coding: utf-8 -*-

from zope.interface import Interface

class IPermalinkProvider(Interface):
    """Interface for object that can provide Permalink data"""
    
    def getPermalink():
        """Obtain permalink"""
