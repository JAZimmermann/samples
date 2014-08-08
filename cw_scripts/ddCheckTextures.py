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
    ddCheckTextures.py

DESC
    Checks if textures files are saved in assetLibrary and file format is ".tif".
    Names texture files to match GEO.

USAGE
    ddCheckTextures.do()
    
FUNCTIONS
    validateTextureFile()
    do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.OpenMaya as om

# PYTHON
import os
import sys
import shutil
import imghdr
import math

# VAD
import ddConstants; reload(ddConstants)
import ddCheckNames; reload(ddCheckNames)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)


def validateTextureFile(fileNode, fileTextureName, publish=False):
    '''
    Check if texture file is tif format and dimensions are square, under 2K and powers of 2.
    @param fileNode: Maya file node.
    @param fileTextureName: From the file node attribute.
    @param publish: If True, stop on errors. Otherwise, just validate.
    '''
    validTextures = True
    if os.path.isfile(fileTextureName):
        # Check if file format is ".tif"
        if not imghdr.what(fileTextureName) == "tiff":
            validTextures = False
            #if not publish: 
            #    return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" is not a ".tif" file. ' % fileTextureName, 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False # Prevent asset export
        
        # Check if square:
        sel = om.MSelectionList()
        sel.add(fileNode)
        fileObj = om.MObject()
        sel.getDependNode(0, fileObj)
        
        im = om.MImage()
        im.readFromTextureNode(fileObj)
        
        utilWidth = om.MScriptUtil()
        utilWidth.createFromInt(0)
        ptrWidth = utilWidth.asUintPtr()
        utilHeight = om.MScriptUtil()
        utilHeight.createFromInt(0)
        ptrHeight = utilHeight.asUintPtr()
        
        im.getSize(ptrWidth, ptrHeight)
        width = om.MScriptUtil.getUint(ptrWidth)
        height = om.MScriptUtil.getUint(ptrHeight)
        
        # Texture dimensions must be square
        if abs(width - height) > 0.0001:
            validTextures = False
            #if not publish: 
            #    return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is not square. ' % (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False # Prevent asset export
        
        
        # Texture dimensions must be less than 2K
        if (width > 2048) or (height > 2048):
            validTextures = False
            #if not publish: 
            #    return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is above the 2K (2048 x 2048) max. ' % (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False # Prevent asset export
        
        # Texture dimensions must be power of 2
        widthPower = math.log(width) / math.log(2)
        heightPower = math.log(height) / math.log(2)
        if not(widthPower - int(widthPower) < 0.0001) and not(heightPower - int(heightPower) < 0.0001):
            validTextures = False
            #if not publish: 
            #    return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is not a power of 2. ' % (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False # Prevent asset export
    return validTextures
    
# end (validateTextureFile)


def do(node=None, override=False, publish=False):
    '''Checks if textures files are saved in assetLibrary and file format is ".tif".
       Names texture files to match GEO.
    '''
    if not node:
        selection = cmds.ls(selection=True, long=True)
        if selection:
            node = selection[0]
        else: 
            return False, override
            
    if publish:
        invalidNode = ddCheckNames.do(node)
        if invalidNode:
            sys.stdout.write("Cannot check textures. Names are not valid for node %s. Skipping... \n" % node.rpartition("|")[2])    
            return False, override
            
    if cmds.referenceQuery(node, isNodeReferenced=True):
        sys.stdout.write("--> Unable to check textures of referenced node %s. Skipping... \n" % node.rpartition("|")[2])
        return False, override
    
    currentNode = node
    if publish:
        newNode = ddRemoveNamespaces.do(node)
        if newNode:
            currentNode = newNode[0]
            
    # Texture file storage location
    textureDir = os.path.join(ddConstants.ASSETLIBRARY, "tex", "tif")
    textureDir = os.path.normpath(textureDir)
    if not os.path.isdir(textureDir):
        raise Exception("Directory %s does not exist" % textureDir)
        
    # Get list of child mesh nodes under GRP node
    meshList = cmds.listRelatives(currentNode, path=True, allDescendents=True, type="mesh") or []
    version = currentNode.partition("_GRP_")[2].partition("_")[0]
    overwriteOverride = False
    skipCopy = False
    skipOverwrite = False
    publishedOverride = False
    
    allShadingEngines = list()
    for shapeNode in meshList:
        # Find shaders
        shapeTransform = cmds.listRelatives(shapeNode, parent=True)[0]
        shapeTransformPath = cmds.listRelatives(shapeNode, path=True, parent=True)[0]
        shadingEngines = cmds.listConnections(shapeNode, type="shadingEngine") or []
        shadingEngines = list(set(shadingEngines))
        if shadingEngines:
            allShadingEngines.extend(shadingEngines)
    
    allShadingEngines = list(set(allShadingEngines))
    
    for shadingEngine in allShadingEngines:
        cnxList = [x for x in (cmds.listConnections(shadingEngine) or []) if cmds.nodeType(x) == "transform"]
        cnxList = list(set(cnxList))
        cnxList.sort()
        rootName = cnxList[0].rpartition("|")[2].rpartition("_")[0]
        currentShadingEngine = shadingEngine
        connectedMeshes = [x for x in (cmds.listConnections(currentShadingEngine) or []) if cmds.listRelatives(x, shapes=True)]
        connectedMeshes = list(set(connectedMeshes))
        if publish:
            if len(connectedMeshes) > 1:
                if rootName:
                    rootName = rootName.replace("_GEO", "")
                    while ord(rootName[-1]) in range(49, 58):
                        rootName = rootName[:-1]
                    while ord(rootName[-1]) in range(65, 91):
                        rootName = rootName[:-1]
                    rootName = "%s_GEO" % rootName
        
        # Find connected file nodes
        historyList = cmds.listHistory(currentShadingEngine) or []
        fileNodes = [x for x in historyList if cmds.nodeType(x) == "file"] or []
        for fileNode in fileNodes:
            fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
            newFileName = ""
            newFilePath = ""
            
            # Determine shader attribute file node is connected to
            surfaceShader = cmds.listConnections("%s.surfaceShader" % currentShadingEngine)
            if surfaceShader:
                surfaceShader = surfaceShader[0]
                cnxList = cmds.listConnections(fileNode, source=False, destination=True, plugs=True) or []
                fileNodeCnx = [x for x in cnxList if surfaceShader in x or "bumpValue" in x]
                if fileNodeCnx:
                    for nodeCnx in fileNodeCnx:
                        attr = nodeCnx.partition(".")[2]
                        if attr in ddConstants.textureTypes.keys():
                            if not validateTextureFile(fileNode, fileTextureName, publish):
                                return False, override
                            
                            # Create texture name to match GEO                                
                            newFileName = "%s_%s.tif" % (rootName.replace("GEO", ddConstants.textureTypes[attr]), version)
                            newFilePath = os.path.join(textureDir, newFileName)
                            
                            if publish:
                                fileNode = cmds.rename(fileNode, "%s_FIL" % rootName.replace("GEO", ddConstants.textureTypes[attr]))
                                if "bump" in nodeCnx:
                                    cmds.rename(nodeCnx.partition(".")[0], "%s_BMP" % rootName.replace("GEO", ddConstants.textureTypes[attr]))
                                placeTextureNode = cmds.listConnections(fileNode, source=True, destination=False)
                                if placeTextureNode:
                                    cmds.rename(placeTextureNode[0].partition(".")[0], "%s_PTN" % rootName.replace("GEO", ddConstants.textureTypes[attr]))
                                    
                else:
                    sys.stdout.write("--- Skipping %s. Not connected to color, specularColor or normalCamera. \n" % fileTextureName)
                    
                if publish:
                    # Rename nodes
                    currentShadingEngine = cmds.rename(currentShadingEngine, rootName.replace("GEO", "SG"))
                    surfaceShader = cmds.rename(surfaceShader, rootName.replace("GEO", "SHD"))
                    
                    # Remove stray namespaces
                    surfaceShaderCnxList = cmds.listConnections(surfaceShader) or []
                    for shaderCnx in surfaceShaderCnxList:
                        if ":" in shaderCnx:
                            shaderNamespace = shaderCnx.partition(":")[0]
                            try:
                                cmds.select(shaderCnx, replace=True)
                                cmds.namespace(mv=(shaderNamespace, ":"), force=True)
                            except:
                                pass
                                
            # Check if file saved in assetLibrary
            if not newFilePath == "" and publish:
                confirm = "Copy to AssetLibrary"
                confirmOverwrite = "Overwrite Existing"
                
                # New section
                if fileTextureName.replace("/", os.sep).startswith(ddConstants.ASSETLIBRARY):
                    if not publishedOverride:
                        confirmOverwrite = cmds.confirmDialog(
                                title="Warning", messageAlign="center", 
                                message='Texture file "%s" already exists in the assetLibrary. ' % fileTextureName, 
                                button=["Ok", "Ok to All", "Cancel"], 
                                defaultButton="Skip", cancelButton="Cancel", dismissString="Cancel"
                                )
                        if confirmOverwrite == "Cancel":
                            return False, override
                        elif confirmOverwrite == "Ok to All":
                            publishedOverride = True
                            skipOverwrite = True
                    continue
                # End of new section
                
                if os.path.isfile(newFilePath):
                    if not overwriteOverride:
                        confirmOverwrite = cmds.confirmDialog(
                                title="Warning", messageAlign="center", 
                                message='Texture file "%s" already exists in the assetLibrary. ' % newFileName, 
                                button=["Overwrite Existing", "Overwrite All", "Skip", "Skip All", "Cancel"], 
                                defaultButton="Overwrite Existing", cancelButton="Cancel", dismissString="Cancel"
                                )
                        if confirmOverwrite == "Cancel":
                            return False, override
                        elif confirmOverwrite == "Overwrite All":
                            overwriteOverride = True
                        elif confirmOverwrite == "Skip All":
                            overwriteOverride = True
                            skipOverwrite = True
                elif not override:
                    confirm = cmds.confirmDialog(
                            title="Warning", messageAlign="center", 
                            message='Texture file "%s" is not in the assetLibrary. ' % newFileName, 
                            button=["Copy to AssetLibrary", "Copy all to AssetLibrary", "Skip", "Skip All", "Cancel"], 
                            defaultButton="Copy to assetLibrary", cancelButton="Cancel", dismissString="Cancel"
                            )
                
                if confirm == "Cancel": 
                    return False, override # Prevent asset export
                elif confirm == "Copy all to AssetLibrary":
                    override = True
                elif confirm == "Skip All":
                    override = True
                    skipCopy = True
                
                if not skipOverwrite and not skipCopy:
                    if confirm == "Copy to AssetLibrary" or confirm == "Copy all to AssetLibrary":
                        if os.path.isfile(fileTextureName):
                            if not fileTextureName.replace("/", os.sep) == newFilePath:
                                shutil.copy(fileTextureName, newFilePath)
                                cmds.setAttr("%s.fileTextureName" % fileNode, newFilePath, type="string")
                        else:
                            confirm = cmds.confirmDialog(
                                    title="Warning", messageAlign="center", 
                                    message='Original texture file "%s" does not exist. ' % fileTextureName, 
                                    button=["Continue","Cancel"], 
                                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                                    )
                            if confirm == "Cancel": 
                                return False, override # Prevent asset export
                                
    # Allow asset export
    return True, override
    
# end (do)
