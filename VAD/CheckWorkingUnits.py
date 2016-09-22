#
# Copyright (c) [2014] John Zimmermann
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
          + " working units, %ss." % working_units[expected] \
          + "\nThis *WILL* cause issues if you continue without fixing."

    warnings.warn(msg, WorkingUnitsWarning)

    result = mc.confirmDialog(title="Warning", messageAlign="center",
                              message=msg,
                              button=["OK"], defaultButton="OK",
                              cancelButton="OK", dismissString="OK")

    return