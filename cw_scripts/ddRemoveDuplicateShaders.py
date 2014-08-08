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
# $Date: 2014-06-19$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddRemoveDuplicateShaders.py

DESC
    Remove duplicate shading networks and remove trailing digits (eg. bark_SG1).
    
USAGE
    ddRemoveDuplicateShaders.do()
    
FUNCTIONS
    getConnectedShadingEngine()
    do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import sys


def getConnectedShadingEngine(node):
    '''
    Returns connected shading engine.
    @param node: A mesh or transform node.
    '''
    # Get shape node.
    shapeNode = ""
    if cmds.nodeType(node) == "mesh":
        shapeNode = node
    else:
        shapeNode = cmds.listRelatives(node, shapes=True, path=True)
        if shapeNode:
            shapeNode = shapeNode[0]
            
    # Get shading engine connections.
    if shapeNode: 
        shadingEngines = cmds.listConnections(shapeNode, type="shadingEngine") or []
        if shadingEngines:
            return shadingEngines[0]
            
    return None

# end (getConnectedShadingEngine)

    
def do(nodes=None):
    '''
    Reduce duplicate shading networks by reconnecting meshes to base shaders.
    Deleting the shading networks is handled elsewhere.
    @param nodes: One or more nodes.
    '''
    # Turn off Consolidate World attribute in Viewport 2.0 (can cause instability).
    try:
        cmds.setAttr("hardwareRenderingGlobals.consolidateWorld", 0)
    except:
        pass
            
    nodeList = None
    if not nodes:
        nodeList = cmds.ls(selection=True, long=True)
    else:
        nodeList = nodes[:]
    
    if not isinstance(nodeList, list):
        nodeList = [nodeList]
        
    for node in nodeList:
        # Get the meshes.
        meshNodes = [x for x in (cmds.listRelatives(node, path=True, allDescendents=True) or []) if cmds.nodeType(x) == "mesh"]

        for mesh in meshNodes:
            # Get the connected shading engines.
            shadingEngine = getConnectedShadingEngine(mesh)
            if not shadingEngine: 
                continue
            
            # Get the end digit of the shading engine.
            digit = shadingEngine.rpartition("_SG")[2]
            if not digit: 
                continue
            
            # Find the base shading engine without an end digit.
            baseShadingEngine = shadingEngine.rpartition(digit)[0]
            if not cmds.objExists(baseShadingEngine): 
                continue
            
            # If there is a base shading engine, assign it to the mesh.
            cmds.sets(mesh, forceElement=baseShadingEngine)
            shaderMeshList = [x for x in (cmds.listConnections(shadingEngine) or []) if cmds.listRelatives(x, shapes=True)]
            if shaderMeshList: 
                continue
                
    return True
    
# end (do)