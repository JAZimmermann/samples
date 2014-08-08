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
NAME    ddAddGrpMetadata.py

DESC    Adds metadata to GRP nodes. 
        If no nodes specified, adds metadata to all GRP nodes in scene file.

USAGE   ddAddGrpMetadata.do(nodes)
        @param nodes: Single node or list of nodes.
        
FUNCTIONS
    doAddGrpMetadata()
    do()
    
'''


import maya.cmds as cmds
import sys


def doAddGrpMetadata(node):
    '''Creates metadata attribute and sets value.
    '''
    tolerance = 0.0001
    
    # Translation data.
    attrName = "originalPivot"
    # Get current translation values.
    pos = cmds.getAttr("%s.t" % node)[0]
    values = [pos[0], pos[1], pos[2]]
    # Reduce precision of data.
    for i in range(3):
        if abs(pos[i]) < tolerance:
            values[i] = "0"
        else:
            values[i] = "%.6f" % values[i]
    # Create attribute and store data.
    if not cmds.attributeQuery(attrName, node=node, exists=True):
        cmds.addAttr(node, longName=attrName, dataType="string")
    cmds.setAttr("%s.%s" % (node, attrName), "(%s, %s, %s)" % (values[0], values[1], values[2]), type="string")
    
    # Rotation data.
    attrName = "originalRotation"
    # Get current rotation values.
    rot = cmds.getAttr("%s.r" % node)[0]
    values = [rot[0], rot[1], rot[2]]
    # Reduce precision of data.
    for i in range(3):
        if abs(rot[i]) < tolerance:
            values[i] = "0"
        else:
            values[i] = "%.6f" % values[i]
    # Create attribute and store data.
    if not cmds.attributeQuery(attrName, node=node, exists=True):
        cmds.addAttr(node, longName=attrName, dataType="string")
    cmds.setAttr("%s.%s" % (node, attrName), "(%s, %s, %s)" % (values[0], values[1], values[2]), type="string")
    
    # Scale data.
    attrName = "originalScale"
    # Get current scale values.
    scl = cmds.getAttr("%s.s" % node)[0]
    values = [scl[0], scl[1], scl[2]]
    # Reduce precision of data.
    for i in range(3):
        if abs(scl[i] - 1.0) < tolerance:
            values[i] = "1.0"
        else:
            values[i] = "%.6f" % values[i]
    # Create attribute and store data.
    if not cmds.attributeQuery(attrName, node=node, exists=True):
        cmds.addAttr(node, longName=attrName, dataType="string")
    cmds.setAttr("%s.%s" % (node, attrName), "(%s, %s, %s)" % (values[0], values[1], values[2]), type="string")
    
    
    # Additional tags for MPC (environment assets only)
    if node.rpartition("|")[2].startswith("env"):
        tagName = ""
        assetName = ""
        nodeSplit = node.rpartition("|")[2].rpartition("_GRP")[0].split("_")
        
        if len(nodeSplit) == 3:
            assetName = nodeSplit[2]
        elif len(nodeSplit) == 4:
            tagName = nodeSplit[2]
            assetName = nodeSplit[3]
        
        if assetName:
            nodeList = [x for x in (cmds.listRelatives(node, path=True, allDescendents=True) or []) if cmds.nodeType(x) == "transform"]
            nodeList.append(node)
            
            # Tag data.
            attrName = "Tag"
            # Create attribute and store data.
            for currentNode in nodeList:
                if not cmds.attributeQuery(attrName, node=currentNode, exists=True):
                    cmds.addAttr(currentNode, longName=attrName, dataType="string")
                cmds.setAttr("%s.%s" % (currentNode, attrName), tagName, type="string")
                
            # Asset data.
            attrName = "Asset"
            # Create attribute and store data.
            for currentNode in nodeList:
                if not cmds.attributeQuery(attrName, node=currentNode, exists=True):
                    cmds.addAttr(currentNode, longName=attrName, dataType="string")
                cmds.setAttr("%s.%s" % (currentNode, attrName), assetName, type="string")
    
# end (doAddGeoMetadata)


def do(nodes=None):
    '''
    Adds metadata attribute to GRP nodes.
    @param nodes: Single node or list of nodes.
    '''
    sys.stdout.write("Adding metadata to GRP nodes... \n")
    cmds.refresh()
    
    # If no nodes, get all GRP nodes in scene file.
    if not nodes:
        nodes = cmds.ls("*_GRP*", type="transform", long=True)
        
    # Make a list out of nodes.
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        # Skip if node is referenced.
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            doAddGrpMetadata(node)
        
# end (do)
