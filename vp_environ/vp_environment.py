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
# $Date: 2014-09-10$
# $Revision: 1.0$
# $Author: johnz $
#

import os


class VPEnvironmentException(Exception):
    pass


class VP_Environment(object):
    def test(self):
        if "SHOW" not in os.environ or os.getenv("SHOW") == "":
            raise VPEnvironmentException(
                "Please make sure that for a proper VP Environment, " \
                + "SHOW has been set.")

        if "ARTIST_EMAIL" not in os.environ or os.getenv("ARTIST_EMAIL") == "":
            raise VPEnvironmentException(
                "Please make sure that for a proper VP Environment, " \
                + "your artist email address has been provided.")

        if "ARTIST" not in os.environ or os.getenv("ARTIST") == "":
            raise VPEnvironmentException(
                "Please make sure that for VP Environment, your name " \
                + "has been provided.")