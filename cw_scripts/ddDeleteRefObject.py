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
    ddDeleteRefObject.py

DESC
    Deletes selected referenced object(s) from scene.     

USAGE
    ddDeleteRefObject.do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import sys


def do(nodes=None):
    '''
    Deletes selected referenced object(s).
    @param nodes: One or more GEO or GRP nodes (optional).
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True) or []
    
    for sel in nodes:
        if cmds.objExists(sel):
            if not cmds.referenceQuery(sel, isNodeReferenced=True):
                sys.stdout.write("--> Not a referenced object: %s. Skipping...\n" % sel)
                continue
                
	    filename = cmds.referenceQuery(sel, filename=True)
            cmds.file(filename, removeReference=True)
            
# end (do)
