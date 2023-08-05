from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class ValidationToolView(BrowserView):

    def runVal(self):
        pt = getToolByName(self.context,'portal_validationtool')
        pt.runVal()

