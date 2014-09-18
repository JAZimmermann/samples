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
# $Date: 2014-09-18$
# $Revision: 1.0$
# $Author: johnz $
#

import warnings
import maya.cmds as mc


class WorkingUnitsWarning(UserWarning):
    pass


def check_units(expected="cm"):
    '''
    check to make sure scene working units are in expected units
    '''
    current_units = mc.currentUnit(query=True, linear=True)
    if current_units != expected:
        notify_wrong_units(expected, current_units)


def notify_wrong_units(expected, current):
    '''
    provided notification dialog stating working units need to be set properly

    :type   expected: C{str}
    :param  expected: working units scene is expected to be in
    :type   current: C{str}
    :param  current: working units scene is currently in
    '''
    working_units = {"mm": "millimeter",
                     "cm": "centimeter",
                     "m": "meter",
                     "km": "kilometer",
                     "in": "inch",
                     "ft": "foot",
                     "yd": "yard",
                     "mi": "mile"
                    }

    msg = "Your scene is currently in the wrong working units." \
          + "\nCurrently in %ss." % working_units[current] \
          + "\nPlease make sure to change to the correct expected" \
          + " working units, %ss" % working_units[expected]

    warnings.warn(msg, WorkingUnitsWarning)

    result = mc.confirmDialog(title="Warning", messageAlign="center",
                              message=msg,
                              button=["OK"], defaultButton="OK",
                              cancelButton="OK", dismissString="OK")

    return