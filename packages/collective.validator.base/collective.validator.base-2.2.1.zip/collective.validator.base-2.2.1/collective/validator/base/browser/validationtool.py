from zope.interface import Interface, implements
from zope.component import adapts, getMultiAdapter
from zope.event import notify
from zope.formlib import form

from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.form.validators import null_validator
from plone.fieldsets.fieldsets import FormFieldsets
from plone.protect import CheckAuthenticator

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty, SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from collective.validator.base.interfaces.interfaces import *

class IValidationToolControlPanelAdapter(SchemaAdapterBase):
    
    implements(IWebValidator)
    adapts(IPloneSiteRoot)
   
    def __init__(self, context):
        super(IValidationToolControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_validationtool')
        
#area config
    
    def get_integratedValidator(self):
        return self.context.getIntegratedValidator()

    def set_integratedValidator(self, value):
        self.context.setIntegratedValidator(value)
    
    def get_validationActionEnabled(self):
        return self.context.getValidationActionEnabled()
    
    def set_validationActionEnabled(self, value):
        pa = getToolByName(self.context, 'portal_actions')
        for action in pa.listActions():
            if action.getId() == 'validationtool':
                if (value):
                    action.visible=1
                else:
                    action.visible=0
        return self.context.setValidationActionEnabled(value)
    
    def get_validatorUrl(self):
        return self.context.getValidatorUrl()

    def set_validatorUrl(self, value):
        self.context.setValidatorUrl(value)
    
    def get_validatorSleep(self):
        return self.context.getValidatorSleep()

    def set_validatorSleep(self, value):
        self.context.setValidatorSleep(value)
    
    integratedValidator = property(get_integratedValidator, set_integratedValidator)
    validationActionEnabled =  property(get_validationActionEnabled, set_validationActionEnabled)
    validatorUrl = property(get_validatorUrl, set_validatorUrl)
    validatorSleep = property(get_validatorSleep, set_validatorSleep)
    
#area validation

    def get_validatorType(self):
        return self.context.getValidatorType()

    def set_validatorType(self, value):
        self.context.setValidatorType(value)
    
    def get_portalTypesList(self):
        return self.context.getPortalTypesList()

    def set_portalTypesList(self, value):
        self.context.setPortalTypesList(value)
    
    def get_reviewStatesList(self):
        return self.context.getReviewStatesList()

    def set_reviewStatesList(self, value):
        self.context.setReviewStatesList(value)
    
    def get_anonymousValidation(self):
        return self.context.getAnonymousValidation()

    def set_anonymousValidation(self, value):
        self.context.setAnonymousValidation(value)
        
    def get_itemsMaxAge(self):
        return self.context.getItemsMaxAge()

    def set_itemsMaxAge(self, value):
        self.context.setItemsMaxAge(value)
    
    def get_emailAddresses(self):
        return self.context.getEmailAddresses()

    def set_emailAddresses(self, value):
        self.context.setEmailAddresses(value)
    
    validatorType = property(get_validatorType, set_validatorType)
    portalTypesList = property(get_portalTypesList, set_portalTypesList)
    reviewStatesList = property(get_reviewStatesList, set_reviewStatesList)
    anonymousValidation = property(get_anonymousValidation, set_anonymousValidation)
    itemsMaxAge = property(get_itemsMaxAge, set_itemsMaxAge)
    emailAddresses = property(get_emailAddresses, set_emailAddresses)
    
    sendReport = ProxyFieldProperty(IValidationToolValidationSchema['sendReport'])
    createReport = ProxyFieldProperty(IValidationToolValidationSchema['createReport'])
    createReportText = ProxyFieldProperty(IValidationToolValidationSchema['createReportText'])
    
#area debug
    def get_debugTypesList(self):
        return self.context.getDebugTypesList()

    def set_debugTypesList(self, value):
        self.context.setDebugTypesList(value)
    
    def get_emailAddressesDebug(self):
        return self.context.getEmailAddressesDebug()

    def set_emailAddressesDebug(self, value):
        self.context.setEmailAddressesDebug(value)
        
    debugTypesList = property(get_debugTypesList, set_debugTypesList)
    emailAddressesDebug = property(get_emailAddressesDebug, set_emailAddressesDebug)
    
    sendReportDebug = ProxyFieldProperty(IValidationToolDebugSchema['sendReportDebug'])
    createReportDebug = ProxyFieldProperty(IValidationToolDebugSchema['createReportDebug'])
    createReportTextDebug = ProxyFieldProperty(IValidationToolDebugSchema['createReportTextDebug'])
    
#area proxy
    def get_proxyAddress(self):
        return self.context.getProxyAddress()

    def set_proxyAddress(self, value):
        self.context.setProxyAddress(value)
    
    def get_proxyPort(self):
        return self.context.getProxyPort()

    def set_proxyPort(self, value):
        self.context.setProxyPort(value)
        
    def get_proxyUserid(self):
        return self.context.getProxyUserid()

    def set_proxyUserid(self, value):
        self.context.setProxyUserid(value)
    
    def get_proxyPassword(self):
        return self.context.getProxyPassword()

    def set_proxyPassword(self, value):
        self.context.setProxyPassword(value)
        
    proxyAddress = property(get_proxyAddress, set_proxyAddress)
    proxyPort = property(get_proxyPort, set_proxyPort)
    proxyUserid = property(get_proxyUserid, set_proxyUserid)
    proxyPassword = property(get_proxyPassword, set_proxyPassword)

config = FormFieldsets(IValidationToolConfigSchema)
config.id = 'config'
config.label = _(u'Config')

validation = FormFieldsets(IValidationToolValidationSchema)
validation.id = 'validation'
validation.label = _(u'Validation')

debug = FormFieldsets(IValidationToolDebugSchema)
debug.id = 'debug'
debug.label = _(u'Debug')

proxy = FormFieldsets(IValidationToolProxySchema)
proxy.id = 'proxy'
proxy.label = _(u'Proxy')

class ValidationToolControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(config, validation, debug, proxy)

    label = _('ValidationTool Settings')
    description = _('')
    form_name = _('ValidationTool Settings')
    
    def saveFields(self,action,data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _("No changes made.")
        portal_val = getToolByName(self.context, 'portal_validationtool')
        str = portal_val.getIntegratedType()
        pa = getToolByName(self.context, 'portal_actions')
        str1 = _('Validate')
        pa.document_actions.validationtool.title = str1 + ' ' + str
        return portal_val

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        self.saveFields(action,data)
        
    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/@@validationtool-controlpanel')
        return ''
    
    @form.action(_(u'save_and_valid',default=u'Save and Run Validate'), name=u'save_validate')
    def run_validation(self, action, data):
        portal_val = self.saveFields(action,data)
        portal_val.runVal()
        return 

    @form.action(_(u'save_and_debug',default=u'Save and Run Debug'), name=u'save_debug')
    def run_debug(self, action, data):
        portal_val = self.saveFields(action,data)
        if  portal_val.runDebug() == 0:
            self.status = _("Debug is not a Css function")
        return

    @form.action(_(u'go_report',default=u'Go to Report Page'), name=u'go_report')
    def go_report(self, action, data):
        CheckAuthenticator(self.request)
        self.request.response.redirect(self.context.portal_url()+"/portal_validationtool/folder_report")
        return

    def _on_save(self, data=None):
        pass