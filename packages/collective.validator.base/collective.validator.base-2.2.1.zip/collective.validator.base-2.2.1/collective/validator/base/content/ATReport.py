from zope.interface import implements
from zope.component import getUtility
from Products.Archetypes.atapi import *

from collective.validator.base.config import PROJECTNAME
from collective.validator.base.interfaces.interfaces import IATReport

from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import BaseSchema, Schema
from Products.Archetypes.atapi import BaseContent
from Products.ATContentTypes.content.document import ATDocument,ATDocumentSchema

schema = Schema((
    BooleanField(
        name='is_valid',
        default=True,
    ),

))

atreport_schema = ATDocumentSchema.copy() + schema.copy()
atreport_schema['presentation'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}
atreport_schema['tableContents'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}
atreport_schema['is_valid'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}

class ATReport(ATDocument):
    implements(IATReport)
    
    schema = atreport_schema 
    _at_rename_after_creation = True

registerATCT(ATReport, PROJECTNAME)



