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
NAME    ddAddGeoMetadata.py

DESC    Adds metadata to selected GEO nodes.

USAGE   ddAddGeoMetadata.do(nodes, hierarchy)
        @param nodes: Single node or list of nodes.
        @param hierarchy: Ignore node(s) and add attribute to children. 
        
FUNCTIONS
    doAddGeoMetadata()
    do()
'''


import maya.cmds as cmds
import sys


def doAddGeoMetadata(node):
    '''Creates metadata attribute and sets value.
    '''
    tolerance = 0.0001
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
    
    # Create attribute.
    if not cmds.attributeQuery(attrName, node=node, exists=True):
        cmds.addAttr(node, longName=attrName, dataType="string")
        
    # Store the data.
    cmds.setAttr("%s.%s" % (node, attrName), "(%s, %s, %s)" % (values[0], values[1], values[2]), type="string")
    
# end (doAddGeoMetadata)


def do(nodes=None, hierarchy=True):
    '''
    Adds metadata attribute to nodes and children (optional) and sets value.
    @param nodes: Single node or list of nodes.
    @param hierarchy: Ignore node(s) and add attribute to children. 
    '''
    # If no nodes, use selection.
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    
    # Make a list out of nodes.
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        # Skip if node is referenced.
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to add metadata to referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        # Single node case.
        if not "GRP" in node and not hierarchy:
            doAddGeoMetadata(node)
            
        # Hierarchy case (GEO), skipping the top node (GRP).
        elif hierarchy:
            children = [x for x in cmds.listRelatives(node, children=True, path=True, allDescendents=True) or [] if cmds.nodeType(x) == "transform"]
            if not "GRP" in node:
                children.append(node)
            for child in children:
                doAddGeoMetadata(child)
            
# end (do)
