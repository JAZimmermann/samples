#
# Copyright (c) [2014] John Zimmermann
#
# $URL$
# $Date: 2014-08-28$
# $Revision: 1.0$
# $Author: johnz $
#

import os
import smtplib
import sys

# apath = "B:/home/johnz/scripts/jbtools"
# if apath not in sys.path:
#     sys.path.insert(2, apath)
#
# from common.vp_mail import email_templates, vp_mail, publish_notes

apath = os.getenv("PYTHONPATH")
if apath not in sys.path:
    sys.path.insert(2, apath)

from vir_prod.vp_mail import email_templates, vp_mail, publish_notes


class PublishEmail(object):
    '''
    build and send email
    '''
    _DEFAULT_HOST = "172.25.1.8"
    def __init__(self, category_template, get_notes=True,
                                    host_server=None, debug_level=1):
        '''
        initialize instance
        '''
        self._host = None
        self._category_details = None
        self._mail = None
        self._publish_details = None
        self._connect_server = None
        self._get_notes = get_notes
        self._debug_level = debug_level

        self.host = host_server
        self.category_details = category_template

    @property
    def host(self):
        '''
        get host address
        '''
        return self._host

    @host.setter
    def host(self, server):
        '''
        set host address to use when sending email

        :type   server: C{str}
        :param  server: server address used to send mail through
        '''
        self._host = server if server else self._DEFAULT_HOST

    @property
    def category_details(self):
        return self._category_details

    @category_details.setter
    def category_details(self, det_template):
        etemplates = email_templates.EmailTemplates()

        self._category_details = etemplates.get_template(det_template)

    @property
    def publish_details(self):
        '''
        get publish details
        '''
        return self._publish_details

    @publish_details.setter
    def publish_details(self, pub_details):
        '''
        collect publish details used in creating mail

        :type   pub_details: C{dict}
        :param  pub_details: publish details including names, files, etc
                                necessary to fill in template
        '''
        if not isinstance(pub_details, dict):
            raise TypeError("%s is not a dict" % pub_details)

        if self._get_notes and not pub_details.get("Notes"):
            pub_details["Notes"] = publish_notes.PublishNotes().notes

        self._publish_details = pub_details

        # initalize VPMail instance with provided details to mail
        self.mail = pub_details

    @property
    def mail(self):
        '''
        get mail details
        '''
        return self._mail

    @mail.setter
    def mail(self, details):
        '''
        create mail information based on template and details

        :type   details: C{dict}
        :params details: details dictionary used to fill in mail template
        '''
        self._mail = vp_mail.VPMail(vp_mail.Templation(), details)

    def build_email(self):
        '''
        build email from template details
        '''
        if not self.mail:
            raise Exception("Mail <VPMail> object has not yet been set. "
                            + "Unable to proceed.")
        if not self.category_details.get("From"):
            raise KeyError(
                        "Unable to send email without a From / Sender address")
        self.mail.from_addrs = self.category_details.get("From")

        if self.category_details.get("To"):
            self.mail.to_addrs = self.category_details.get("To")
        if self.category_details.get("Cc"):
            self.mail.cc_addrs = self.category_details.get("Cc")
        if self.category_details.get("Bcc"):
            self.mail.bcc_addrs = self.category_details.get("Bcc")
        if not self.mail.to_addrs \
                and not self.mail.cc_addrs \
                and not self.mail.bcc_addrs:
            raise KeyError(
                    "Unable to send mail without a TO, CC, or BCC address(es).")

        if self.category_details.get("Subject Template"):
            self.mail.subject = self.category_details.get("Subject Template")

        if self.category_details.get("Template File"):
            self.mail.body = self.category_details.get("Template File")

    def send_mail(self):
        '''
        attempt to send email through smtp
        '''
        try:
            print "Sending mail '%s' to the following addresses %s..." \
                                            % (self.mail.subject,
                                               ",".join(self.mail.all_to_addrs))
            self._connect_server = smtplib.SMTP(self.host)
            self._connect_server.set_debuglevel(self._debug_level)
            status = self._connect_server.sendmail(self.mail.from_addrs,
                                          self.mail.all_to_addrs,
                                          str(self.mail))
            print "Status of sent mail: %s" % status
            self._connect_server.quit()
        except smtplib.SMTPConnectError, emsg:
            print "Issues connecting to send mail..\n\t%s" % emsg
            raise smtplib.SMTPConnectError

        except Exception, emsg:
            raise Exception("Issues sending mail..\n\t%s" % emsg)

    def print_message(self):
        '''
        print out mail information
        '''
        print self.mail


def test():
    '''
    publish email module tester
    '''
    # collect publish details expected for templation
    pub_details = {"SHOW": "DEVTD",
                   "ARTIST": "Bobo the monkey",
                   "FILE": "tester_obj.ma",
                   "FILEPATH": "B:/show/DEVTD/assets/testing/testing_obj.ma",
                   "FBXPATH": "B:/show/DEVTD/assets/testing/testing_obj.fbx",
                   "Set": "0004_JAB_undercove",
                   "Notes": "'To Start Press Any Key'. Where's the ANY key?"
                   }

    # initialize instance with specified template category
    pe_mail = PublishEmail("tester")
    # pass / assign necessary publish details
    pe_mail.publish_details = pub_details
    # process details in order to build mail
    pe_mail.build_email()

    # attempt to mail specified template and details
    pe_mail.send_mail()
    sys.stdout.write("Sent the following mail.. \n%s" % pe_mail.print_message())