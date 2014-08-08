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
    ddCheckPivotOffsets.py

DESC
    Checks if there are any pivot offsets on the node and children.
    
USAGE
    ddCheckPivotOffsets.do()
    
FUNCTION
    doCheckPivotOffsets()
    do()
    
'''

# MAYA
import maya.cmds as cmds


def doCheckPivotOffsets(node):
    '''Checks if there are any pivot offsets on the node and children.
    '''
    tolerance = 0.0001
    localRotatePivot = cmds.xform(node, query=True, objectSpace=True, rotatePivot=True)
    
    for attrValue in localRotatePivot:
        if abs(attrValue) > tolerance: return False
        
    if "_GRP_" in node.rpartition("|")[2]:
        children = [x for x in (cmds.listRelatives(node, children=True, path=True) or []) if cmds.nodeType(x) == "transform"]
        for child in children:
            childPos = cmds.getAttr("%s.t" % child)[0]
            childRot = cmds.getAttr("%s.r" % child)[0]
            childScl = cmds.getAttr("%s.s" % child)[0]
            childLocalRotatePivot = cmds.xform(child, query=True, objectSpace=True, rotatePivot=True)
            attrName = "originalPivot"
            if cmds.attributeQuery(attrName, node=child, exists=True):
                childMeta = eval(cmds.getAttr("%s.%s" % (child, attrName)))
                for p, m in zip(childPos, childMeta):
                    if abs(p-m) > tolerance: return False
            
            for attr in [childRot, childLocalRotatePivot]:
                for attrValue in attr:
                    if abs(attrValue) > tolerance: return False
                        
            for attrValue in childScl:
                if abs(attrValue-1.0) > tolerance: return False
            
    return True
    
# end (doCheckPivotOffsets)


def do(nodes=None):
    '''Checks if there are any pivot offsets on the node and children.
    '''
    pivotOffsetList = list()
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        valid = doCheckPivotOffsets(node)
        if not valid:
            pivotOffsetList.append(node)
    
    return pivotOffsetList
    
# end (do)
