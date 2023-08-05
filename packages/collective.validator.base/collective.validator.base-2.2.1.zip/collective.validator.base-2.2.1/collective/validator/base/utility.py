from zope.interface import implements,alsoProvides
from zope.component import adapts
from zope.component.globalregistry import getGlobalSiteManager as getSiteManager

from collective.validator.base.interfaces import IVTPlone

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName 

import string

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *

class DynamicImport(object):
    
    implements(IDynamicImport)
    
    def __init__(self, context):
        self.context = context

    def dynamic_import(self):
        registrations = getSiteManager().registeredAdapters()
        str=[]
        for reg in registrations:
            if reg.required[0].__name__ == 'IVTPlone':
                str.append('from %s import %s' %(reg.provided.__module__,reg.provided.__name__))
        return str

    def dynamic_vocabulary(self):
        registrations = getSiteManager().registeredAdapters()
        str=[]
        for reg in registrations:
            if reg.required[0].__name__ == 'IVTPlone':
                if reg.provided.__name__ != 'Interface':
                    str.append(reg.provided.__name__)
        return str

    def dynamic_integrated_vocab(self):
        registrations = getSiteManager().registeredAdapters()
        str=[]
        for reg in registrations:
            if reg.required[0].__name__ == 'IVTPlone':
                if reg.provided.__name__ != 'Interface' and reg.provided.__name__ != 'ICss':
                    str.append(reg.provided.__name__)
        return str

