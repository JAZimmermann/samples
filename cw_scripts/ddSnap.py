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
# $Date: 2014-06-10$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddSnap.py

DESC
    Snaps second object to first.
    
USAGE
    ddSnap.do()
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import sys


def do(selection=None):
    '''
    Snaps second object to first.
    @param selection: List of 2 objects (optional).
    '''
    if not selection:
        selection = cmds.ls(selection=True, long=True)
        
    if not len(selection) == 2:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="Select exactly two objects to snap the second to the first.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        if confirm == "Ok":
            return
            
    source = selection[0]
    target = selection[1]
    
    try:
        cmds.delete(cmds.parentConstraint(source, target, mo=False))
        cmds.delete(cmds.scaleConstraint(source, target, mo=False))
    except:
        sys.stdout.write("Unable to snap %s to %s. \n" % (target, source))
        
# end (do)
