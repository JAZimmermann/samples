#
# Copyright (c) [2014] John Zimmermann
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