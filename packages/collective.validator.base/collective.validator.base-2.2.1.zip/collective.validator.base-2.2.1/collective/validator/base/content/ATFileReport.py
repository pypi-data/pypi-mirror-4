from zope.interface import implements
from zope.component import getUtility
from Products.Archetypes.atapi import *

from collective.validator.base.config import PROJECTNAME
from collective.validator.base.interfaces.interfaces import IATFileReport

from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import BaseSchema, Schema
from Products.Archetypes.atapi import BaseContent
from Products.ATContentTypes.content.file import ATFile,ATFileSchema

schema = Schema((
    BooleanField(
        name='is_valid',
        default=True,
    ),

))

at_file_report_schema = ATFileSchema.copy() + schema.copy()
at_file_report_schema['is_valid'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}

class ATFileReport(ATFile):
    implements(IATFileReport)
    
    schema = at_file_report_schema 
    _at_rename_after_creation = True

registerATCT(ATFileReport, PROJECTNAME)



