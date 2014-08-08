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
    ddImportFromReference.py

DESC
    Import selected nodes from reference.
    
USAGE
    ddImportFromReference.do()
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import sys

# VAD
import ddCheckGeoInstanceNumber; reload(ddCheckGeoInstanceNumber)
import ddRemoveDuplicateShaders; reload(ddRemoveDuplicateShaders)


def do(nodes=None):
    '''
    Import selected nodes from reference.
    @param nodes: One or more GEO or GRP nodes.
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    cmds.namespace(setNamespace=":")
    # Try to turn off Viewport 2.0 to prevent fatal errors.
    try:
        mel.eval('setRendererInModelPanel base_OpenGL_Renderer modelPanel4;')
    except:
        pass
    
    # Create a temporary top group.
    topGrp = "tempRefGrp"
    if cmds.objExists(topGrp):
        cmds.delete(topGrp)
    topGrp = cmds.createNode("transform", name="tempRefGrp")
    newTopNodes = list()
    
    for node in nodes:
        if not cmds.objExists(node):
            continue
            
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> %s is not referenced. Skipping...\n" % node.rpartition("|")[2])
            continue
        
        currentNode = node
        referenceFile = cmds.referenceQuery(node, filename=True)
        tempNamespace = ""
        # Gather the reference node data.
        try:
            tempNamespace = "tempNamespace"
            cmds.file(referenceFile, edit=True, namespace=tempNamespace)
            currentNode = "%s:%s" % (tempNamespace, node.rpartition(":")[2])
        except:
            pass
        
        # Parent the namespace objects under the temporary group.
        currentParent = cmds.listRelatives(currentNode, path=True, parent=True)
        cmds.parent(currentNode, topGrp)
        
        # Import from reference and merge namespace with root.
        cmds.file(referenceFile, importReference=True, mergeNamespaceWithRoot=True)
        if not tempNamespace == "":
            if cmds.namespace(exists="%s" % tempNamespace):
                cmds.namespace(removeNamespace=tempNamespace, mergeNamespaceWithRoot=True)
        
        # Find the imported nodes under the temporary group and reparent to original location.
        topNode = cmds.listRelatives(topGrp, children=True, path=True)
        newTopNode = topNode[0]
        if currentParent:
            newTopNode = cmds.parent(newTopNode, currentParent)[0]
        else:
            newTopNode = cmds.parent(newTopNode, world=True)[0]
        
        # Fix the GEO instance numbers.
        done = ddCheckGeoInstanceNumber.do(newTopNode)
        
        # Reassign the shaders.
        done = ddRemoveDuplicateShaders.do(newTopNode)
        
        newTopNodes.append(newTopNode)
    
    # Delete the temporary group.
    if cmds.objExists(topGrp):
        cmds.delete(topGrp)
    
    return newTopNodes
    
# end (do)
