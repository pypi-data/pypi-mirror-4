from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class ReportValidationToolView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.translation_service = getToolByName(self.context,'translation_service')

 
    def getValidityIcon(self,x):
        if x.getObject().is_valid:
            return "valid.gif"
        return "not_valid.gif"
        
    def getResults(self):
        path = "/".join(self.context.getPhysicalPath())
        pc = getToolByName(self.context,'portal_catalog')
        if self.getSubmitted():
            self.delete_items()
        return pc.searchResults(path={"query":path, "depth":1},
                                sort_on="created",
                                sort_order="reverse")

    def getSubmitted(self):
        if self.request.get('submit') ==  self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='table_delete_button', \
                                           default='Delete', \
                                           context=self.context):
            return True
        return False

    def is_selected_all(self):
        if self.request.get('select') == 'all':  
            return True
        return False

    def delete_items(self):
        plone_utils = getToolByName(self, 'plone_utils')
        args = self.request.get('del')
        try:
            self.context.manage_delObjects(args)
        except:
            if self.context.wl_isLocked():
                self.context.wl_clearLocks()
                self.context.manage_delObjects(args)
        plone_utils.addPortalMessage(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='message_deleted_report', \
                                           default='Selected reports deleted', \
                                           context=self.context))
        self.request.RESPONSE.redirect(self.context.absolute_url()+'/folder_report')
