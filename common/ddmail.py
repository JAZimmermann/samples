#
# Copyright (c) [2014] John Zimmermann
#
# $URL$
# $Date: 2014-06-10$
# $Revision: 1.0$
# $Author: johnz $
#

'''
email -- send maiil to multiple people, with file attachements
'''
# adapted from dd.mail

import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from email.Header import Header


def sendMail(send_from, send_to, subject,
                text=None, html=None, files=None,
                server='172.25.1.8', send_cc=None):
    assert type(send_to) is list
    files = files or []
    assert type(files) is list
    send_cc = send_cc or []
    assert type(send_cc) is list

    # Need at least text or html specified
    assert text is not None or html is not None

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    if send_cc:
        msg['Cc'] = COMMASPACE.join(send_cc)

    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Header(subject)

    # attach parts into message container
    # according to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred
    if text is not None:
        msg.attach(MIMEText(text, 'plain'))

    if html is not None:
        msg.attach(MIMEText(html, 'html'))

    # attach files
    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(f))

    if send_cc:
        send_to += send_cc

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
