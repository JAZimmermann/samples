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

import csv
import os


class EmailTemplates(object):
    '''
    collect email templates information from csv
    '''
    def __init__(self, csv_file=None):
        '''
        initialize instance
        '''
        self._csv_file = csv_file
        self._templates = {}

        self._process_csv()

    @property
    def csv_file(self):
        '''
        get current csv file to use
        '''
        if self._csv_file and os.path.isfile(self._csv_file):
            print "Utilizing provided csv template %s" \
                                % os.path.basename(self._csv_file)
            return self._csv_file
        else:
            print "Utilizing default csv template %s" \
                                % os.path.basename(self.default_csv_template)
            return self.default_csv_template

    @property
    def default_csv_template(self):
        '''
        get default csv template path
        '''
        cwd = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(cwd, 'publish_email_templates.csv')

    def get_template(self, category):
        '''
        get specified categories template details

        :type   category: C{str}
        :param  category: provided category name to search for template
        '''
        for template in self._templates:
            if template["Category"] == category:
                return self._get_extra_details(template)

        raise Exception("Failed to locate category %s, in the csv." % category)

    def _process_csv(self):
        '''
        collect information from csv file
        '''
        try:
            ifile = open(self.csv_file, "r")
            self._templates = csv.DictReader(ifile)
            # ifile.close()
        except csv.Error, emsg:
            raise csv.Error("Issues with csv file %s. %s"
                                    % (os.path.basename(self.csv_file), emsg))
        except Exception:
            raise Exception("Issues processing CSV file %s." % self._csv_file)

    @staticmethod
    def _get_extra_details(template):
        '''
        attempt to collect basic details such as artist email for From, etc.

        :type   template: C{dic}
        :param  template: dictionary of category email details to add to for use
        '''
        template['From'] = os.getenv("ARTIST_EMAIL") \
                                    if os.getenv("ARTIST_EMAIL") else None
        # template['SHOW'] = os.getenv("SHOW") if os.getenv("SHOW") else None

        return template