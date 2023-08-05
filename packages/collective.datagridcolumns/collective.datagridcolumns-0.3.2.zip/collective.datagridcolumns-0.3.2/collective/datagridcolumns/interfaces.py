# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class ICallingContextProvider(Interface):
    """An object able to provide and URL for make a query call on the server"""

    url = Attribute("A proper site URL, where make an AJAX call")
