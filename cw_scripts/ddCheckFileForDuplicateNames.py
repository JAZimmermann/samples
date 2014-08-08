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
    ddCheckFileForDuplicateNames.py

DESC
    Check for duplicate names.
    
USAGE
    ddCheckFileForDuplicateNames.do()
'''

# MAYA
import maya.cmds as cmds


def do():
    '''Check for duplicate names.
    '''
    dividerTypes = ["GRP", "CPF", "CPO", "CPD"]
    duplicateNodes = list()
    allNodes = list()
    for dividerType in dividerTypes:
        dividerTypeNodes = [x for x in (cmds.ls("*_%s_*" % dividerType) or []) if cmds.nodeType(x) == "transform"]
        if dividerTypeNodes:
            allNodes.extend(dividerTypeNodes)
    for node in allNodes:
        if "|" in node and not node.startswith("|"):
            duplicateNodes.append(node)
    
    return duplicateNodes
    
# end (do)
