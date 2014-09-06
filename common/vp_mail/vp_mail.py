#
# Confidential and Proprietary Source Code
#
# This Digital Domain Productions, Inc. source code, including without
# limitation any human-readable computer programming code and associated
# documentation (together "Source Code"), contains valuable confidential,
# proprietary and trade secret information of Digital Domain Productions and is
# protected by the laws of the United States and other countries. Digital
# Domain Productions, Inc. may, from time to time, authorize specific employees
# to use the Source Code internally at Digital Domain Production Inc.'s premises
# solely for developing, updating, and/or troubleshooting the Source Code. Any
# other use of the Source Code, including without limitation any disclosure,
# copying or reproduction, without the prior written authorization of Digital
# Domain Productions, Inc. is strictly prohibited.
#
# Copyright (c) [2012] Digital Domain Productions, Inc. All rights reserved.
#
# $URL$
# $Date: 2014-08-22$
# $Revision: 1.0$
# $Author: johnz $
#

import email
import jinja2
import mimetypes
import os
import re


class Templation(object):
    '''
    Templating engine utilizing Jinja for generating email
        based on given template
    '''
    def __init__(self):
        '''
        initialize instance
        '''
        self._details = None
        self._template = None
        self._environment = jinja2.Environment(trim_blocks=True,
                                               autoescape=False)
        self._loader()

    @property
    def results(self):
        '''
        get rendered template string
        '''
        return self._template.render(self.details)

    @property
    def details(self):
        '''
        get details for template variables
        '''
        return self._details

    @details.setter
    def details(self, udetails):
        '''
        set collection of details for template variables

        :type   udetails: C{dict}
        :param  udetails: collection of details for template variables
        '''
        self._details = udetails

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, utemplate):
        self._template = self._load_template(utemplate)

    @property
    def default_template_path(self):
        '''
        directory path containing the default set of email body templates
        '''
        cwd = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(cwd, 'etemplates')

    def _loader(self, tpath=None):
        if not tpath or not os.path.isdir(tpath):
            tpath = self.default_template_path

        self._environment.loader = jinja2.FileSystemLoader(tpath)

    def _load_template(self, template):
        # check if provided template is just a string a
        template_str_pattern = re.compile("{{")
        if template_str_pattern.search(template):
            return self._environment.from_string(template)

        try:
            if os.path.isfile(os.path.abspath(template)):
                if os.path.dirname(os.path.abspath(template)) \
                                != self.default_template_path:
                    self._loader(os.path.dirname(os.path.abspath(template)))
                    template = os.path.basename(template)

            return self._environment.get_template(template)

        except jinja2.TemplateNotFound:
            if isinstance(template, str):
                return self._environment.from_string(template)
        except Exception, emsg:
            raise Exception("Issues loading template. %s" % emsg)


class VPMail(object):
    '''
    main class for email details
    '''
    def __init__(self, template=None, pub_details={}):
        '''
        initialize instance
        '''
        self._message_details = email.MIMEMultipart.MIMEMultipart()
        self._message_details["Date"] = email.Utils.formatdate(localtime=True)
        self._template = template
        if not template:
            self._template = Templation()
        self._template.details = pub_details

    def __str__(self):
        '''
        represent message details as a string
        :return:
        '''
        return self._message_details.as_string()

    @property
    def template(self):
        return self._template

    @property
    def from_addrs(self):
        '''
        get list of sender addresses
        '''
        return self._message_details['From'].split(email.Utils.COMMASPACE)

    @from_addrs.setter
    def from_addrs(self, addrs):
        '''
        set string of comma separated sender addresses

        :type   addrs: C{list} or C{str}
        :param  addrs: provided list or string of sender addresses to process
        '''
        addrs = self.check_addrs_instance(addrs)

        self._message_details["From"] = email.Utils.COMMASPACE.join(addrs)

    @property
    def to_addrs(self):
        '''
        get list of recipient addresses
        '''
        return self._message_details['To'].split(email.Utils.COMMASPACE)

    @to_addrs.setter
    def to_addrs(self, addrs):
        '''
        set string of comma separated recipient addresses

        :type   addrs: C{list} or C{str}
        :param  addrs: provided list or string of recipient addresses to use
        '''
        addrs = self.check_addrs_instance(addrs)

        self._message_details['To'] = email.Utils.COMMASPACE.join(addrs)

    @property
    def cc_addrs(self):
        '''
        get list of cc-ed recipient addresses
        '''
        if not self._message_details['Cc']:
            return []
        return self._message_details['Cc'].split(email.Utils.COMMASPACE)

    @cc_addrs.setter
    def cc_addrs(self, addrs):
        '''
        set string of comma separated cc-ed recipient addresses

        :type   addrs: C{list} or C{str}
        :param  addrs: provided list or string of cc-ed recipient
                            addresses to use
        '''
        addrs = self.check_addrs_instance(addrs)

        self._message_details['Cc'] = email.Utils.COMMASPACE.join(addrs)

    @property
    def bcc_addrs(self):
        '''
        get list of bcc-ed recipient addresses
        '''
        if not self._message_details['Bcc']:
            return []
        return self._message_details['Bcc'].split(email.Utils.COMMASPACE)

    @bcc_addrs.setter
    def bcc_addrs(self, addrs):
        '''
        set string of comma separated bcc-ed recipient addresses

        :type   addrs: C{list} or C{str}
        :param  addrs: provided list or string of bcc-ed recipient
                            addresses to use
        '''
        addrs = self.check_addrs_instance(addrs)

        self._message_details['Bcc'] = email.Utils.COMMASPACE.join(addrs)

    @property
    def all_to_addrs(self):
        '''
        get a list of all to, cc-ed, and bcc-ed addresses to use
        '''
        return self.to_addrs + self.cc_addrs + self.bcc_addrs

    @property
    def subject(self):
        '''
        get subject line
        '''
        return self._message_details["Subject"]

    @subject.setter
    def subject(self, subject):
        '''
        set subject line to specified string or generated template string

        :type   subject: C{str}
        :param  subject: provided string or subject template string to process
                            for subject line
        '''
        self.template.template = subject
        self._message_details["Subject"] = self.template.results

    def body(self, btemplate):
        '''
        get body message processed for email based on provided template

        :type   btemplate: C{str}
        :param  btemplate: body template name for use
        '''
        subtype = self.check_mimetype(btemplate)

        self.template.template = btemplate
        # print self.template.results
        body = email.MIMEText.MIMEText(self.template.results, subtype)
        self._message_details.attach(body)
    body = property(fset=body)

    @staticmethod
    def check_mimetype(check_obj):
        '''
        get and check mimetype for file given, need plain text

        :type   check_obj: C{str}
        :param  check_obj: valid file path to be checked
        '''
        content_type = None
        encoding = None

        if os.path.isfile(check_obj):
            content_type, encoding = mimetypes.guess_type(check_obj)
        if not content_type or not encoding:
            content_type = "text/plain"
        main, sub = content_type.split("/", 1)
        if main != "text":
            raise TypeError("%s is not a valid type for %s" % (main, check_obj))

        return sub

    @staticmethod
    def check_addrs_instance(addrs):
        '''
        determine addrs is the proper instance type,
            looking a comma separated string or a list

        :type   addrs: C{list} or C{str}
        :param  addrs: provided list or string of addresses to use
        '''
        if isinstance(addrs, str):
            addrs = [x.strip() for x in addrs.split(email.Utils.COMMASPACE) if x]
        if not isinstance(addrs, list):
            raise TypeError("%s is not a list" % addrs)

        return addrs

