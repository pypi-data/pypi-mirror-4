from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from collective.validator.base.interfaces.interfaces import IBaseValidationType

class BaseContentValidable(object):
    """Adapter allowing a content type to return HTML to validate
    """
    implements(IBaseValidationType)
    
    def __init__(self, context):
        self.context = context


    def getAvailableViews(self):
        """Obtain all available view of the object adapted, revolsing alias"""
        #actions = [x['id'] for x in self.context.__class__.actions if x.get('visible',True)]
        portal_types = getToolByName(self.context, 'portal_types')
        portal_actions = getToolByName(self.context, 'portal_actions')
        site_properties = getToolByName(self.context, 'portal_properties').site_properties

        actions = portal_actions.listFilteredActionsFor(self.context)
        actionlist=[]
        if self.context.getTypeInfo().getId() in site_properties.use_folder_tabs:
            actionlist=actions['folder']+actions['object']+actions.get('object_tabs',[])
        else:
            actionlist=actions['object']+actions.get('object_tabs',[])
        
        typeinfo = portal_types.getTypeInfo(self.context)
        views = []
        for a in [x['id'] for x in actionlist]:
            views.append(typeinfo.queryMethodID(a))
        return views
        

    def getSources(self):
        """For basic type I only need to obtain the source of one object for every tab available
        So I obtain a list like this:
        [ (idaction, htmlstring), ... ]
        """      
        actions = self.getAvailableViews()
        html_list = []
        for action in actions:
            if action=='(selected layout)':
                action = "view"
            try:
                html_list.append(
                     (action, str(eval("self.context.%s()" % action).encode('utf-8'),) )
                 )
            except AttributeError:
                pass
            except SyntaxError, mgm:
                self.context.plone_log("Can't debug view %s\n%s" % (action, msg) )
        return html_list

    def isValid(self):
        """Return the tuple (success, validation_report_list)
        """        
        # for the basic type the adapter runs:
        success = True
        sources = self.getSources()
        validation_report_list = []
        for s in sources:
            is_tool = getToolByName(self.context, 'portal_validationtool')
            report = is_tool.validateReportPage(s[1])
            r = report['m:validity']

            success = success and r
            validation_report_list.append( (s[0],report,) )

        return (success, validation_report_list)
