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
    ddRemoveNamespaces.py

DESC
    Removes namespaces from nodes.
    
USAGE
    ddRemoveNamespaces.do()
    
FUNCTION
    doRemoveNamespaces()
    do()
    
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import os
import sys


def doRemoveNamespaces(node):
    '''
    Removes namespaces from node, children and connections.
    @param node:
    '''
    if not cmds.objExists(node):
        return node
    
    newTopNode = node
    
    # Get the children.
    nodeChildren = [x for x in (cmds.listRelatives(node, path=True, children=True) or []) if cmds.nodeType(x) == "transform"]
    
    if (":" in node) or nodeChildren:
        # Build a list of all connected namespaces to be removed.
        namespaceList = list()
        
        # Parent the node to a temporary group to make it easier to find later.
        topGrp = cmds.createNode("transform", name="tempRefGrp")
        currentParent = cmds.listRelatives(node, path=True, parent=True)
        currentNode = cmds.parent(node, topGrp)
        
        # Add the namespace of the top node.
        if ":" in node:
            namespaceList.append(node.rpartition(":")[0].rpartition("|")[2])
        
        # Add the namespaces of the children.
        for nodeChild in nodeChildren:
            if ":" in nodeChild:
                namespaceList.append(nodeChild.rpartition(":")[0].rpartition("|")[2])
        
        # Add the namespaces of the connections.
        children = [x for x in (cmds.listRelatives(currentNode, path=True, allDescendents=True) or []) if cmds.nodeType(x) == "mesh"]
        for child in children:
            cnxList = cmds.listConnections(child) or []
            for cnx in cnxList:
                if ":" in cnx:
                    namespaceList.append(cnx.rpartition(":")[0].rpartition("|")[2])
        
        # Merge all of the namespaces to the root.        
        namespaceList = list(set(namespaceList))
        for namespace in namespaceList:
            if cmds.namespace(exists=namespace):
                cmds.namespace(mergeNamespaceWithRoot=True, removeNamespace=namespace)
        
        # Find the top node again and reparent it.
        topNode = cmds.listRelatives(topGrp, children=True, path=True)
        if topNode:
            if currentParent:
                currentParent = currentParent[0]
                if cmds.objExists(currentParent):
                    newTopNode = cmds.parent(topNode[0], currentParent)[0]
                elif cmds.objExists(currentParent.rpartition(":")[2]):
                    newTopNode = cmds.parent(topNode[0], currentParent.rpartition(":")[2])[0]
            else:
                newTopNode = cmds.parent(topNode[0], world=True)[0]
                
        # Delete the temporary group.
        cmds.delete(topGrp)
        
    return newTopNode
    
# end (doRemoveNamespaces)


def do(nodes=None):
    '''
    Removes namespaces from nodes, children and connections.
    @param nodes: One or more nodes (optional).
    '''
    newNodes = list()
    
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if not cmds.objExists(node):
            continue
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to remove namespaces from referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        newNode = doRemoveNamespaces(node)
        newNodes.append(newNode)
        
    return newNodes
    
# end (do)
