# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.atapi import listTypes
from config import PROJECTNAME
from Products.CMFCore.permissions import AddPortalContent

# Add permissions differ for each type, and are imported by __init__.initialize
# so don't change their names!

AddATReport = 'collective.validator.base: Add ATReport'
AddATFileReport = 'collective.validator.base: Add ATFileReport'

# Set up default roles for permissions

setDefaultRoles(AddATReport,('Manager',))
setDefaultRoles(AddATFileReport,('Manager',))

ADD_CONTENT_PERMISSIONS = {
    'ATReport'   : AddATReport ,
    'ATFileReport': AddATFileReport}

