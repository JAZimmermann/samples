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
    ddSwapForReference.py

DESC
    Swaps selected group or reference for another reference.
    
USAGE
    ddSwapForReference.do()
    
FUNCTIONS
    doSwapForReference()
    do()
    
'''


# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import sys

# VAD
import ddConstants; reload(ddConstants)


def doSwapForReference(node, startingDirectory=ddConstants.ASSETLIBRARY, filename=None):
    '''
    Swaps selected group or reference for another reference.
    @param node: Node or GRP node to be swapped out.
    @param startingDirectory: Base asset library directory (optional).
    @param filename: Can pass filename directly to bypass file browser dialog (optional).
    '''
    # Get the node's parent. 
    nodeParent = cmds.listRelatives(node, parent=True, path=True)
    
    # Get the node's layer.
    topGrpLayer = None
    cnxList = [x for x in (cmds.listConnections(node, source=True, destination=False) or []) if cmds.nodeType(x) == "displayLayer"]
    if cnxList:
        topGrpLayer = cnxList[0]
    
    # Get the node's transformations.
    pos = cmds.xform(node, query=True, worldSpace=True, absolute=True, rotatePivot=True)
    rot = cmds.getAttr("%s.r" % node)[0]
    scl = cmds.getAttr("%s.s" % node)[0]
    
    # Select the node for the user to see.
    cmds.select(node, replace=True)
    cmds.refresh()
    cmds.namespace(setNamespace=":")
    
    # Get new reference file using file browser dialog.
    if not filename:
        filename = cmds.fileDialog2(
                fileMode=1, caption="Swap For Reference", 
                startingDirectory=startingDirectory, okCaption="Reference"
                )
        if not filename: 
            return None, startingDirectory, None
        filename = filename[0]
    
    # Check if file exists.
    if not os.path.isfile(filename):
        sys.stdout.write("File %s not found.\n" % filename)
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='File not found "%s".' % filename, 
                button=["Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel")
        return None, startingDirectory, None
    
    # Create the namespace.
    namespace = filename.rpartition("/")[2].rpartition("\\")[2].rpartition(".")[0]
    
    # Update the startingDirectory for the next pass.
    startingDirectory = filename.rpartition("/")[0]
    
    # Remove old reference or just delete the node.
    if cmds.referenceQuery(node, isNodeReferenced=True):
        referencedPath = cmds.referenceQuery(node, filename=True)
        cmds.file(referencedPath, removeReference=True, mergeNamespaceWithRoot=True)
    else:
        cmds.delete(node)
        
    # Load new reference under the new namespace.
    newReferencedNodes = cmds.file(filename, reference=True, namespace=namespace, returnNewNodes=True)
    
    # Find the top group of the referenced file.
    referencedTopGrp = ""
    refTransforms = [x for x in newReferencedNodes if cmds.nodeType(x) == "transform"]
    for refTransform in refTransforms:
        refParent = cmds.listRelatives(refTransform, parent=True, fullPath=True)
        if not refParent or not refParent[0] in refTransforms:
            referencedTopGrp = refTransform
            
    # Position new top group using node's transformations. 
    try:
        cmds.xform(referencedTopGrp, worldSpace=True, absolute=True, translation=pos)
        cmds.setAttr("%s.r" % referencedTopGrp, rot[0], rot[1], rot[2])
        cmds.setAttr("%s.s" % referencedTopGrp, scl[0], scl[1], scl[2])
    except:
        sys.stdout.write("Unable to reposition new node %s due to locked channels.\n" % referencedTopGrp)
        
    # Parent new top group to node's parent and node's layer.
    if topGrpLayer:
        cmds.editDisplayLayerMembers(topGrpLayer, referencedTopGrp, noRecurse=True)
    if nodeParent:
        try:
            referencedTopGrp = cmds.parent(referencedTopGrp, nodeParent[0])[0]
        except:
            sys.stdout.write("Unable to reparent new node %s.\n" % referencedTopGrp)
    
    # Return new top group and updated starting directory.
    return referencedTopGrp, startingDirectory, filename
    
# end (do)


def do(nodes=None, filename=None, startingDirectory=ddConstants.ASSETLIBRARY):
    '''
    Swaps selected group or reference for another reference.
    @param nodes: One or more GEO or GRP nodes (optional).
    @param filename: Can pass filename directly to bypass file browser dialog (optional)
    @param startingDirectory: Base asset library directory (optional).
    '''
    nodeList = list()
    newNodes = list()
    cmds.namespace(setNamespace=":")
    
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
    
    for node in nodes:
        if not cmds.objExists(node):
            continue
            
        # Use the top GRP node for swap if there is one.
        currentNode = node
        nodeParent = ""
        # Get the full node name and look for a part containing "GRP".
        fullNode = mel.eval('longNameOf("%s")' % currentNode)
        while fullNode:
            nodeParent, divider, subNode = fullNode.rpartition("|")
            if "GRP" in subNode:
                # A GRP node has been found, use it instead of the node.
                currentNode = fullNode
                fullNode = ""
            else:
                fullNode = nodeParent
        
        nodeParts = node.rpartition("|")[2].split("_")
        currentNodeParts = currentNode.rpartition("|")[2].split("_")
        if nodeParts[0] == currentNodeParts[0]:
            nodeList.append(currentNode)
        else:
            nodeList.append(node)
    
    nodeList = list(set(nodeList))
    
    # Swap for each node.
    for node in nodeList:
        print node
        newNode, startingDirectory, filename = doSwapForReference(node, startingDirectory, filename)
        if newNode:
            newNodes.append(newNode)
    
    # Select the swapped nodes for the user.
    if newNodes:
        cmds.select(newNodes, replace=True)
        
    return newNodes
    
# end (do)
