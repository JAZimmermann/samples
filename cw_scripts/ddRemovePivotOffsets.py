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
    ddRemovePivotOffsets.py

DESC
    Freezes transforms and removes pivot offsets. Deletes history and removes empty group nodes.
    
USAGE
    ddRemovePivotOffsets.do()

FUNCTIONS
    doRemovePivotOffsets()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys

# VAD
import ddUnlockGeoTransforms; reload(ddUnlockGeoTransforms)


def doRemovePivotOffsets(node, returnToPos=False, currentAssetCategory="environments"):
    '''
    Freezes transforms and removes pivot offsets.
    @paran node: One top GRP node.
    '''
    nodeParent = None
    currentNode = node
    dividerTypes = ["GRP", "CPF", "CPO", "CPD"]
    
    divider = ""
    nodeParts = node.rpartition("|")[2].split("_")
    for nodePart in nodeParts:
        if nodePart in dividerTypes:
            divider = nodePart
    
    tempParent = cmds.createNode("transform", name="tempParent")
    tempChildren = cmds.createNode("transform", name="tempChildren")
    
    
    # Parent to world.
    if divider:
        nodeParent = cmds.listRelatives(currentNode, parent=True, path=True)
        if nodeParent:
            currentNode = cmds.parent(currentNode, world=True)[0]
        
    # Freeze top node.
    pos = cmds.xform(currentNode, query=True, worldSpace=True, absolute=True, rotatePivot=True)
    rot = cmds.getAttr("%s.r" % currentNode)[0]
    scl = cmds.getAttr("%s.s" % currentNode)[0]
    
    # Move back to origin, relative to pivot.
    cmds.setAttr("%s.r" % currentNode, 0, 0, 0)
    cmds.setAttr("%s.s" % currentNode, 1, 1, 1)
    if not currentAssetCategory == "characters":
        cmds.move(0,0,0, currentNode, rotatePivotRelative=True)
    else:
        cmds.setAttr("%s.t" % currentNode, 0, 0, 0)
        if returnToPos:
            cmds.createNode("transform", name="tempCharReset")
            cmds.delete(cmds.parentConstraint(currentNode, "tempCharReset", mo=False))
            cmds.createNode("transform", name="tempCharZero")
            cmds.parent("tempCharZero", "tempCharReset")
        
    # Freeze transformations.
    cmds.makeIdentity(currentNode, apply=True, translate=True, rotate=True, scale=True, normal=False)
    
    # Get children GEO.
    nodeList = [x for x in (cmds.listRelatives(currentNode, path=True, allDescendents=True) or []) if cmds.nodeType(x) == "transform"]
    for nodeName in nodeList:
        cmds.polyMoveVertex(nodeName, localTranslate=(0,0,0), constructionHistory=False)
        cmds.select(clear=True)
        
    cmds.delete(currentNode, constructionHistory=True)    
    
    # Freeze children.
    for nodeName in nodeList:
        children = cmds.listRelatives(nodeName, children=True, path=True)
        if not children:
            cmds.delete(nodeName)
            continue
        else:
            for child in children:
                if cmds.nodeType(child) == "transform":
                    cmds.parent(child, tempChildren)
            
        nodeNameParent = cmds.listRelatives(nodeName, parent=True, path=True)
        pivotPos = cmds.xform(nodeName, query=True, worldSpace=True, rotatePivot=True)
        cmds.move(0,0,0, nodeName, rotatePivotRelative=True)
        
        if nodeNameParent:
            nodeName = cmds.parent(nodeName, tempParent)[0]
            
        cmds.makeIdentity(nodeName, apply=True, translate=True, rotate=True, scale=True, normal=False)
        cmds.polyMoveVertex(nodeName, localTranslate=(0,0,0), constructionHistory=False)
        cmds.select(clear=True)
        cmds.delete(nodeName, constructionHistory=True)
        
        if nodeNameParent:
            parentedNodes = cmds.listRelatives(tempParent, children=True, path=True)
            nodeName = cmds.parent(parentedNodes, nodeNameParent)[0]
        
        childNodes = cmds.listRelatives(tempChildren, children=True, path=True)
        
        cmds.setAttr("%s.t" % nodeName, pivotPos[0], pivotPos[1], pivotPos[2])
        if childNodes:
            cmds.parent(childNodes, nodeName)
    
    cmds.delete(tempParent, tempChildren)
    
    # Move top node back
    if returnToPos:
        if not currentAssetCategory == "characters":
            cmds.xform(currentNode, worldSpace=True, absolute=True, translation=pos)
        else:
            cmds.xform("tempCharReset", worldSpace=True, absolute=True, translation=pos)
            cmds.delete(cmds.parentConstraint("tempCharZero", currentNode, mo=False))
            cmds.delete("tempCharReset")
            
        cmds.setAttr("%s.r" % currentNode, rot[0], rot[1], rot[2])
        cmds.setAttr("%s.s" % currentNode, scl[0], scl[1], scl[2])
        
        if nodeParent:
            try:
                cmds.parent(currentNode, nodeParent)
            except:
                pass
            
    return currentNode
    
# end (doRemovePivotOffsets)


def do(nodes=None, returnToPos=False, currentAssetCategory="environments"):
    nodeList = list()
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to remove pivot offsets from referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
        
        ddUnlockGeoTransforms.do(nodes=node)
        newNode = doRemovePivotOffsets(node=node, returnToPos=returnToPos, currentAssetCategory=currentAssetCategory)
        nodeList.append(newNode)
    
    return nodeList
    
# end (do)
