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
    ddTransferTransformsFromGeo.py

DESC
    Transfers transformation data from GEO to GRP node.
    
USAGE
    ddTransferTransformsFromGeo.do()

FUNCTIONS
    doTransferTransformsFromGeo()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys



def doTransferTransformsFromGeo(node):
    '''
    Transfers transformation data from one child GEO node to its top GRP node.
    @param node: One top GRP node which contains one child GEO node.
    '''
    children = [x for x in (cmds.listRelatives(node, children=True, path=True) or []) if cmds.nodeType(x) == "transform"]
    if len(children) == 1:
        child = children[0]
        
        # Create temporary null hierarchy for transferring data.
        nullParent = cmds.createNode("transform", name="tempNullParent")
        null = cmds.createNode("transform", name="tempNull", parent=nullParent)
        
        # Snap nullParent to GEO node and set null child to local rotate pivot.
        cmds.delete(cmds.parentConstraint(child, nullParent, mo=0))
        cmds.delete(cmds.scaleConstraint(child, nullParent, mo=0))
        lrp = cmds.xform(child, query=True, objectSpace=True, rotatePivot=True)
        cmds.setAttr ("%s.t" % null, -1.0*lrp[0], -1.0*lrp[1], -1.0*lrp[2])
        
        # Zero out the GEO node.
        cmds.xform(child, objectSpace=True, rotatePivot=[0,0,0])
        cmds.xform(child, objectSpace=True, scalePivot=[0,0,0])
        cmds.setAttr("%s.t" % child, 0, 0, 0)
        cmds.setAttr("%s.r" % child, 0, 0, 0)
        cmds.setAttr("%s.s" % child, 1, 1, 1)
        
        # Zero out the GRP node.
        cmds.xform(node, objectSpace=True, rotatePivot=[0,0,0])
        cmds.xform(node, objectSpace=True, scalePivot=[0,0,0])
        cmds.setAttr("%s.t" % node, 0, 0, 0)
        cmds.setAttr("%s.r" % node, 0, 0, 0)
        cmds.setAttr("%s.s" % node, 1, 1, 1)
        
        # Snap the GRP node to the null position (local rotate pivot of GEO).
        cmds.delete(cmds.parentConstraint(null, node, mo=0))
        cmds.delete(cmds.scaleConstraint(null, node, mo=0))
        
        # Delete the temporary null hierarchy.
        cmds.delete(nullParent)
        
    elif len(children) > 1:
        sys.stdout.write("--> Cannot transfer transforms from GEO to GRP node. Too many nodes found under %s. Skipping...\n" % node.rpartition("|")[2])
        return
        
# end (doTransferTransformsFromGeo)


def do(nodes=None):
    '''
    Transfers transformation data from GEO to GRP node.
    @param nodes: One or more top GRP nodes (optional). 
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to transfer transforms of referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        doTransferTransformsFromGeo(node)
        
# end (do)



"""    
# old version

def doTransferTransformsFromGeo(node):
    '''Transfers transformation data from GEO to GRP node.
    '''
    children = [x for x in (cmds.listRelatives(node, children=True, path=True) or []) if cmds.nodeType(x) == "transform"]
    if len(children) == 1:
        child = children[0]
        null = cmds.createNode("transform", name="tempNull")
        cmds.parent(null, node, relative=True)
        cmds.delete(cmds.parentConstraint(child, null))
        cmds.delete(cmds.scaleConstraint(child, null))
        cmds.parent(null, world=True)
        
        worldRotatePivot = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)
        
        cmds.setAttr("%s.t" % child, 0, 0, 0)
        cmds.setAttr("%s.r" % child, 0, 0, 0)
        cmds.setAttr("%s.s" % child, 1, 1, 1)
        
        #cmds.setAttr("%s.rp" % node, worldRotatePivot[0], worldRotatePivot[1], worldRotatePivot[2])
        cmds.delete(cmds.parentConstraint(null, node))
        cmds.delete(cmds.scaleConstraint(null, node))
        
        cmds.delete(null)
        
    elif len(children) > 1:
        sys.stdout.write("--> Cannot transfer transforms from GEO to GRP node. Too many nodes found under %s. Skipping...\n" % node.rpartition("|")[2])
        return
        
# end (doTransferTransformsFromGeo)

"""

