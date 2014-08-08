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
# $Date: 2014-06-13$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddCheckTexturePublished.py

DESC
    Checks if connected textures are in Shader Library.

USAGE
    ddCheckTexturePublished.do()
    
FUNCTIONS
    doCheckAllTexturesPublished()
    doCheckTexturePublished()
    getConnectedShadingEngine()
    getTopGrpOfNode()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import os
import sys

# constants
import ddConstants; reload(ddConstants)


def doCheckAllTexturesPublished(assetCategory="environments"):
    '''Checks all shading engines in scene file.
    '''
    currentShaderLibrary = ddConstants.SHADER_DIRECTORIES[assetCategory]
    currentTextureLibrary = ddConstants.TEXTURE_DIRECTORIES[assetCategory]
    
    categories = [x for x in (os.listdir(currentShaderLibrary) or []) if os.path.isdir(os.path.join(currentShaderLibrary, x)) 
               and not x.startswith(".")]
               
    swatches = [x.replace(".png", "") for x in os.listdir(currentShaderLibrary) if x.endswith(".png")]
    
    for category in categories:
        categorySwatches = [x.replace(".png", "") for x in os.listdir(os.path.join(currentShaderLibrary, category)) if x.endswith(".png")]
        if categorySwatches:
            swatches.extend(categorySwatches)
    
    shadingEngines = [x for x in (cmds.ls(type="shadingEngine") or []) if not x in ['initialParticleSE', 'initialShadingGroup']]
    unpublishedShadingEngines = list()
    referencedShaders = False
    
    for shadingEngine in shadingEngines:
        shadingEngineName = shadingEngine.split("_")[0]
        if cmds.referenceQuery(shadingEngine, isNodeReferenced=True):
            referencedShaders = True
            continue
        if not shadingEngine.endswith("_SG"):
            unpublishedShadingEngines.append(shadingEngine)
            continue
        if not shadingEngine.replace("_SG", "") in swatches:
            unpublishedShadingEngines.append(shadingEngine)
            continue
        surfaceShader = cmds.listConnections("%s.surfaceShader" % shadingEngine)
        if surfaceShader:
            if not surfaceShader[0].endswith("_SHD") and not surfaceShader[0].startswith(shadingEngineName):
                unpublishedShadingEngines.append(shadingEngine)
                continue
                
        fileNodes = [x for x in (cmds.listHistory(shadingEngine) or []) if cmds.nodeType(x) == "file"]
        for fileNode in fileNodes:
            if not fileNode.endswith("_FIL") and not fileNode.startswith(shadingEngineName):
                unpublishedShadingEngines.append(shadingEngine)
                continue
            fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
            if fileTextureName:
                if not (fileTextureName.replace("/", os.sep).startswith(currentTextureLibrary) or fileTextureName.startswith(currentTextureLibrary)):
                    unpublishedShadingEngines.append(shadingEngine)
                    continue
    
    problemMeshes = list()
    for unpublished in unpublishedShadingEngines:
        meshList = [x for x in cmds.listHistory(unpublished) if cmds.nodeType(x) == "mesh"]
        for mesh in meshList:
            meshParent = cmds.listRelatives(mesh, parent=True, fullPath=True)
            if meshParent:
                problemMeshes.append(meshParent[0])
        
    problemMeshes = list(set(problemMeshes))
    problemGroups = getTopGrpOfNode(problemMeshes)
    problemGroups = list(set(problemGroups))
    
    if referencedShaders:
        sys.stdout.write("Skipping referenced shaders...\n")
    
    return problemGroups
    
# end (doCheckAllTexturesPublished)


def doCheckTexturePublished(node, verbose=False, assetCategory="environments"):
    '''Checks shading engine attached to node.'''
    currentShaderLibrary = ddConstants.SHADER_DIRECTORIES[assetCategory]
    currentTextureLibrary = ddConstants.TEXTURE_DIRECTORIES[assetCategory]
    
    categories = [x for x in (os.listdir(currentShaderLibrary) or []) if os.path.isdir(os.path.join(currentShaderLibrary, x)) 
               and not x.startswith(".")]
    
    swatches = [x.replace(".png", "") for x in os.listdir(currentShaderLibrary) if x.endswith(".png")]
    
    for category in categories:
        categorySwatches = [x.replace(".png", "") for x in os.listdir(os.path.join(currentShaderLibrary, category)) if x.endswith(".png")]
        if categorySwatches:
            swatches.extend(categorySwatches)
    
    meshNodes = [x for x in (cmds.listRelatives(node, path=True, allDescendents=True) or []) if cmds.nodeType(x) == "mesh"]
    for meshNode in meshNodes:
        meshParent = cmds.listRelatives(meshNode, parent=True, path=True)[0]
        shadingEngine = getConnectedShadingEngine(meshParent)
        shadingEngineName = shadingEngine.split("_")[0]
        if not shadingEngine:
            sys.stdout.write('No shader attached to %s.\n' % meshParent.rpartition("|")[2].rpartition(":")[2])
            return False
        if not shadingEngine.endswith("_SG"):
            if verbose:
                sys.stdout.write('Shading engine attached to %s is not named correctly. Import or re-import from Shader Library.\n' % meshParent.rpartition("|")[2].rpartition(":")[2])
            return False
        if not shadingEngine.replace("_SG", "") in swatches:
            if verbose:
                sys.stdout.write("Shader attached to %s is not in the Shader Library.\n" % meshParent.rpartition("|")[2].rpartition(":")[2])
            return False
        surfaceShader = cmds.listConnections("%s.surfaceShader" % shadingEngine)
        if surfaceShader:
            if not surfaceShader[0].endswith("_SHD") and not surfaceShader[0].startswith(shadingEngineName):
                if verbose:
                    sys.stdout.write('Shader attached to %s is not named correctly. Import or re-import from Shader Library.\n' % meshParent.rpartition("|")[2].rpartition(":")[2])
                return False
                
        fileNodes = [x for x in (cmds.listHistory(shadingEngine) or []) if cmds.nodeType(x) == "file"]
        for fileNode in fileNodes:
            if not fileNode.endswith("_FIL") and not fileNode.startswith(shadingEngineName):
                if verbose:
                    sys.stdout.write('Shader attached to %s has incorrectly named nodes. Import or re-import from Shader Library.\n' % meshParent.rpartition("|")[2].rpartition(":")[2])
                return False
            fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
            if fileTextureName:
                if not (fileTextureName.replace("/", os.sep).startswith(currentTextureLibrary) or fileTextureName.startswith(currentTextureLibrary)):
                    if verbose:
                        sys.stdout.write('Tif file %s attached to %s is not in the "tex" directory. Import or re-import the shader from Shader Library.\n' % (fileTextureName, meshParent.rpartition("|")[2].rpartition(":")[2]))
                    return False
                    
    return True
    
# end (doCheckTexturePublished)


def getConnectedShadingEngine(node):
    '''Get connect shading engine.
    '''
    shapeNode = cmds.listRelatives(node, shapes=True, path=True)
    if shapeNode: 
        shadingEngines = cmds.listConnections(shapeNode[0], type="shadingEngine") or []
        shadingEngines = list(set(shadingEngines))
        if shadingEngines:
            return shadingEngines[0]
    return None
    
# end (getConnectedShadingEngine)


def getTopGrpOfNode(nodes):
    '''Get top group of node.
    '''
    nodeList = list()
    for node in nodes:
        searchPath = node
        found = False
        while not found and searchPath:
            currentLevel = searchPath.rpartition("|")[2]
            if "GRP" in currentLevel:
                nodeList.append(searchPath)
                found = True
                searchPath = None
            else:
                children = cmds.listRelatives(searchPath, shapes=True)
                if children:
                    searchPath = searchPath.rpartition("|")[0]
                else:
                    found = True
                    searchPath = None     
            
    nodeList = list(set(nodeList))
    
    return nodeList
    
# end (getTopGrpOfNode)


def do(nodes=None, verbose=False, confirm=True, assetCategory="environments"):
    
    # Nodes are top group nodes
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
    
    nodesWithUnpublishedShaders = list()
    for node in nodes:
        if node.rpartition("|")[2].startswith("char_"):
            assetCategory = "characters"
        else:
            assetCategory = "environments"
        published = doCheckTexturePublished(node=node, verbose=verbose, assetCategory=assetCategory)
        if not published:
            nodesWithUnpublishedShaders.append(node)
    
    if nodesWithUnpublishedShaders:
        nodesStr = ""
        for item in nodesWithUnpublishedShaders:
            nodesStr += "%s, " % item
            
        if not verbose and confirm:
            confirm = cmds.confirmDialog(title="Warning", message="The following nodes have unpublished shaders: %s" % nodesStr[:-2], button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok", messageAlign="center")
        return False
    
    return True
    
# end (do)
