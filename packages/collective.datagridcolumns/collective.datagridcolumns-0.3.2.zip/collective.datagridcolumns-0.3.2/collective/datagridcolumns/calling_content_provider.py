# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from collective.datagridcolumns.interfaces import ICallingContextProvider

class SimpleCallingContextProvider(object):
    """
    See ICallingContextProvider docstring.
    This is a simple implementation: always call on the site root
    """
    implements(ICallingContextProvider)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    @property
    def url(self):
        return getToolByName(self.context, 'portal_url')()

