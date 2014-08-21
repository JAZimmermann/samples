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
    ddResetGeoMetadata.py

DESC
    Reset position of GEO nodes to metadata.
    
USAGE
    ddResetGeoMetadata.do()

FUNCTIONS
    doResetGeoMetadata()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys


def doResetGeoMetadata(node):
    '''
    Resets position of GEO node to metadata.
    @param node: GEO node.
    '''
    attrName = "originalPivot"
    if cmds.attributeQuery(attrName, node=node, exists=True):
        # Get the stored metadata.
        pos = eval(cmds.getAttr("%s.%s" % (node, attrName)))
        try:
            # Unlock attributes.
            for ch in ["t", "r", "s"]:
                cmds.setAttr("%s.%s" % (node, ch), lock=False)
            for ch in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
                cmds.setAttr("%s.%s" % (node, ch), lock=False)
            
            # Zero the local rotate pivots.
            cmds.xform(node, objectSpace=True, rotatePivot=[0,0,0])
            cmds.xform(node, objectSpace=True, scalePivot=[0,0,0])
            
            # Reset the transformations from the metadata.
            cmds.setAttr("%s.t" % node, pos[0], pos[1], pos[2])
            cmds.setAttr("%s.r" % node, 0, 0, 0)
            cmds.setAttr("%s.s" % node, 1, 1, 1)
            
            # Relock the attributes.
            for ch in ["t", "r", "s"]:
                cmds.setAttr("%s.%s" % (node, ch), lock=True)
        except:
            sys.stdout.write("--> Unable to reset metadata for %s. Skipping... \n" % node)
            return False
    else:
        # Attribute does not exist.
        sys.stdout.write("--> No metadata found for %s. Asset might not have been published. Skipping... \n" % node)
        return False
        
    return True
    
# end (doResetGeoMetadata)


def do(nodes=None, hierarchy=True):
    '''
    Resets position of GEO node to metadata.
    @param nodes: One or more top GRP or GEO nodes (optional).
    @param hierarchy: If True, includes children GEO nodes (optional).
    '''
    # Get a list of nodes.
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    if not isinstance(nodes, list):
        nodes = [nodes]
    
    failed = list()
    for node in nodes:
        # Check if node is referenced.
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to reset metadata of referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        if not hierarchy:
            # Only check the node, ignore the children.
            doResetGeoMetadata(node)
        else:
            # Zero the local rotate pivots of the top node
            cmds.xform(node, objectSpace=True, rotatePivot=[0,0,0])
            cmds.xform(node, objectSpace=True, scalePivot=[0,0,0])
            
            # Only check the children, ignore top node.
            children = [x for x in (cmds.listRelatives(node, children=True, path=True, allDescendents=True) or []) 
                        if cmds.nodeType(x) == "transform" and not "_GRP_" in x.rpartition('|')[-1]]
            for child in children:
                valid = doResetGeoMetadata(child)
                if not valid:
                    failed.append(child)
                    
    # Notify user of failed nodes.
    if failed:
        failedStr = ""
        for failedNode in failed:
            failedStr += "%s, " % failedNode
            
        confirmPivots = cmds.confirmDialog(
                title="Warning", messageAlign="center",
                message='Check script editor... Unable to reset the metadata for %s. ' % failedStr[:-2], 
                button=["Ok"],  
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return False
    
    return True
    
# end (do)
