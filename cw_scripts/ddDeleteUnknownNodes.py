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
# $Date: 2014-07-01$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddDeleteUnknownNodes.py
    
DESC
    Delete unknown nodes.

USAGE
    ddDeleteUnknownNodes.do()
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import sys

def do():
    unknownNodes = cmds.ls(type="unknown") or []
    for unknownNode in unknownNodes:
        if not cmds.objExists(unknownNode):
            continue
        if cmds.lockNode(unknownNode, query=True, lock=True):
            cmds.lockNode(unknownNode, lock=False) 
        cmds.delete(unknownNode)
        sys.stdout.write("Deleted %s.\n" % unknownNode)
        
# end (do)
