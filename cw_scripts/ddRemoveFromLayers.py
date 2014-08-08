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
    ddRemoveFromLayers.py

DESC
    Disconnect layers from nodes.
    
USAGE
    ddRemoveFromLayers.do()
    
FUNCTIONS
    doRemoveFromLayers()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import os


def doRemoveFromLayers(node):
    '''Disconnect layers from nodes.
    '''
    topGrpLayer = None
    cnxList = [x for x in (cmds.listConnections(node, source=True, destination=False) or []) if cmds.nodeType(x) == "displayLayer"]
    if cnxList:
        topGrpLayer = cnxList[0]
    nodeList = cmds.listRelatives(node, path=True, allDescendents=True) or []
    nodeList.append(node)
    if nodeList:
        cmds.editDisplayLayerMembers("defaultLayer", nodeList, noRecurse=True)
    return topGrpLayer
    
# end (doRemoveFromLayers)


def do(nodes=None, hierarchy=True):
    '''Disconnect layers from nodes.
    '''
    topGrpLayers = list()
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        topLayer = doRemoveFromLayers(node)
        topGrpLayers.append(topLayer)
        
    return topGrpLayers
    
# end (do)
