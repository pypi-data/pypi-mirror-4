# -*- coding: utf-8 -*-

from Products.Five import BrowserView


class RemoteValidation(BrowserView):
    """vista per fare la validaizone del sito"""

    def remoteValidation(self):
        """
        @author: andrea cecchi
        Metodo che richiamato esegue la validazione del sito
        """
        self.context.plone_log('Inizio validazione')
        p_ist= self.context.portal_validationtool
        p_ist.runVal()
        self.context.plone_log('Validazione eseguita')
        return 'OK'
        
