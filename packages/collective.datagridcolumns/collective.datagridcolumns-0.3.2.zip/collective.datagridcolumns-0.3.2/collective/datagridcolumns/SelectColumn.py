# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope import schema

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.Archetypes import atapi

from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn as BaseSelectColumn

class SelectColumn(BaseSelectColumn):
    """ Defines column with dropdown menu cells in DataGridField """

    security = ClassSecurityInfo()

    def __init__(self, label, vocabulary=None, vocabulary_factory=None, default=None):
        """ Create a SelectColumn

        @param vocabulary Vocabulary method name. This method is called
               from Archetypes instance to get values for dropdown list.
        """
        # do not call base SelectColumn constructor
        Column.__init__(self, label, default=default)
        self.vocabulary = vocabulary
        self.vocabulary_factory = vocabulary_factory


    security.declarePublic('getVocabulary')
    def getVocabulary(self, instance):
        """ Gets this column vocabulary for specific Archetypes instance
        """
        if self.vocabulary_factory:
            try:
                factory = getUtility(schema.interfaces.IVocabularyFactory, name=self.vocabulary_factory)
            except ComponentLookupError:
                raise ComponentLookupError, "Cannot find a vocabulary utility named %s" % self.vocabulary_factory
            factory_context = instance
            return atapi.DisplayList([(t.value, t.title or t.token) for t in factory(factory_context)])
        if self.vocabulary:
            try:
                func = getattr(instance, self.vocabulary)
            except AttributeError:
                raise AttributeError, "Class %s is missing vocabulary function %s" % (str(instance), self.vocabulary)
            return func()
        return atapi.DisplayList([('', '???')])

# Initializes class security
InitializeClass(SelectColumn)
