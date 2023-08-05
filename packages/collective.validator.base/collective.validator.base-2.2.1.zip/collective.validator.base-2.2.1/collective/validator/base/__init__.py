from Products.Archetypes.public import listTypes
from Products.Archetypes import process_types
from Products.CMFCore.permissions import AddPortalContent

from config import GLOBALS, PROJECTNAME
from permissions import ADD_CONTENT_PERMISSIONS


from Products.CMFCore.utils import ToolInit,ContentInit

from Products.CMFCore.DirectoryView import registerDirectory

from config import *
from collective.validator.base.content import ValidationTool

registerDirectory('skins', globals())

DEFAULT_ADD_CONTENT_PERMISSION = AddPortalContent

def initialize(context):
    ToolInit( 'Validation Tool',
                tools=(ValidationTool.ValidationTool, ),
                icon='skins/validationtool_images/validation.gif',
                ).initialize(context)


    import content

    # How exactly does 'listTypes' work: See those registerType() calls in your content type modules? 
    # Notice how we also import those modules (but do nothing with the import) in the 'content' 
    # package's __init__.py. The registerType() call tells AT about the type so that listTypes() can
    # find it later.
    contentTypes, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)
    
    ContentInit(
        PROJECTNAME + ' Content',
    content_types = contentTypes,
    permission = DEFAULT_ADD_CONTENT_PERMISSION,
    extra_constructors = constructors,
    fti = ftis,
    ).initialize(context)

    
    for i in range(0, len(contentTypes)):
        klassname = contentTypes[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue
        context.registerClass(meta_type = ftis[i]['meta_type'],
                              constructors = (constructors[i],),
                                  permission   = ADD_CONTENT_PERMISSIONS[klassname])