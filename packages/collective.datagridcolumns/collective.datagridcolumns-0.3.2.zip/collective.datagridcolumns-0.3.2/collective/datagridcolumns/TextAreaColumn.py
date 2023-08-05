# -*- coding: utf-8 -*-

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.DataGridField.Column import Column

class TextAreaColumn(Column):
    """ Textarea column """

    security = ClassSecurityInfo()

    def __init__(self, label, default=None, default_method=None, label_msgid=None,
                       rows=3, cols=0):
        Column.__init__(self, label, default, default_method, label_msgid)
        self.rows = rows
        self.cols = cols
        
    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_textarea_cell"


# Initializes class security
InitializeClass(TextAreaColumn)
