# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from plone.memoize.view import memoize
from collective.permalink.interfaces import IPermalinkProvider

class PermalinkUrlView(BrowserView):
    """View for showing permalink on Plone contents"""

    def __call__(self):
        context = self.context
        return self.permalink

    @property
    @memoize
    def permalink(self):
        """Get the permalink info from the context"""
        try:
            return IPermalinkProvider(self.context).getPermalink()
        except TypeError:
            return None

