# FROM http://snippets.dzone.com/posts/show/2038
# NBB: Original version has error on line 27:
#        part.set_payload( open(file,"rb").read() )

import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_from, send_to, subject, text, files=[], server="localhost", mimeb=("application", "octet-stream"), filenamepars=[]):
    assert type(send_to)==list
    assert type(files)==list
    assert len(mimeb)==2
    if filenamepars:
        assert len(filenamepars)>=2

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    prog=0
    for f in files:
        prog+=1
        part = MIMEBase(mimeb[0], mimeb[1])
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        if not filenamepars:
            stfile = part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        else:
            if len(files)==1:
                stfile =  "%s%s" % (filenamepars[0], filenamepars[1])
            else:
                stfile =  "%s%s%s" % (filename[0], prog, filenamepars[1])
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % stfile)
    msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
 
