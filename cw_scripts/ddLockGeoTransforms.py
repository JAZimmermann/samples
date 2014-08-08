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
    ddLockGeoTransforms.py

DESC
    Locks transform channels on GEO nodes.
    
USAGE
    ddLockGeoTransforms.do()
    
FUNCTIONS
    doLockGeoTransforms()
    do()
    
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import sys


def doLockGeoTransforms(node):
    '''Locks transform channels on GEO node.
    '''
    if "GEO" in node:
        for attr in ["t", "r", "s"]:
            cmds.setAttr("%s.%s" % (node, attr), lock=True)
            
# end (doLockGeoTransforms)


def do(nodes=None, hierarchy=True):
    '''
    Locks transform channels.
    @param nodes: One or more GEO or GRP nodes (optional).
    @param hierarchy: If True, unlock children GEO nodes (optional).
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to lock transforms on referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        if not hierarchy:
            # Lock transforms on node only.
            doLockGeoTransforms(node)
        else:
            # Lock transforms on node and children.
            children = [x for x in cmds.listRelatives(node, children=True, path=True, allDescendents=True) or [] if cmds.nodeType(x) == "transform"]
            children.append(node)
            for child in children:
                doLockGeoTransforms(child)
                
# end (do)
