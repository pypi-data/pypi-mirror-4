# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID

class UUIDAwarePermalinkAdapter(object):

    def __init__(self, context):
        self.context = context

    def getPermalink(self):
        context = self.context
        portal_url = getToolByName(context, 'portal_url')
        return portal_url() + '/resolveuid/%s' % IUUID(context)

