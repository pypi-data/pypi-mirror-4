# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from zope.publisher.browser import TestRequest
from zope.component import adapts,getMultiAdapter
from Products.Archetypes.utils import shasattr

class ValidateXhtmlView(BrowserView):
    """Metodo che restituisce la vista di un oggetto"""

    def getRightView(self):
        """
        @author: andrea cecchi
        Metodo che restituisce la vista di un oggetto 
        """
        context=self.context
        if shasattr(context,'view'):
            xhtml = context.view().encode('utf-8')
        else:
            try:
                request = TestRequest()
                xhtml=getMultiAdapter((context,request),'view').encode('utf-8')
            except:
                try:
                    xhtml = context.encode('utf-8')
                except:
                    xhtml=context.unrestrictedTraverse('base_view')().encode('utf-8')
        return xhtml

        
