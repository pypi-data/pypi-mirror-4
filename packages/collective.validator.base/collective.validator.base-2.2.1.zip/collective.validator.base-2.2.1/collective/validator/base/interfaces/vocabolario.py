from Products.CMFCore.utils import UniqueObject, getToolByName 
from zope.schema.vocabulary import SimpleVocabulary
from Products.Archetypes.atapi import DisplayList

import string

from collective.validator.base.utility import DynamicImport

def Portal(self):
        portal = getToolByName(self.context,'portal_types')
        ptypes = portal.listTypeTitles() 
        del ptypes['ValidationTool']
        ks = ptypes.keys()
        ks.sort()
        return SimpleVocabulary.fromValues(ks)

def Validators(self):
    dynamic_vocab=DynamicImport(self)
    str = dynamic_vocab.dynamic_vocabulary()
    str.sort()
    return SimpleVocabulary.fromItems([(el.lstrip('I'),el) for el in str])

def Integrated_val(self):
    dynamic_vocab=DynamicImport(self)
    str = dynamic_vocab.dynamic_integrated_vocab()
    str.sort()
    return SimpleVocabulary.fromItems([(el.lstrip('I'),el) for el in str])
