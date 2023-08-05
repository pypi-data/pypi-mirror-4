# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName

from Products.DataGridField.Column import Column

from collective.datagridcolumns.interfaces import ICallingContextProvider


class ReferenceColumn(Column):
    """ Defines column with that will contains an UID, that reference another content """

    security = ClassSecurityInfo()

    def __init__(self, label, default=None, default_method=None,
                label_msgid=None, required=False, object_provides=[],
                surf_site=True, search_site=True):
        if required:
            # sorry for this trick, but we are using this product with a custom DataGridField 1.6.4
            # see https://github.com/RedTurtle/Products.DataGridField/tree/1.6
            Column.__init__(self, label, default=default, default_method=default_method,
                            label_msgid=label_msgid, required=required)
        else:
            Column.__init__(self, label, default=default, default_method=default_method,
                            label_msgid=label_msgid)
        self.object_provides = object_provides
        self.surf_site = surf_site
        self.search_site = search_site

    security.declarePublic('getAJAXCallingContext')

    def getAJAXCallingContext(self, context):
        return getMultiAdapter((context, context.REQUEST), ICallingContextProvider).url

    security.declarePublic('getMacro')

    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_reference_cell"

    security.declarePublic('getTarget')

    def getTarget(self, context, cell_value):
        """ Return the object that the saved UID refers to """
        if cell_value:
            reference_catalog = getToolByName(context, 'reference_catalog')
            return reference_catalog.lookupObject(cell_value)

    security.declarePublic('getAllowedInterfaces')

    def getAllowedInterfaces(self):
        """ Return the a proper comma separated strings of object_provides values """
        return ','.join(self.object_provides)

    security.declarePublic('surfSite')

    def surfSite(self):
        return self.surf_site

    security.declarePublic('searchSite')

    def searchSite(self):
        return self.search_site


InitializeClass(ReferenceColumn)
