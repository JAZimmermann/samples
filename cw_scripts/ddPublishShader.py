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
# $Date: 2014-06-18$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddPublishShader.py

DESC
    Renames shading networks, validates textures and publishes shader and screen grab 
    into selected category folder in shaderLibrary.
    Dimensions must be square, less than 2K and a power of 2.

USAGE
    (from ddShaderLibrary)
    ddPublishShader.do()
    
FUNCTIONS
    doNameShaders()
    getAssetShaderLibrary()
    getAssetTextureLibrary()
    getCategoryFolder()
    getConnectedShadingEngine()
    validateTextureFile()
    do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

# PYTHON
import os
import sys
import shutil
import imghdr
import math

# VAD
import ddConstants; reload(ddConstants)
import ddCheckForDuplicateShader; reload(ddCheckForDuplicateShader)
import ddDeleteUnknownNodes; reload(ddDeleteUnknownNodes)
import ddRemoveRequires; reload(ddRemoveRequires)


def doNameShaders(node, directory):
    '''
    Rename the shading network nodes.
    @param node: Node with connected shader.
    @param directory: Category directory. 
    '''
    textureDir = getAssetTextureLibrary()
    currentAssetDirectory = getAssetLibrary()
    dividerTypes = ["CPF", "CPO", "CPD"]
    
    divider = ""
    nodeParts = node.split("_")
    for nodePart in nodeParts:
        if nodePart in dividerTypes:
            divider = nodePart
    
    # Get shape node.
    shapeNode = cmds.listRelatives(node, shapes=True, path=True)
    if shapeNode:
        cmds.select(shapeNode, replace=True)
        cmds.refresh()
    
    # Get name for shader.
    found = False
    result = "OK"
    rootName = ""
    
    # Create a starting name for promptDialog.
    meshDescriptor = ""
    if currentAssetDirectory == ddConstants.CHAR_ASSETLIBRARY:
        meshDescriptor = node.rpartition("|")[2].rpartition("_%s" % divider)[0].partition("_")[2].partition("_")[2].replace("_", "")
    else:
        meshDescriptor = node.rpartition("|")[2].rpartition("_GEO")[0].rpartition("_")[2]
        
    if not meshDescriptor:
        meshDescriptor = node.replace("_SG", "").replace("_SHD", "").rpartition("|")[2]
    while not found and not result == "Cancel":
        result = cmds.promptDialog(
                title="Shader Namer", messageAlign="center", 
                message='Enter a name for the shader.  ', text=meshDescriptor, 
                button=["OK", "Cancel"], 
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel"
                )
        if result == "Cancel": 
            return False 
        rootName = cmds.promptDialog(query=True, text=True).rpartition("|")[2]
        
        # Check for invalid character at end of rootName
        if not ((ord(rootName[-1]) in range(97, 123)) or (ord(rootName[-1]) in range(65, 91)) or 
                (ord(rootName[-1]) in range(48, 58))):
            confirmInvalid = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Invalid character at end of name.  ", 
                    button=[" Enter a New Name ", "Cancel"], 
                    defaultButton=" Enter a New Name ", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirmInvalid == "Cancel":
                return False
        else:
            # Check for existing swatch.
            swatchPath = os.path.join(directory, "%s.ma" % rootName)
            if not os.path.isfile(swatchPath):
                found = True
            else:
                confirm = cmds.confirmDialog(
                        title="Warning", messageAlign="center", 
                        message="Swatch name already exists.  ", 
                        button=[" Enter a New Name ", "Replace", "Cancel"], 
                        defaultButton=" Enter a New Name ", cancelButton="Cancel", dismissString="Cancel"
                        )
                if confirm == "Cancel":
                    return False
                elif confirm == "Replace":
                    found = True
                    
    # Rename the shading engine.
    shadingEngine = getConnectedShadingEngine(node)
    if shadingEngine:
        try:
            shadingEngine = cmds.rename(shadingEngine, "%s_SG" % rootName)
        except:
            sys.stdout.write("--> Cannot publish read only shader %s. Skipping... \n" % shadingEngine)
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Cannot publish read only shader %s.  " % shadingEngine, 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel":
                return False
                
            return False
    else:
        sys.stdout.write("--> No shading engine found for %s. Skipping... \n" % node)
        
    # Rename the surface shader
    surfaceShader = cmds.listConnections("%s.surfaceShader" % shadingEngine)    
    if surfaceShader:
        surfaceShader = cmds.rename(surfaceShader[0], "%s_SHD" % rootName)
    else:
        sys.stdout.write("--> No surface shader found for %s. Skipping... \n" % surfaceShader)
        
    # Rename the other shading network nodes.
    historyList = cmds.listHistory(shadingEngine) or []
    fileNodes = [x for x in historyList if cmds.nodeType(x) == "file"] or []
    
    # From fileNodes, check if a similar shader has already been published.
    confirm = cmds.confirmDialog(
            title="Question", messageAlign="center", 
            message="Check if a similar shader has already been published? It might take a few minutes... ", 
            button=["  Continue With Check  ", "  Publish Without Checking  "], 
            defaultButton="  Continue With Check  ", cancelButton="  Publish Without Checking  ", 
            dismissString="  Publish Without Checking  "
            )
    if confirm == "  Continue With Check  ":
        alreadyExists = ddCheckForDuplicateShader.do(fileNodes)
        if alreadyExists == "Fail":
            return False
        if alreadyExists:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Shader resembles an already published shader: %s.  " % alreadyExists, 
                    button=["  Continue With Publish  ", "  Cancel Publish  "], 
                    defaultButton="  Continue With Publish  ", cancelButton="  Cancel Publish  ", 
                    dismissString="  Cancel Publish  "
                    )
            if confirm == "  Cancel Publish  ":
                return False    
    
    for fileNode in fileNodes:
        # Copy the file textures on disk and rename.
        fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
        cnxList = cmds.listConnections(fileNode, source=False, destination=True, plugs=True) or []
        fileNodeCnx = [x for x in cnxList if surfaceShader in x or "bumpValue" in x]
        if fileNodeCnx:
            for nodeCnx in fileNodeCnx:
                attr = nodeCnx.partition(".")[2]
                if attr in ddConstants.textureTypes.keys():
                    if not validateTextureFile(fileNode, fileTextureName, publish=True):
                        return False
                    
                    fileNode = cmds.rename(fileNode, "%s_%s_FIL" % (rootName, ddConstants.textureTypes[attr]))
                    if "bump" in nodeCnx:
                        cmds.rename(nodeCnx.partition(".")[0], "%s_%s_BMP" % (rootName, ddConstants.textureTypes[attr]))
                    placeTextureNode = cmds.listConnections(fileNode, source=True, destination=False)
                    if placeTextureNode:
                        cmds.rename(placeTextureNode[0].partition(".")[0], "%s_%s_PTN" % (rootName, ddConstants.textureTypes[attr]))
                        
                    newFileName = "%s_%s_SL.tif" % (rootName, ddConstants.textureTypes[attr])
                    newFilePath = os.path.join(textureDir, newFileName)
                    
                    if not (fileTextureName.replace("/", os.sep) == newFilePath) and not (fileTextureName == newFilePath):
                        shutil.copy(fileTextureName, newFilePath)
                        cmds.setAttr("%s.fileTextureName" % fileNode, newFilePath, type="string")
                    
    # Remove stray namespaces.
    surfaceShaderCnxList = cmds.listConnections(surfaceShader) or []
    for shaderCnx in surfaceShaderCnxList:
        if ":" in shaderCnx:
            shaderNamespace = shaderCnx.partition(":")[0]
            cmds.select(shaderCnx, replace=True)
            cmds.namespace(mv=(shaderNamespace, ":"), force=True)
    
    sys.stdout.write("Shader renamed: %s\n" % surfaceShader)
    
    return shadingEngine
    
# end (doNameShaders)


def getAssetCategory(arg=None):
    '''Return selected asset category.
    '''
    selected = cmds.optionMenu("assetCategoryMenu", query=True, select=True)
    currentAssetCategory = ddConstants.ASSET_CATEGORIES[selected-1]
    return currentAssetCategory


def getAssetLibrary(arg=None):
    '''Get selected asset category and return corresponding shader directory.
    '''
    assetCategory = getAssetCategory()
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[assetCategory]
    return currentAssetLibrary


def getAssetShaderLibrary(arg=None):
    '''Get selected asset category and return corresponding shader directory.
    '''
    assetCategory = getAssetCategory()
    currentShaderLibrary = ddConstants.SHADER_DIRECTORIES[assetCategory]
    
    return currentShaderLibrary


def getAssetTextureLibrary(arg=None):
    '''Get selected asset category and return corresponding texture directory.
    '''
    assetCategory = getAssetCategory()
    currentTextureDirectory = ddConstants.TEXTURE_DIRECTORIES[assetCategory]
    
    return currentTextureDirectory


def getCategoryFolder(arg=None):
    '''Get selected category folder and return corresponding category directory.
    '''
    currentShaderLibrary = getAssetShaderLibrary()
    category = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True)
    directory = currentShaderLibrary
    if category:
        category = category[0]
        if not (category == "-- UNFILED --"):
            directory = os.path.join(currentShaderLibrary, category)
            
    return directory


def getConnectedShadingEngine(node):
    '''Find shading engine connected to node.
    '''
    shapeNode = ""
    if cmds.nodeType(node) == "shadingEngine":
        return node
    
    if cmds.nodeType(node) == "mesh":
        shapeNode = [node]
    else:
        shapeNode = cmds.listRelatives(node, shapes=True, path=True)
    if shapeNode: 
        shadingEngines = cmds.listConnections(shapeNode[0], type="shadingEngine") or []
        shadingEngines = list(set(shadingEngines))
        if shadingEngines:
            return shadingEngines[0]
            
    return None


def validateTextureFile(fileNode, fileTextureName, publish=True):
    '''
    Check if texture file is tif format and dimensions are square, under 2K and powers of 2.
    @param fileNode: Maya file node.
    @param fileTextureName: From the file node attribute.
    @param publish: If True, stop on errors. Otherwise, just validate.
    '''
    if os.path.isfile(fileTextureName):
        # Check if file format is TIF. 
        if not imghdr.what(fileTextureName) == "tiff":
            if not publish: 
                return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" is not a ".tif" file.' % fileTextureName, 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        
        # Check if square:
        sel = om.MSelectionList()
        sel.add(fileNode)
        fileObj = om.MObject()
        sel.getDependNode(0, fileObj)
        
        im = om.MImage()
        try:
            im.readFromTextureNode(fileObj)
        except:
            sys.stdout.write('--> Unable to analyze data in %s. Verify that TIF file does NOT use ZIP compression.\n' % fileTextureName)
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Unable to analyze data in %s. \n\nVerify that TIF file does NOT use ZIP compression.\n' % fileTextureName, 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            return False
        
        utilWidth = om.MScriptUtil()
        utilWidth.createFromInt(0)
        ptrWidth = utilWidth.asUintPtr()
        utilHeight = om.MScriptUtil()
        utilHeight.createFromInt(0)
        ptrHeight = utilHeight.asUintPtr()
        
        im.getSize(ptrWidth, ptrHeight)
        width = om.MScriptUtil.getUint(ptrWidth)
        height = om.MScriptUtil.getUint(ptrHeight)
        
        # Texture dimensions must be square.
        if abs(width - height) > 0.0001:
            if not publish: 
                return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is not square.' % 
                            (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        
        # Texture dimensions must be less than 2K.
        if (width > 2048) or (height > 2048):
            if not publish: 
                return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is above the 2K (2048 x 2048) max.' % 
                            (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        
        # Texture dimensions must be power of 2.
        widthPower = math.log(width) / math.log(2)
        heightPower = math.log(height) / math.log(2)
        if not(widthPower - int(widthPower) < 0.0001) and not(heightPower - int(heightPower) < 0.0001):
            if not publish: 
                return False
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Texture file "%s" has dimensions %s x %s which is not a power of 2.' % 
                            (fileTextureName, width, height), 
                    button=["Continue","Cancel"], 
                    defaultButton="Continue", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
                
        return True
    else:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='Texture file is missing: "%s".' % fileTextureName, 
                button=["Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
        if confirm == "Cancel": 
            return False
        
# end (validateTextureFile)


def do(nodes=None):
    '''
    Publish shader attached to nodes.
    @param nodes: One or more GEO or shader nodes.
    '''
    currentShaderLibrary = getAssetShaderLibrary()

    # Swatches file storage location.
    if not os.path.isdir(currentShaderLibrary):
        raise Exception("Directory %s does not exist" % currentShaderLibrary)
    
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
    # If still no nodes...
    if not nodes:
        sys.stdout.write("Select a mesh with an attached shader to be published.\n")
        
    if not isinstance(nodes, list):
        nodes = [nodes]
    
    for node in nodes:
        currentNode = node
        
        # Check if referenced.
        if cmds.referenceQuery(node, isNodeReferenced=True):
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Cannot publish a referenced shader. Try importing from reference.', 
                    button=["Ok"], 
                    defaultButton="Ok", cancelButton="Ok", dismissString="Ok")
            if confirm == "Ok":
                return
        
        # If node is not a mesh, look for a shading engine.
        if not cmds.listRelatives(currentNode, shapes=True):
            # Check if node is a GRP with one mesh below.
            children = cmds.listRelatives(currentNode, children=True)
            if children:
                if len(children) == 1 and cmds.listRelatives(children[0], shapes=True):
                    currentNode = children[0]
                else:
                    confirm = cmds.confirmDialog(
                                title="Warning", messageAlign="center", message='Unable to determine which shader to publish.', 
                                button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                                )
                    if confirm == "Ok":
                        return
            else:
                # Look for a connected shading engine.
                shadingEngines = [x for x in (cmds.listHistory(currentNode, future=True) or []) if cmds.nodeType(x) == "shadingEngine"]
                if shadingEngines:
                    currentNode = shadingEngines[0]
                else:
                    confirm = cmds.confirmDialog(
                            title="Warning", messageAlign="center", message='Unable to find a shader to publish.', 
                            button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                            )
                    if confirm == "Ok":
                        return
        
        # Get the shader category.
        directory = getCategoryFolder()
        shadingEngine = doNameShaders(node=currentNode, directory=directory)
        if not shadingEngine:
            continue
            
        rootName = shadingEngine.replace("_SG", "")
        
        # Create swatch.
        swatch = cmds.polyPlane(name="%s_Swatch" % rootName, width=1, height=1, sx=1, sy=1, ax=[0,0,1], ch=0)
        swatchShape = cmds.listRelatives(swatch, shapes=True, path=True)
        cmds.sets(swatchShape, forceElement=shadingEngine)
        
        imagePath = os.path.join(directory, "%s.png" % rootName)
        
        # Create snapshot.
        screenGrabCam = cmds.camera(centerOfInterest=378.926)
        cmds.setAttr("%s.tz" % screenGrabCam[0], 378.926)
        cmds.setAttr("%s.orthographic" % screenGrabCam[1], 1)

        cmds.select(swatch, replace=True)
        
        currentPanel = "modelPanel4"
        if not cmds.modelEditor(currentPanel, exists=True):
            currentPanel = cmds.getPanel(withFocus=True)
    
        mel.eval('enableIsolateSelect %s true;' % currentPanel)
        cmds.isolateSelect(currentPanel, state=1)
        mel.eval('lookThroughModelPanel %s %s' % (screenGrabCam[0], currentPanel))
        
        cmds.viewFit()
        cmds.setAttr("%s.orthographicWidth" % screenGrabCam[1], 1)
        cmds.select(clear=True)
        gridValue = cmds.modelEditor(currentPanel, query=True, grid=True)
        cmds.modelEditor(
                currentPanel, edit=True, displayAppearance="smoothShaded", 
                displayTextures=True, displayLights="default", grid=False
                )
        cmds.playblast(
                frame=1, format="image", completeFilename=imagePath, clearCache=True, viewer=False, 
                showOrnaments=False, compression="png", quality=40, percent=100, widthHeight=[144,144]
                )
        cmds.isolateSelect(currentPanel, state=0)
        cmds.modelEditor(currentPanel, edit=True, grid=gridValue)
        mel.eval('lookThroughModelPanel persp %s' % currentPanel)
        cmds.delete(screenGrabCam[0])
        sys.stdout.write("Screen grab of swatch saved to: %s\n" % imagePath)
        
        # Delete unknown nodes (mental ray).
        ddDeleteUnknownNodes.do()
        
        # Export swatch file.
        swatchPath = os.path.join(directory, "%s.ma" % rootName)
        cmds.select(swatch, replace=True)
        exportedFile = cmds.file(swatchPath, type="mayaAscii", exportSelected=True, force=True)
        ddRemoveRequires.do(path=swatchPath)
        
        if exportedFile:
            cmds.delete(swatch)
            
# end (do)