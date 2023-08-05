# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from zope.i18nmessageid import MessageFactory

from tlspu.cookiepolicy.interfaces import ICookiePolicy

_ = MessageFactory('tlspu.cookiepolicy')


class CookiePolicy(BrowserView):
    """
    """
    implements(ICookiePolicy)

    def __init__(self, context, request, *args, **kwargs):
        super(CookiePolicy, self).__init__(context, request, *args, **kwargs)
        context = aq_inner(context)
        self.context = context
        pp = getToolByName(context, 'portal_properties')
        self.sheet = getattr(pp, 'tlspu_cookiepolicy_properties', None)
