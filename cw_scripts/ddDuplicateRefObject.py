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
# $Date: 2014-05-30$
# $Revision: 1.1$
# $Author: cwong $
#


'''
NAME
    ddDuplicateRefObject.py

DESC
    Duplicates references of selected object(s) and places new referenced object(s) 
    at same position, orientation and scale as originals. Also adds new referenced object(s) 
    to same layer. Selects new object(s) when done.

USAGE
    ddDuplicateRefObject.do()
'''


# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import sys


def do(nodes=None):
    '''
    Duplicate referenced objects as referenced objects.
    @param nodes: One or more GEO or GRP nodes (optional).
    '''
    topGrp = "RefGrp"
    if not nodes:
        nodes = cmds.ls(selection=True, long=True) or []
        
    newSelection = list()
    referencedFiles = list()
    cmds.namespace(setNamespace=":")
    
    for node in nodes:
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Not a referenced object: %s. Skipping...\n" % node)
            continue
        
        # Get the referenced node data.
        namespace = cmds.referenceQuery(node, namespace=True)
        namespaceChildren = [x for x in (cmds.ls("%s:*" % namespace, long=True) or []) if cmds.nodeType(x) == "transform"]
        
        # Get the top node.
        currentNode = node
        for child in namespaceChildren:
            parent = cmds.listRelatives(child, parent=True, path=True)
            if parent and not parent in namespaceChildren:
                currentNode = parent
        
        # Find the original reference information.
        filename = cmds.referenceQuery(currentNode, filename=True)
        nodeParent = cmds.listRelatives(currentNode, parent=True, path=True)
        topGrpLayer = None
        cnxList = [x for x in (cmds.listConnections(currentNode, source=True, destination=False) or []) if cmds.nodeType(x) == "displayLayer"]
        if cnxList:
            topGrpLayer = cnxList[0]
            
        # Check if new reference has already been created for this object.
        if filename in referencedFiles:
            continue
            
        # Reference nodes under topGrp.
        namespace = cmds.file(filename, query=True, namespace=True)
        cmds.file(filename, reference=True, namespace=namespace, groupReference=True, groupName=topGrp)
        referencedFiles.append(filename)
        
        # Transform the new nodes.
        newObjects = [x for x in cmds.listRelatives(topGrp, path=True) if cmds.nodeType(x) == "transform"] or None
        if newObjects:
            newNamespace = newObjects[0].rpartition(":")[0]
            for newObject in newObjects:
                # Find the matching original object.
                matchingObject = newObject.replace(newNamespace, namespace)
                if cmds.objExists(matchingObject):
                    # Get the transforms of the original object.
                    pos = cmds.getAttr("%s.t" % matchingObject)[0]
                    rot = cmds.getAttr("%s.r" % matchingObject)[0]
                    scl = cmds.getAttr("%s.s" % matchingObject)[0]
                    
                    # Transform the new object.
                    cmds.setAttr("%s.t" % newObject, pos[0], pos[1], pos[2])
                    cmds.setAttr("%s.r" % newObject, rot[0], rot[1], rot[2])
                    cmds.setAttr("%s.s" % newObject, scl[0], scl[1], scl[2])
                    
        # Clean out the topGrp.
        topGrpObjects = cmds.listRelatives(topGrp, path=True) or None
        if topGrpObjects:
            newSelection.extend(topGrpObjects)
            if nodeParent:
                cmds.parent(topGrpObjects, nodeParent)
            else:
                cmds.parent(topGrpObjects, world=True)
                
            if topGrpLayer:
                cmds.editDisplayLayerMembers(topGrpLayer, topGrpObjects, noRecurse=True)
                
        if cmds.objExists(topGrp):
            cmds.delete(topGrp)
    
    if newSelection:
        cmds.select(newSelection, replace=True)
    
# end (do)
