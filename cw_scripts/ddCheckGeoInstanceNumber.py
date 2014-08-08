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
# 

'''
NAME
    ddCheckGeoInstanceNumber.py

DESC
    Checks GEO name against GRP name and matches instance numbers to GRP.
    
USAGE
    ddCheckGeoInstanceNumber.do()
    
FUNCTIONS
    doCheckGeoInstanceNumber()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys


def doCheckGeoInstanceNumber(node):
    '''Checks GEO instance number against GRP.
    '''
    changed = False
    instanceNumber = node.rpartition("_")[2]
    children = [x for x in (cmds.listRelatives(node, children=True, allDescendents=True, path=True) or []) if cmds.nodeType(x) == "transform"]
    for child in children:
        childParts = child.rpartition("|")[2].rpartition("_")
        if not childParts[2] == instanceNumber:
            changed = True
            newChildName = "%s_%s" % (childParts[0], instanceNumber)
            try:
                cmds.rename(child, newChildName)
            except:
                sys.stdout.write("---> Unable to rename fix instance number of %s.\n" % child)
            
    return changed
    
# end (doCheckGeoNameWithGrp)


def do(nodes=None):
    '''Checks GEO name against GRP name.
    '''
    geoRenamed = False
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if not cmds.objExists(node):
            continue
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to check geo instance numbers for referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
        
        changed = doCheckGeoInstanceNumber(node)
        if changed:
            geoRenamed = True
    
    return geoRenamed
    
# end (do)
