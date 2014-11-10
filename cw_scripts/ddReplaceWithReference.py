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
    ddReplaceWithReference.py

DESC
    Replaces selected nodes with references.
    
USAGE
    ddReplaceWithReference.do()
        
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import os
import sys

# VAD
import ddConstants; reload(ddConstants)


def do(nodes=None, currentAssetLibrary=ddConstants.ASSETLIBRARY):
    '''
    Replaces selected nodes with references.
    @param nodes: One or moer GEO or GRP nodes (optional).
    @param currentAssetLibrary: Base asset library (optional).
    '''
    # Divider tokens: environment assets: GRP; character chessPieces: CPF, CPO, CPD.
    dividerTypes = ["CPF", "CPO", "CPD", "CPS"]
    
    # Character token abbreviations and equivalent asset directories.
    charType = { "hero": "hero", "bg": "background", "sec": "secondary" }
    
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    cmds.namespace(setNamespace=":")
    
    for node in nodes:
        if not node:
            sys.stdout.write("--> %s does not exist. Skipping...\n" % node)
            continue
            
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to replace referenced node %s with reference. Skipping... \n" % node.rpartition("|")[2])
            continue
            
        if ":" in node:
            sys.stdout.write("--> Unable to find original file for %s. Try removing namespaces first. Skipping... \n" % node.rpartition("|")[2])
            continue
        
        # Find the correct divider token used by the node.
        divider = "GRP"
        nodeParts = node.rpartition("|")[2].split("_")
        for nodePart in nodeParts:
            if nodePart in dividerTypes:
                divider = "%s_GRP" % nodePart

        # There should be at least 6 tokens to find the file.
        #   unless it's in the prop structure
        if not nodeParts[0].startswith('prop') and len(nodeParts) < 6:
            cmds.warning("--> Published asset file not found for %s. Skipping..." % node.rpartition("|")[2])
            continue
        
        currentPath = node
        found = False
        nodeName = ""
        # Find the full path to the top node containing the correct divider token.
        while not(currentPath == "") and not found:
            firstPart, pipeChr, lastPart = currentPath.rpartition("|")
            if divider in lastPart:
                found = True
                nodeName = lastPart
            else:
                currentPath = firstPart
        
        # Get the top node's parent.
        nodeParent = cmds.listRelatives(currentPath, parent=True, path=True)
        
        # Get the top node's layer.
        topGrpLayer = None
        cnxList = [x for x in (cmds.listConnections(currentPath, source=True, destination=False) or []) if cmds.nodeType(x) == "displayLayer"]
        if cnxList:
            topGrpLayer = cnxList[0]
            
        # Get the top node's transformations.
        pos = cmds.xform(currentPath, query=True, worldSpace=True, absolute=True, rotatePivot=True)
        rot = cmds.getAttr("%s.r" % currentPath)[0]
        scl = cmds.getAttr("%s.s" % currentPath)[0]
        
        nodePath, grp, version = nodeName.partition('_%s_' % divider)
        version = version.partition("_")[0]
        dirs, underscore, asset = nodePath.rpartition("_")
        nodePathParts = nodePath.split("_")
        
        # Build the path to the asset.
        assetPath = currentAssetLibrary
        for i in range(len(nodePathParts)):
            if currentAssetLibrary==ddConstants.CHAR_ASSETLIBRARY:
                if nodePathParts[i] == "char" or i > 2:
                    continue
                elif nodePathParts[i] in charType.keys():
                    assetPath = os.path.join(assetPath, charType[nodePathParts[i]])
                else:
                    assetPath = os.path.join(assetPath, nodePathParts[i])
                
            else:
                assetPath = os.path.join(assetPath, nodePathParts[i])
        
        # Build the asset filename and full path.
        assetFileName = "%s_%s.ma" % (asset, version)
        if currentAssetLibrary==ddConstants.CHAR_ASSETLIBRARY:
            assetPath = os.path.join(assetPath, "chesspiece", "published")
            asset = nodePath.replace("%s_%s_" % (nodePathParts[0], nodePathParts[1]), "")
            assetFileName = "%s_%s_%s.ma" % (asset, divider.replace("_GRP", ""), version)
        assetPath = os.path.join(assetPath, assetFileName)
        if not os.path.isfile(assetPath):
            cmds.warning("--> Published asset file not found for %s. Skipping..." % node.rpartition("|")[2])
            continue
        
        # Check if trying to reference the current scene file.
        currentSceneFile = cmds.file(query=True, sceneName=True).replace("/", os.sep)
        if currentSceneFile == assetPath:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Scene file is already open. Cannot reference a file into itself.", 
                    button=["Ok"], 
                    defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                    )
            if confirm == "Ok":
                continue
                
        # Delete the original node.
        cmds.delete(node)
        
        # Create the namespace.
        namespace = os.path.split(assetFileName)[1].partition(".")[0]
        # Reference a copy of the asset into the namespace.
        newReferencedNodes = cmds.file(assetPath, reference=True, namespace=namespace, returnNewNodes=True)
        # Find the new referenced top node.
        referencedTopGrp = ""
        refTransforms = [x for x in newReferencedNodes if cmds.nodeType(x) == "transform"]
        for refTransform in refTransforms:
            refParent = cmds.listRelatives(refTransform, parent=True, fullPath=True)
            if not refParent or not refParent[0] in refTransforms:
                referencedTopGrp = refTransform
        
        # Set the referenced top node's transformations to match the original node.
        cmds.xform(referencedTopGrp, worldSpace=True, absolute=True, translation=pos)
        cmds.setAttr("%s.r" % referencedTopGrp, rot[0], rot[1], rot[2])
        cmds.setAttr("%s.s" % referencedTopGrp, scl[0], scl[1], scl[2])
        
        # Parent the referenced top node to the original node's parent and layer.
        if topGrpLayer:
            cmds.editDisplayLayerMembers(topGrpLayer, referencedTopGrp, noRecurse=True)
        if nodeParent:
            cmds.parent(referencedTopGrp, nodeParent[0])
            
    return True
    
# end (do)
