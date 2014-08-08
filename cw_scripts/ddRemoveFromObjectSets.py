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
    ddRemoveFromObjectSets.py

DESC
    Removes nodes from object sets.
    
USAGE
    ddRemoveFromObjectSets.do()
    
FUNCTION
    ddRemoveFromObjectSets()
    do()
    
'''

# MAYA
import maya.cmds as cmds


def doRemoveFromObjectSets(node):
    '''Remove node from any objectSets.
    '''
    shapes = cmds.listRelatives(node, shapes=True, path=True) or []
    for shape in shapes:
        objectSets = cmds.listConnections(shape, type="objectSet", source=True, destination=False) or []
        for objectSet in objectSets:
            setMembers = cmds.sets(objectSet, query=True) or []
            for setMember in setMembers:
                if setMember.partition(".")[0] == node:
                    cmds.sets(setMember, rm=objectSet)


def do(nodes=None):
    '''Remove one or more nodes from any objectSets.
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        geoNodes = cmds.listRelatives(node, children=True, path=True) or []
        for geoNode in geoNodes:
            doRemovePivotOffsets(geoNode)
    
# end (do)
