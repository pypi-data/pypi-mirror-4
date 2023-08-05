from zope.component import adapts

from AccessControl import ClassSecurityInfo

from xml.dom import minidom
from DateTime import DateTime

from collective.validator.base.config import *
from collective.validator.base.interfaces.interfaces import *
from collective.validator.base.content import sendattachment
from collective.validator.base.content.ValidationTool import ValidationTool

import tempfile

class Parser(object):

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context
        self.translation_service = getToolByName(self.context,'translation_service')

    security.declarePrivate('val_type')
    def getValidatorType(self):
        return self.val_type
   
    security.declarePrivate('val_url')
    def getValidatorUrl(self):
        return self.val_url
  
    security.declarePrivate('createResult')
    def createResult(self,resp,error=False):
        """create a structure for the result report"""
        
        if error:
            return {'valiator_error':resp}
        
        results = {'m:errors':{'m:errorcount':0,
                               'm:errorlist':[],
                              },
                   'm:warnings':{'m:warningcount':0,
                                 'm:warninglist':[],
                                },
                   'm:validity':None,
                  }
        try:
            xmldoc = minidom.parseString(resp)
        except:
            return 'wrong file!'
        errors = xmldoc.getElementsByTagName('m:error')
        err_results = []
        for err in errors:
            diz = {}
            diz['m:line'] = err.getElementsByTagName('m:line')[0].childNodes[0].nodeValue
            diz['m:message'] = err.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
            diz['m:col'] = err.getElementsByTagName('m:col')[0].childNodes[0].nodeValue
            err_results.append(diz)
        errs = results['m:errors']
        errs['m:errorcount'] = len(err_results)
        errs['m:errorlist'] = err_results
        results['m:errors'] = errs

        warnings = xmldoc.getElementsByTagName('m:warning')
        warn_results = []
        for warn in warnings:
            diz = {}
            if warn.getElementsByTagName('m:message')[0].childNodes[0].nodeValue != 'DOCTYPE Override in effect!':
                try:
                    diz['m:line'] = warn.getElementsByTagName('m:line')[0].childNodes[0].nodeValue
                    diz['m:col'] = warn.getElementsByTagName('m:col')[0].childNodes[0].nodeValue
                except IndexError:
                    diz['m:line'] = 0
                    diz['m:col'] = 0
                diz['m:message'] = warn.getElementsByTagName('m:message')[0].childNodes[0].nodeValue
                warn_results.append(diz)   
        warns = results['m:warnings']
        warns['m:warningcount'] = len(warn_results)
        warns['m:warninglist'] = warn_results
        results['m:warnings'] = warns
        results['m:validity'] = xmldoc.getElementsByTagName('m:validity')[0].childNodes[0].nodeValue == 'true'
        return results

    security.declarePrivate('search')
    def search(self):
        """search the pages to be validated"""
        catalog = getToolByName(self.context,'portal_catalog')
        searchQuery = {}
        searchQuery['portal_type']=list(self.context.getPortalTypesList())
        if self.context.getReviewStatesList():
            searchQuery['review_state']=list(self.context.getReviewStatesList())
        if self.context.getItemsMaxAge():
            searchQuery['modified'] = {'query':DateTime()-self.context.getItemsMaxAge(), 'range':'min'}
        return catalog(**searchQuery)


    security.declarePrivate('dumpErrors')
    def dumpErrors(self, elist):
        """Render html for validation error structure"""
        stout = "<dl>"
        st = "<dt>%s/%s</dt><br><dd>"
        st += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='row', \
                                           default="row:", \
                                           context=self.context))
        st +=" %s, "
        st += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='column', \
                                           default="column:", \
                                           context=self.context))
        st +=" %s</dd><dd><em>%s</em></dd>"
        cnt = 0
        elen = len(elist)
        if not elen: return ""
        try:
            for x in elist:
                cnt+=1
                stout+= st % (cnt, elen, x['m:line'], x['m:col'], x['m:message'])
            return stout+"</dl>"
        except:
            return "wrong list"

    security.declarePrivate('createReportPage')
    def createReportPage(self, validation, title, url):
        """Create the HTML output report for a given HTML source"""
        report = ""
        report+="""<h2>%s</h2><pre><a href="%s">%s</a></pre><p style="margin-top:0px;">""" % (title, url, url)
        parerr = parwarn = 0
        if validation.get('valiator_error',''):
            report+="Problems on validating this page: %s" %validation['valiator_error']
            report+="</p><br>"
            return (report, parerr, parwarn,False)
        
        if validation['m:validity']:
            report+= str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='success_valid', \
                                           default="Page validation succesfull<br>", \
                                           context=self.context))
        else:
            report+= str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='unsuccess_valid', \
                                           default="Page validation failed<br>", \
                                           context=self.context))
            if validation.get('m:errors',None):
                parerr = parerr + validation['m:errors']['m:errorcount']
                report += self.createReportErr(validation['m:errors']['m:errorcount'])
                report+=str(self.dumpErrors(validation['m:errors']['m:errorlist']).encode('utf8'))

            if validation.get('m:warnings',None):
                parwarn = parwarn + validation['m:warnings']['m:warningcount']
                report += self.createReportWarn(validation['m:warnings']['m:warningcount'])
                report+=str(self.dumpErrors(validation['m:warnings']['m:warninglist']).encode('utf8'))
        report+="</p><br>"
        
        return (report, parerr, parwarn,validation['m:validity'])

    security.declarePrivate('createReportDocument')
    def createReportDocument(self,fileout,toterr,totwarn,tot_files,valid):
        now = DateTime().strftime("%d/%m/%Y")
        container = self.context
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        pt = getToolByName(self.context, 'portal_types')
        
        if self.context.getCreateReport():
            # Save report in the tool as ATReport
            newId = self.context.generateUniqueId('report')
            title="Report %s: %s" % (self.val_type,now)
            type_name = "ATReport"
            info = pt.getTypeInfo( type_name )
            ob = info._constructInstance(container, newId)
            ob.setTitle(title)
            ob.setDescription(self.createDescription(toterr,totwarn,tot_files))
            ob.setText(fileout)
            ob.setIs_valid(valid)
#            info._finishConstruction(ob)
            logger.validator_info('Report page created')
            
        elif self.context.getCreateReportText():
            #create a text report
            newId = self.context.generateUniqueId('report-text')
            type_name = "ATFileReport"
            title="Report Text %s: %s" % (self.val_type,now)
            info = pt.getTypeInfo( type_name )
            ob = info._constructInstance(container, newId)
            file_title = 'report_text_'+DateTime().strftime("%d-%m-%Y")
            ob.setTitle(title)
            ob.setDescription(self.createDescription(toterr,totwarn,tot_files))
            ob.setFile(portal_transforms.convert('html_to_web_intelligent_plain_text',fileout).getData())
            ob.setFilename(file_title+'.txt')
            ob.setContentType('text/plain')
            ob.setIs_valid(valid)
            logger.validator_info('Report document created')
        
        return newId

    security.declarePrivate('createDebugReportDocument')
    def createDebugReportDocument(self,fileout,toterr,totwarn,tot_files,valid):
        # Save report in the tool as ATReport
        now = DateTime().strftime("%d/%m/%Y")
        container = self.context
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        pt = getToolByName(self.context, 'portal_types')
        if self.context.getCreateReport():
            # Save report in the tool as ATReport
            
            newId = self.context.generateUniqueId('report')
            title="Report Debug %s: %s" % (self.val_type,now)
            type_name = "ATReport"
            info = pt.getTypeInfo( type_name )
            ob = info._constructInstance(container, newId)
            ob.setTitle(title)
            ob.setDescription(self.createDescription(toterr,totwarn,tot_files))
            ob.setText(fileout)
            ob.setIs_valid(valid)
            info._finishConstruction(ob)
            
        elif self.context.getCreateReportText():
            #create a text report
            newId = self.context.generateUniqueId('report-text')
            type_name = "ATFileReport"
            title="Report Debug Text %s: %s" % (self.val_type,now)
            info = pt.getTypeInfo( type_name )
            ob = info._constructInstance(container, newId)
            file_title = 'report_debug_text_'+DateTime().strftime("%d-%m-%Y")
            ob.setTitle(title)
            ob.setDescription(self.createDescription(toterr,totwarn,tot_files))
            ob.setFile(portal_transforms.convert('html_to_web_intelligent_plain_text',fileout).getData())
            ob.setFilename(file_title+'.txt')
            ob.setContentType('text/plain')
            ob.setIs_valid(valid)
            info._finishConstruction(ob)
            
        return newId

    security.declarePrivate('createDescription')
    def createDescription(self,toterr,totwarn,tot_files):
        desc = ""
        desc +="%s " %toterr
        desc += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_errors', \
                                           default="errors", \
                                           context=self.context))

        desc += ", %s " %totwarn
        desc += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_warnings', \
                                           default="warnings", \
                                           context=self.context))
        desc +=" in %s file(s)" %tot_files
        return desc

    security.declarePrivate('createReportErr')
    def createReportErr(self,errorcount):
        report = ""
        report +=str(self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='found', \
                                   default="<h3>Found", \
                                   context=self.context))
        report +=" %s " %errorcount
        report += str(self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='tot_errors', \
                                   default="errors", \
                                   context=self.context))
        report += "</h3>"
        return report

    security.declarePrivate('createReportWarn')
    def createReportWarn(self,warncount):
        report = ""
        report +=str(self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='found', \
                                   default="<h3>Found", \
                                   context=self.context))
        report +=" %s " %warncount
        report += str(self.translation_service.utranslate( \
                                   domain='collective.validator.base', \
                                   msgid='tot_warnings', \
                                   default="warnings", \
                                   context=self.context))
        report += "</h3>"
        return report

    security.declarePrivate('createReportMail')
    def createReportMail(self,fileout,toterr, totwarn, tot_files):
        """create the attachment for the mail"""
        stringa = ""
        stringa += "<html><head><title>Portal validation</title></head>"
        stringa += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='valid_res_for', \
                                           default="<body><h3>Validation Results for", \
                                           context=self.context))
        stringa +=" %s</h3>" %self.val_type
        stringa += "<h3>%s " %toterr
        stringa += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_errors', \
                                           default="errors", \
                                           context=self.context))
        stringa +=", %s " %totwarn
        stringa += str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='tot_warnings', \
                                           default="warnings", \
                                           context=self.context))
        stringa += " in %s file(s)</h3>" % tot_files
        stringa += fileout
        stringa += "<br></body></html>"
        return stringa

    security.declarePrivate('sendReportAsAttach')
    def sendReportAsAttach(self,str_report,filenamepars, send_from=None, send_to=[], subject="", text="", files=[]):
        """Send the content of a file as attachment to adresses list"""
        plone_utils = self.context.plone_utils
        
        tempf = tempfile.NamedTemporaryFile()
        tempf.write(str_report)
        tempf.flush()

        send_from = send_from or self.context.getPortalEmailFromAddress()
        if type(send_from)==tuple and send_from:
            send_from = send_from[0]
        send_to = send_to or list(self.context.getEmailAddresses())
        subject = subject or str(self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='valid_results_title', \
                                           default="Validation Results", \
                                           context=self.context))
        text1 = (self.translation_service.utranslate( \
                                           domain='collective.validator.base', \
                                           msgid='generated_report', \
                                           default="Generated validation report for ", \
                                           context=self.context))
        text1 += self.val_type 
        text = text or text1
        files = [tempf.name,]
        server = self.context.MailHost.smtp_host
        
        try:
            sendattachment.send_mail(send_from=send_from,
                                 send_to=send_to,
                                 subject=subject,
                                 text=text,
                                 files=files,
                                 server=server,
                                 mimeb=("text", "html"),
                                 filenamepars=filenamepars,
                                 )
            text=self.translation_service.utranslate(domain='collective.validator.base',
                                                    msgid='mail_sent_message',
                                                    default="Mail sent",
                                                    context=self.context)
            logger.validator_info(text)
            plone_utils.addPortalMessage(text)
            
        except Exception, err:
            
            logger.exception('Error when sending the mail.')
            plone_utils.addPortalMessage(err)
            
        tempf.close()
