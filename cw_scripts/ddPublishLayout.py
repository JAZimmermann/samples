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
ddPublishLayout.py

Checks scene file for the following: 
    - Pivot offsets.
    - Naming

FUNCTIONS
    doAddGrpMetadata()
    doAddGrpToNodeNames()
    doCleanScene()
    doCleanUpShadingEngines()
    doClearDisplay()
    doCreateNullHierarchy()
    doDisplayList()
    doFixAllDuplicateNodeNames()
    doFixDuplicateNodeNames()
    doFixInstanceNumbers()
    doFixInvalidNames()
    doFixInvalidPivots()
    doFixRefEdits()
    doFixVertexEdits()
    doFixWaitCursor()
    doGetDuplicateNodeNames()
    doGetInvalidNamesList()
    doGetInvalidTexturesList()
    doGetNodesWithRefEdits()
    doGetNodesWithVertexEdits()
    doGetNonReferencedNodes()
    doGetPivotOffsetsList()
    doGetPublishedAssets()
    doGetReferencedNodes()
    doGetUnpublishedAssets()
    doImportAllFromRef()
    doOptimizeAndClean()
    doPublishScene()
    doRefreshDisplay()
    doRemoveReferenceEdits()
    doRemoveVertexEdits()
    doReplaceAllWithReferences()
    doResetInstanceNumber()
    doSelectItems()
    getSelectedItems()
    getTopGroups()
    getTopGrpOfNode()
    scFixInvalidNames()
    scCheckTextures()
    scImportFromReference()
    scRemoveNamespaces()
    scRemoveReferenceEdits()
    scRemoveVertexEdits()
    scReplaceWithReference()
    scResetGeoMetadata()
    scSwapForReference()
    showPublishLayoutHelp()
    do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import sys
from functools import partial

# VAD
import ddConstants; reload(ddConstants)
import ddAddGeoMetadata; reload(ddAddGeoMetadata)
import ddAddGrpMetadata; reload(ddAddGrpMetadata)
import ddAssetNamer; reload(ddAssetNamer)
import ddCheckFileForDuplicateNames; reload(ddCheckFileForDuplicateNames)
import ddCheckGeoInstanceNumber; reload(ddCheckGeoInstanceNumber)
import ddCheckNames; reload(ddCheckNames)
import ddCheckPivotOffsets; reload(ddCheckPivotOffsets)
import ddCheckTexturePublished; reload(ddCheckTexturePublished)
import ddCheckTextures; reload(ddCheckTextures)
import ddCreateReference; reload(ddCreateReference)
import ddDeleteRefObject; reload(ddDeleteRefObject)
import ddDeleteUnknownNodes; reload(ddDeleteUnknownNodes)
import ddDuplicateRefObject; reload(ddDuplicateRefObject)
import ddExportAssets; reload(ddExportAssets)
import ddImportFromReference; reload(ddImportFromReference)
import ddLockGeoTransforms; reload(ddLockGeoTransforms)
import ddRemoveFromLayers; reload(ddRemoveFromLayers)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddRemovePivotOffsets; reload(ddRemovePivotOffsets)
import ddRemoveRequires; reload(ddRemoveRequires)
import ddReplaceWithReference; reload(ddReplaceWithReference)
import ddResetGeoMetadata; reload(ddResetGeoMetadata)
import ddScreenGrab; reload(ddScreenGrab)
import ddSwapForReference; reload(ddSwapForReference)
import ddTransferTransformsFromGeo; reload(ddTransferTransformsFromGeo)
import ddUnlockGeoTransforms; reload(ddUnlockGeoTransforms)
import edFindVertTransforms; reload(edFindVertTransforms)


def doAddGrpMetadata(arg=None):
    '''Button: Add Metadata to GRP Nodes.
    '''
    cmds.undoInfo(openChunk=True)
    ddAddGrpMetadata.do()
    cmds.undoInfo(closeChunk=True)
    sys.stdout.write("Metadata added to GRP nodes.\n")

# end (doAddGrpMetadata)


def doAddGrpToNodeNames(arg=None):
    '''Button: Add GRP to Node Names.
    '''
    sys.stdout.write('Adding "GRP" to node names... \n')
    cmds.refresh()
    
    # Get all top groups.
    topGrps = getTopGroups()
    parentGrps = list()
    
    # Get the parent groups.
    for topGrp in topGrps:
        currentGrp = topGrp
        done = False
        while not done:
            parentGrp = cmds.listRelatives(currentGrp, parent=True, path=True)
            if not parentGrp:
                done = True
            else:
                parentGrp = parentGrp[0]
                if parentGrp.endswith("_master"):
                    done = True
                else:
                    parentGrps.append(parentGrp)
                    currentGrp = parentGrp
                    
    parentGrps = list(set(parentGrps))
    
    # Sort by nesting level
    sortedGrps = list()
    for parentGrp in parentGrps:
        tokens = parentGrp.split("|")
        sortedGrps.append("%s___%s" % (len(tokens), parentGrp))
    sortedGrps.sort(reverse=True)
    
    # Rename duplicate groups and add "GRP"
    for parentGrpStr in sortedGrps:
        parentGrp = parentGrpStr.rpartition("___")[2]
        newNodeName = parentGrp.rpartition("|")[2]
        selection = cmds.ls("*|%s" % newNodeName) or []
        instanceNumber = 1
        while len(selection) > 1:
            newNodeName = "%s_%s_GRP" % (newNodeName.replace("_GRP", "").replace("GRP", "").replace("_group", ""), instanceNumber)
            instanceNumber += 1
            selection = cmds.ls("*|%s" % newNodeName)
        
        newNodeName = newNodeName.replace("_GRP", "").replace("GRP", "").replace("_group", "")
        if cmds.objExists(parentGrp):
            cmds.rename(parentGrp, "%s_GRP" % newNodeName)
        sys.stdout.write('Renamed "%s" to "%s_GRP".\n' % (parentGrp, newNodeName))
        
    sys.stdout.write('Finished adding "GRP" to node names... \n')

# end (doAddGrpToNodeNames)


def doCleanScene(arg=None):
    '''
    Button: Clean Scene.
    Runs through buttons on right of interface.
    '''
    # Confirm that user has already saved file before beginning.
    confirm = cmds.confirmDialog(
            title="Warning", messageAlign="center", message='Save file before continuing.', 
            button=["  Already Saved  ", "  Stop and Save  "], 
            defaultButton="Ok", cancelButton="  Stop and Save  ", dismissString="Ok"
            )
    if confirm == "  Stop and Save  ": 
        return
    
    try:
        mel.eval('DisplayWireframe;')
        mel.eval('setRendererInModelPanel base_OpenGL_Renderer modelPanel4;')
    except:
        pass
        
    # Check for unpublished assets.
    unpublishedAssets = doGetUnpublishedAssets()
    if unpublishedAssets:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are unpublished assets in the scene file.', 
                button=["Continue", "Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
        if confirm == "Cancel": 
            return
    
    # Check for nodes with reference edits.
    nodesWithRefEdits = doGetNodesWithRefEdits()
    if nodesWithRefEdits:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are nodes with reference edits in the scene file.', 
                button=["Fix", "Cancel"], 
                defaultButton="Fix", cancelButton="Cancel", dismissString="Cancel"
                )
        if confirm == "Cancel": 
            return
        else:
            doRemoveReferenceEdits(nodesWithRefEdits)
    
    # Import all from reference.
    doImportAllFromRef()
    if doGetReferencedNodes():
        doImportAllFromRef()
    
    # Show invalid names.
    invalidNamesList = doGetInvalidNamesList()
    if invalidNamesList:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are nodes with invalid names.', 
                button=["Fix", "Cancel"], 
                defaultButton="Fix", cancelButton="Cancel", dismissString="Cancel"
                )
        if confirm == "Cancel": 
            return
        else:
            doFixInvalidNames()
    
    # Show invalid textures.
    invalid_textures = doGetInvalidTexturesList()
    if invalid_textures:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are invalid textures.',
                button=[" Ignore and Continue ", "Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
        if confirm == "Cancel": 
            return
    
    # Check for pivot offsets.
    nodesWithPivotOffsets = doGetPivotOffsetsList()
    if nodesWithPivotOffsets:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are nodes with pivot offsets in the scene file. Remove all pivot offsets?', 
                button=["Ok", "Cancel"], 
                defaultButton="Ok", cancelButton="Cancel", dismissString="Ok"
                )
        if confirm == "Cancel": 
            return
        else:
            valid = ddResetGeoMetadata.do(nodesWithPivotOffsets)
            if not valid:
                confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Unable to remove pivot offsets. Check script editor for unpublished assets.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
                return
                
    cmds.refresh()
    
    # Check for nodes with vertex edits.
    nodesWithVertexEdits = doGetNodesWithVertexEdits()
    if nodesWithVertexEdits:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='There are nodes with vertex edits in the scene file. Remove all vertex edits?', 
                button=["Remove", "Cancel"], 
                defaultButton="Remove", cancelButton="Cancel", dismissString="Remove"
                )
        if confirm == "Cancel": 
            return
        else:
            doRemoveVertexEdits(nodesWithVertexEdits)
    
    # Check for duplicate node names.
    topGrps = getTopGroups()
    doFixDuplicateNodeNames(topGrps)
    
    # Fix geo instance numbers
    topGrps = getTopGroups()
    ddCheckGeoInstanceNumber.do(topGrps)
    
    # Optimize and clean.
    continueClean = doOptimizeAndClean()
    if not continueClean:
        return
    
    # Add "GRP" to all groups above assets.
    doAddGrpToNodeNames()
    
    # Add metadata to top groups.
    ddAddGrpMetadata.do()
    
    # Create null hierarchy for motionBuilder.
    doCreateNullHierarchy()
    
    sys.stdout.write("Scene file cleaned. \n")
    confirm = cmds.confirmDialog(
        title="Done", messageAlign="center", 
        message='Scene has been cleaned.', 
        button=["Ok"], 
        defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
        )
    
# end (doCleanScene)


def doCleanUpShadingEngines(arg=None):
    '''
    Duplicate shading networks are numbered after ImportFromReference. 
    Delete Duplicate Shading Networks cleans out the duplicate shaders but may leave a number at the end of node names.
    This script will try to strip the number from the shading network nodes.
    '''
    cmds.waitCursor( state=True )
    shadingEngines = cmds.ls("*_SG*")
    
    for shadingEngine in shadingEngines:
        if shadingEngine.endswith("SG"):
            # Shading engine already has valid name.
            continue
        
        # Determine valid name for shading engine.
        correctShadingEngine = "%s_SG" % shadingEngine.rpartition("_SG")[0]
        
        # If shader with valid name does not already exist, use the name.
        if not cmds.objExists(correctShadingEngine):
            digit = shadingEngine.rpartition("_SG")[2]
            historyNodes = [x for x in (cmds.listHistory(shadingEngine) or []) if not cmds.nodeType(x) == "mesh"]
            for historyNode in historyNodes:
                if historyNode.endswith(digit):
                    cmds.rename(historyNode, historyNode.rpartition(digit)[0])            
        else:
            sys.stdout.write("The following shader might not exist in the Shader Library: %s\n" % shadingEngine.replace("_SG", "_SHD"))
    cmds.waitCursor( state=False )

# end (doCleanUpShadingEngines)


def doClearDisplay(arg=None):
    '''Button: Clear Display.
    '''
    displayDataSL = "displayDataSL"
    displayDataSL = cmds.textScrollList(displayDataSL, edit=True, removeAll=True)
    cmds.textField("currentlyShowingTFD", edit=True, text="")

# end (doClearDisplay)


def doCreateNullHierarchy(arg=None):
    '''
    Button: Create Null Hierarchy.
    Creates the scene hierarchy nulls for motionbuilder.
    '''
    sys.stdout.write("Creating null hierarchy... \n")
    cmds.refresh()
    
    # Find the scene name for the envName.
    sceneName = cmds.file(query=True, sceneName=True)
    sceneName = sceneName.replace("/", os.sep).rpartition(".")[0]
    version = sceneName.rpartition(os.sep)[2].partition(".")[0].rpartition("_")[2]
    if version.startswith("v"):
        version = int(version.replace("v", ""))
    else:
        version = 1
    layoutDir = os.path.join(ddConstants.ASSETLIBRARY.rpartition(os.sep)[0], "layoutFiles%s" % os.sep)
    prefix = "env_%s" % sceneName.replace(layoutDir, "").partition(os.sep)[0]
    
    # Names of nulls to be created.
    sceneMaster = "scene_master"
    envMaster = "env_master"
    envName = "%s_v%03d" % (prefix, int(version))
    lightMaster = "light_master"
    fxMaster = "fx_master"
    miscMaster = "misc_master"
    zuluMaster = "zulu_master"
    animMaster = "anim_master"
    charMaster = "char_master"
    camMaster = "cam_master"
    propsMaster = "props_master"
    
    # Request confirmation of name from user.
    result = cmds.promptDialog(
            title="Creating Scene Hierarchy Nulls", messageAlign="center", 
            message='Enter the env name including version number', text=envName, 
            button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
            )
    inputName = cmds.promptDialog(query=True, text=True)
    if inputName:
        envName = inputName
    
    envName = "%s_GRP" % envName
    if not envName.startswith("env_"):
        envName = "env_%s" % envName
    
    # Remove locator shapes if exist.
    for item in [sceneMaster, envMaster, lightMaster, fxMaster, miscMaster, zuluMaster, animMaster, charMaster, camMaster, propsMaster]:
        if cmds.objExists(item):
            itemShape = cmds.listRelatives(item, shapes=True)
            if itemShape and cmds.nodeType(itemShape[0]) == "locator":
                cmds.delete(itemShape[0])
            
    # Create the sceneMaster null.
    if not cmds.objExists(sceneMaster):
        sceneMaster = cmds.createNode("transform", name=sceneMaster)
    
    # Create the envName null.
    envNameNull = cmds.createNode("transform", name="%s_Temp" % envName)
    
    if not cmds.objExists(envMaster):
        envMaster = cmds.createNode("transform", name=envMaster, parent=sceneMaster)
    else:
        parent = cmds.listRelatives(envMaster, parent=True)
        if not parent or (parent and not parent[0] == sceneMaster):
            cmds.parent(envMaster, sceneMaster)
            
        children = cmds.listRelatives(envMaster, children=True, path=True) or []
        for child in children:
            #if child.startswith(prefix) or len(children) == 1:
            grandChildren = cmds.listRelatives(child, children=True, path=True)
            if grandChildren:
                cmds.parent(grandChildren, envNameNull)
            cmds.delete(child)
        
    envNameNull = cmds.rename(envNameNull, envName)
    cmds.parent(envNameNull, envMaster)
    
    # Create the rest of the nulls.
    for masterNode in [lightMaster, fxMaster, miscMaster, zuluMaster, animMaster, charMaster, camMaster, propsMaster]:
        if not cmds.objExists(masterNode):
            loc = cmds.createNode("transform", name=masterNode, parent=sceneMaster)
        else:
            parent = cmds.listRelatives(masterNode, parent=True)
            if not parent or (parent and not parent[0] == sceneMaster):
                cmds.parent(masterNode, sceneMaster)
    
    # Re-parent charMaster, camMaster and propMaster.
    cmds.parent(charMaster, camMaster, propsMaster, animMaster)
    
    # Lock the transforms.
    for node in (sceneMaster, envMaster, lightMaster, fxMaster, miscMaster, zuluMaster, animMaster, charMaster, camMaster, propsMaster):
        cmds.setAttr("%s.t" % node, lock=True)
        cmds.setAttr("%s.r" % node, lock=True)
    
    # Attempt to parent root level folders.
    leaveBehind = ["persp", "top", "front", "side", sceneMaster]
    assemblies = [x for x in cmds.ls(assemblies=True, long=True) if not x in leaveBehind]
    
    for node in assemblies:
        # Parent anything env related to the envName.
        if node.startswith("env") or node.startswith("Env") or node.startswith("ENV"):
            try:
                cmds.parent(node, envName)
            except: pass
        
        # Parent anything fx related to the fxMaster.
        if node.startswith("fx") or node.startswith("Fx") or node.startswith("FX"):
            try:
                cmds.parent(node, fxMaster)
            except: pass
        
        # Parent anything zulu related to the zuluMaster.
        if node.startswith("zulu") or node.startswith("Zulu") or node.startswith("ZULU"):
            try:
                cmds.parent(node, zuluMaster)
            except: pass
            
        # Parent lights to the lightMaster.
        if node.startswith("light") or node.startswith("Light") or node.startswith("LIGHT"):
            try:
                cmds.parent(node, lightMaster)
            except: pass
    
    # Stray lights
    lightShapes = cmds.ls(type="light")
    for lightShape in lightShapes:
        lightTransform = cmds.listRelatives(lightShape, parent=True, path=True)[0]
        lightParent = cmds.listRelatives(lightTransform, parent=True, path=True)
        if not lightParent or not lightParent[0] == lightMaster:
            try:
                cmds.parent(lightTransform, lightMaster)
            except: pass
    
    # Hunt down fx and zulu groups.
    fxGrps = ["fx_GRP", "Fx_GRP", "FX_GRP"]
    for fxGrp in fxGrps:
        if cmds.objExists(fxGrp):
            fxParent = cmds.listRelatives(fxGrp, parent=True, path=True)
            if fxParent and not fxParent[0] == fxMaster:
                cmds.parent(fxGrp, fxMaster)
                
    # Parent anything left lying around at the root level into the envName.
    assemblies = [x for x in cmds.ls(assemblies=True, long=True) if not x in leaveBehind]
    if assemblies:
        try:
            cmds.parent(assemblies, envName)
        except: pass

# end (doCreateNullHierarchy)


def doDisplayList(nodeList, checkIfReferenced=True):
    '''Loads list of nodes into window.
    '''
    displayDataSL = "displayDataSL"
    
    doClearDisplay()
    if nodeList:
        nodeList.sort()
        cmds.textScrollList(displayDataSL, edit=True, append=nodeList)
        if checkIfReferenced:
            for i in range(len(nodeList)):
                if cmds.referenceQuery(nodeList[i], isNodeReferenced=True):
                    cmds.textScrollList(displayDataSL, edit=True, lineFont=[i+1, "obliqueLabelFont"])
    else:
        cmds.textScrollList(displayDataSL, edit=True, append=["No nodes found"])
        
# end (doDisplayList)


def doFixAllDuplicateNodeNames(arg=None):
    '''Button: Fix Duplicate Node Names.
    '''
    displayDataSL = "displayDataSL"
    sys.stdout.write("Fixing all duplicate node names...\n")
    cmds.refresh()
    
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        doFixDuplicateNodeNames(nodes=items)
    sys.stdout.write("Finished fixing all duplicate node names.\n")

# end (doFixAllDuplicateNodeNames)


def doFixDuplicateNodeNames(nodes=None, arg=None):
    '''Menu Item: Fix Duplicate Node Names (Increment Instance).
    '''
    sys.stdout.write("Fixing duplicate node names (incrementing instances)... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    cmds.undoInfo(openChunk=True)
    
    if not nodes:
        nodes = getSelectedItems() or []
        
    for node in nodes:
        if not cmds.objExists(node):
            continue
        if cmds.referenceQuery(node, isNodeReferenced=True):
            cmds.waitCursor( state=False )
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", message='Cannot fix duplicate node names of referenced nodes.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        newNodeName = node.rpartition("|")[2]
        assetGrpName = newNodeName.rpartition("_")[0]
        if not assetGrpName:
            continue
            
        instanceNumber = 1
        found = True
        while found:
            newNodeName = "%s_%s" % (assetGrpName, instanceNumber)
            instanceNumber += 1
            if not cmds.objExists(newNodeName):
                found = False
            
        newNodeName = cmds.rename(node, newNodeName)
        newNodeName = ddCheckGeoInstanceNumber.do(newNodeName)
        
    doRefreshDisplay()
    cmds.undoInfo(closeChunk=True)
    cmds.waitCursor( state=False )

# end (doFixDuplicateNodeNames)


def doFixInstanceNumbers(arg=None):
    '''Button: Fix Instance Numbers.
    '''
    sys.stdout.write("Fixing instance numbers...\n")
    cmds.refresh()
    cmds.undoInfo(openChunk=True)
        
    topGrps = getTopGroups()
    ddCheckGeoInstanceNumber.do(topGrps)
    cmds.undoInfo(closeChunk=True)
    
    sys.stdout.write("Finished fixing instance numbers.\n")

# end (doFixInstanceNumbers)


def doFixInvalidNames(arg=None):
    '''Button: Fix Invalid Names.
    '''
    displayDataSL = "displayDataSL"
    sys.stdout.write("Fixing invalid names...\n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    cmds.undoInfo(openChunk=True)
    
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        newNodes = ddRemoveNamespaces.do(items)
        if newNodes:
            doRefreshDisplay()
            
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        newNodes = ddCheckGeoInstanceNumber.do(items)
        if newNodes:
            doRefreshDisplay()
            
    doFixAllDuplicateNodeNames()

    cmds.undoInfo(closeChunk=True)
    cmds.waitCursor( state=False )
    sys.stdout.write("Finished fixing invalid names.\n")

# end (doFixInvalidNames)


def doFixInvalidPivots(arg=None):
    '''Button: Fix Invaild Pivots.
    '''
    displayDataSL = "displayDataSL"
    sys.stdout.write("Fixing invalid pivots...\n")
    cmds.refresh()
    cmds.undoInfo(openChunk=True)
    
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        for item in items:
            if "_GRP_" in item.rpartition("|")[2]:
                valid = ddResetGeoMetadata.do(item)
            else:
                newNode = cmds.createNode("transform")
                parentNode = cmds.listRelatives(item, parent=True, path=True)
                if parentNode:
                    cmds.parent(newNode, parentNode[0])
                cmds.delete(cmds.parentConstraint(item, newNode, maintainOffset=False))
                children = cmds.listRelatives(item, children=True, path=True)
                if children:
                    cmds.parent(children, newNode)
                cmds.xform(item, objectSpace=True, rotatePivot=[0,0,0])
                cmds.xform(item, objectSpace=True, scalePivot=[0,0,0])
                cmds.delete(cmds.parentConstraint(newNode, item, maintainOffset=False))
                children = cmds.listRelatives(newNode, children=True, path=True)
                if children:
                    cmds.parent(children, item)
                cmds.delete(newNode)
        doRefreshDisplay()
    
    cmds.undoInfo(closeChunk=True)
    sys.stdout.write("Finished fixing invalid pivots.\n")

# end (doFixInvalidPivots)


def doFixRefEdits(arg=None):
    '''Button: Fix Reference Edits.
    '''
    displayDataSL = "displayDataSL"
    sys.stdout.write("Attempting to fix reference edits...\n")
    cmds.refresh()
    
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        doRemoveReferenceEdits(items)
        doRefreshDisplay()
    sys.stdout.write("Finished fixing reference edits. If not fixed, manually swap out for clean references.\n")

# end (doFixRefEdits)


def doFixVertexEdits(arg=None):
    '''Button: Fix Vertex Edits.
    '''
    displayDataSL = "displayDataSL"
    sys.stdout.write("Attempting to fix vertex edits...\n")
    cmds.refresh()
    
    items = cmds.textScrollList(displayDataSL, query=True, allItems=True)
    if items and not items == ["No nodes found"]:
        doRemoveVertexEdits(items)
        doRefreshDisplay()
    sys.stdout.write("Finished fixing vertex edits.\n")

# end (doFixVertexEdits)


def doFixWaitCursor(arg=None):
    '''Button: Fix Wait Cursor.
    '''
    cmds.waitCursor( state=False )

# end (doFixWaitCursor)


def doGetDuplicateNodeNames(arg=None):
    '''Button: Show Duplicate Node Names.
    '''
    sys.stdout.write("Building list of nodes with duplicate names...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    duplicateNodeNames = ddCheckFileForDuplicateNames.do()
    doDisplayList(duplicateNodeNames)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetDuplicateNodeNames")
    cmds.waitCursor( state=False )
    
    return duplicateNodeNames
    
# end (doGetDuplicateNodeNames)


def doGetInvalidNamesList(arg=None):
    '''
    Button: Show Invalid Names.
    Checks scene for invalid names. Returns list of invalid top grp nodes.
    '''
    sys.stdout.write("Building list of invalid names...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    topGrps = getTopGroups()
    invalidNamesList = list()
    
    for topGrp in topGrps:
        if not cmds.referenceQuery(topGrp, isNodeReferenced=True):
            currentAssetCategory = "environments"
            if topGrp.rpartition("|")[2].startswith("char_"):
                currentAssetCategory = "characters"
            invalidNodes = ddCheckNames.do(topGrp, currentAssetCategory)
            if invalidNodes:
                invalidNamesList.append(invalidNodes[0])
        else:
            sys.stdout.write("Unable to verify names of referenced node: %s\n" % topGrp)
    
    meshList = [cmds.listRelatives(x, parent=True, fullPath=True)[0] for x in cmds.ls(type="mesh")] or []
    for mesh in meshList:
        if not ("GEO" in mesh) and not ("zulu" in mesh):
            invalidNamesList.append(mesh)
            
    # Get invalid chessPiece names.
    chessPieceGrpNames = ["chesspieces", "Chesspieces", "ChessPieces", "chessPieces", "CHESSPIECES"]
    chessPieceGrp = ""
    chessPieces = list()
    
    for chessPieceName in chessPieceGrpNames:
        if cmds.objExists(chessPieceName):
            fullPath = cmds.ls(chessPieceName, long=True)
            chessPieceGrp = fullPath[0]
            
    if chessPieceGrp:
        chessPieces = cmds.listRelatives(chessPieceGrp, fullPath=True)
        
    for chessPieceName in chessPieceGrpNames:
        selList = [x for x in (cmds.ls("*%s*" % chessPieceName, long=True) or []) if cmds.nodeType(x) == "transform"]
        for sel in selList:
            if not sel in chessPieces and not sel == chessPieceGrp:
                chessPieces.append(sel)
    
    for chessPiece in chessPieces:
        invalidNodes = ddCheckNames.do(chessPiece, currentAssetCategory="characters")
        if invalidNodes:
                invalidNamesList.append(invalidNodes[0])
                
    # Check for duplicate node names.
    duplicateNodeNames = ddCheckFileForDuplicateNames.do()
    if duplicateNodeNames:
        invalidNamesList.extend(duplicateNodeNames)
        
    # Check geo instance numbers.
    ddCheckGeoInstanceNumber.do(topGrps)

    # Update invalid names list.
    invalidNamesList = list(set(invalidNamesList))
    
    doDisplayList(invalidNamesList)
    
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetInvalidNamesList")
    cmds.waitCursor( state=False )
    
    return invalidNamesList
    
# end (doGetInvalidNamesList)


def doGetInvalidTexturesList(arg=None):
    '''
    Button: Show Invalid Textures.
    Checks scene for invalid textures. Returns list of invalid texture nodes.
    '''
    sys.stdout.write("Building list of invalid textures...\n")
    doClearDisplay()
    cmds.refresh()

    cmds.waitCursor( state=True )
    invalid_textures = ddCheckTextures.check_all_layout_textures()

    doDisplayList(invalid_textures)
    cmds.textField("currentlyShowingTFD", edit=True,
                                        text="doGetInvalidTexturesList")
    cmds.waitCursor( state=False )

    return invalid_textures

# end (doGetInvalidTexturesList)


def doGetUnpublishedTexturesList(arg=None):
    '''
    Button: Show Unpublished Textures.
    Checks scene for unpublished textures.
    Returns list of top group nodes using unpublished textures.
    '''
    sys.stdout.write("Building list of unpublished textures...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    unpublishedShadingEngines = ddCheckTexturePublished.doCheckAllTexturesPublished()
    
    doDisplayList(unpublishedShadingEngines)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetUnpublishedTexturesList")
    cmds.waitCursor( state=False )
    
    return unpublishedShadingEngines
    
# end (doGetUnpublishedTexturesList)


def doGetNodesWithRefEdits(arg=None):
    '''Button: Show Reference Edits.
    '''
    sys.stdout.write("Building list of nodes with reference edits...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    topGrps = getTopGroups()
    refEdits = list()
    for topGrp in topGrps:
        if not cmds.referenceQuery(topGrp, isNodeReferenced=True):
            continue
        refNode = cmds.referenceQuery(topGrp, referenceNode=True)
        if cmds.referenceQuery(refNode, editNodes=True):
            refEditStrings = cmds.referenceQuery(refNode, editStrings=True)
            removeEdits = list()
            for refEdit in refEditStrings:
                if refEdit.startswith("parent "):
                    removeEdits.append(refEdit)
                #elif "dagSetMembers" in refEdit:
                #    removeEdits.append(refEdit)
                elif "drawInfo" in refEdit:
                    removeEdits.append(refEdit)
                else:
                    for ch in ["translate", "rotate", "scale", "visibility", "drawOverride"]:
                        if ("%s.%s" % (topGrp, ch)) in refEdit:
                            removeEdits.append(refEdit)
                    
            for removeEdit in removeEdits:
                refEditStrings.remove(removeEdit)        
            if refEditStrings:
                refEdits.append(topGrp)
    doDisplayList(refEdits)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetNodesWithRefEdits")    
    cmds.waitCursor( state=False )
    
    return refEdits
    
# end (doGetNodesWithRefEdits)


def doGetNodesWithVertexEdits(arg=None):
    '''Button: Show Vertex Edits.
    '''
    sys.stdout.write("Building list of nodes with vertex edits...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    topGrps = getTopGroups()
    vertexEdits = list()
    for topGrp in topGrps:
        children = cmds.listRelatives(topGrp, children=True, path=True)
        vertexEdit = edFindVertTransforms.edVtxChanges(transforms=children, reset=False, sel=False, debugOn=False) or []
        for vertEd in vertexEdit:
            parent = cmds.listRelatives(vertEd, parent=True, path=True)[0]
            vertexEdits.append(parent)
    doDisplayList(vertexEdits)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetNodesWithVertexEdits")
    cmds.waitCursor( state=False )
    
    return vertexEdits
    
# end (doGetNodesWithVertexEdits)


def doGetNonReferencedNodes(arg=None):
    '''Button: Show Non-Referenced Nodes.
    '''
    sys.stdout.write("Building list of non-referenced nodes...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    topGrps = getTopGroups()
    nonReferencedNodes = list()
    for topGrp in topGrps:
        if not cmds.referenceQuery(topGrp, isNodeReferenced=True):
            nonReferencedNodes.append(topGrp)
    doDisplayList(nonReferencedNodes)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetNonReferencedNodes")
    cmds.waitCursor( state=False )
    
    return nonReferencedNodes
    
# end (doGetNonReferencedNodes)


def doGetPivotOffsetsList(arg=None):
    '''
    Button: Shwo Invalid Pivots.
    Checks scene for GEO nodes with transforms which do not match metadata.
    '''
    sys.stdout.write("Building list of nodes with pivot offsets...\n")
    doClearDisplay()
    cmds.refresh()
    attrName = "originalPivot"
    
    cmds.waitCursor( state=True )
    allGrps = [x for x in (cmds.ls("*_GRP*", type="transform", long=True) or []) if not "GEO" in x]
    invalidTransforms = ddCheckPivotOffsets.do(allGrps)
    
    invalidTransforms = list(set(invalidTransforms))
    doDisplayList(invalidTransforms)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetPivotOffsetsList")
    cmds.waitCursor( state=False )
    
    return invalidTransforms
    
# end (doGetPivotOffsetsList)


def doGetPublishedAssets(arg=None):
    '''Button: Show Published Assets.
    '''
    sys.stdout.write("Building list of published assets...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    dividerTypes = ["GRP", "CPF", "CPO", "CPD"]
    meshList = [cmds.listRelatives(x, parent=True, fullPath=True)[0] for x in cmds.ls(type="mesh")]
    topGrpList = getTopGrpOfNode(meshList)
    publishedAssets = list()
    for topGrp in topGrpList:
        divider = ""
        for dividerType in dividerTypes:
            if dividerType in topGrp:
                divider = dividerType

        nodePath, grp, version = topGrp.rpartition(":")[2].rpartition("|")[2].partition("_%s_" % divider)
        version = version.partition("_")[0]
        dirs, underscore, asset = nodePath.rpartition("_")
        nodePathParts = nodePath.split("_")
        
        assetPath = ddConstants.ASSETLIBRARY
        for n in nodePathParts:
            assetPath = os.path.join(assetPath, n)
        
        if os.path.isdir(assetPath):
            assetName = topGrp.rpartition("|")[2]
            if divider in assetName:
                publishedAssets.append(assetName.rpartition("_")[0])
    
    publishedAssets = list(set(publishedAssets))
    doDisplayList(publishedAssets, checkIfReferenced=False)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetPublishedAssets")
    cmds.waitCursor( state=False )
    
# end (doGetPublishedAssets)


def doGetReferencedNodes(arg=None):
    '''Button: Show Referenced Nodes.
    '''
    sys.stdout.write("Building list of referenced nodes...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    topGrps = getTopGroups()
    referencedNodes = list()
    for topGrp in topGrps:
        if cmds.referenceQuery(topGrp, isNodeReferenced=True):
            referencedNodes.append(topGrp)
    doDisplayList(referencedNodes)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetReferencedNodes")
    cmds.waitCursor( state=False )
    
    return referencedNodes
    
# end (doGetReferencedNodes)


def doGetUnpublishedAssets(arg=None):
    '''Button: Show Unpublished Assets.
    '''
    sys.stdout.write("Building list of unpublished assets...\n")
    doClearDisplay()
    cmds.refresh()
    
    cmds.waitCursor( state=True )
    dividerTypes = ["GRP", "CPF", "CPO", "CPD"]
    meshList = [cmds.listRelatives(x, parent=True, fullPath=True)[0] for x in cmds.ls(type="mesh")]
    topGrpList = getTopGrpOfNode(meshList)
    unpublishedAssets = list()
    for topGrp in topGrpList:
        divider = ""
        for dividerType in dividerTypes:
            if dividerType in topGrp:
                divider = dividerType
        nodePath, grp, version = topGrp.rpartition(":")[2].rpartition("|")[2].partition("_%s_" % divider)
        version = version.partition("_")[0]
        dirs, underscore, asset = nodePath.rpartition("_")
        nodePathParts = nodePath.split("_")
        
        assetPath = ddConstants.ASSETLIBRARY
        for n in nodePathParts:
            assetPath = os.path.join(assetPath, n)
        
        if not os.path.isdir(assetPath):
            assetName = topGrp.rpartition("|")[2]
            if divider in assetName:
                unpublishedAssets.append(assetName)
    
    unpublishedAssets = list(set(unpublishedAssets))
    doDisplayList(unpublishedAssets, checkIfReferenced=False)
    cmds.textField("currentlyShowingTFD", edit=True, text="doGetUnpublishedAssets")
    cmds.waitCursor( state=False )
    
# end (doGetUnpublishedAssets)


def doImportAllFromRef(arg=None):
    '''Button. Import All From Reference.
    '''
    sys.stdout.write("Importing all from reference... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    
    try:
        mel.eval('MLdeleteUnused')
    except:
        pass
    
    topGrps = getTopGroups()
    for topGrp in topGrps:
        if not cmds.objExists(topGrp):
            continue
        newTopGrp = topGrp
        if cmds.referenceQuery(topGrp, isNodeReferenced=True):
            newTopGrp = ddImportFromReference.do(topGrp)
        newTopGrp = ddRemoveNamespaces.do(newTopGrp)
    
    try:
        mel.eval('MLdeleteUnused')
    except:
        pass
    
    cmds.waitCursor( state=False )
    sys.stdout.write("Finished importing all from reference.\n")
 
# end (doImportAllFromRef)


def doOptimizeAndClean(arg=None):
    '''Button: Optimize and Clean.
    '''
    cmds.waitCursor( state=True )
    # Remove all namespaces.
    # sys.stdout.write("Removing namespaces... \n")
    # cmds.refresh()
    # namespaces = cmds.namespaceInfo(listOnlyNamespaces=True) or []
    # for namespace in namespaces:
    #     if namespace == "UI" or namespace == "shared":
    #         continue
    #     cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)
    
    confirm = cmds.confirmDialog(
            title="Warning", messageAlign="center", message='Optimizing scene. Continue?', 
            button=["Ok", "Cancel"], 
            defaultButton="Ok", cancelButton="Cancel", dismissString="Ok"
            )
    if confirm == "Cancel": 
        cmds.waitCursor( state=False )
        return False

    # Optimize scene (all).
    sys.stdout.write("Optimizing scene... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    mel.eval('cleanUpScene 1;')

    # Remove any stray light links.
    sys.stdout.write("Removing stray light links... \n")
    cmds.refresh()
    count = 0
    cnxList = cmds.listConnections("defaultLightSet.msg", source=False, destination=True, plugs=True)
    for cnx in cnxList:
        if "ignore" in cnx:
            cmds.disconnectAttr("defaultLightSet.msg", cnx)
            count += 1
    sys.stdout.write("Deleted %s light link messages.\n" % count)
    cmds.refresh()

    cmds.waitCursor( state=False )
    sys.stdout.write("Optimized and cleaned.\n")

    return True

    # # Delete unused nodes.
    # sys.stdout.write("Deleting unused nodes... \n")
    # cmds.refresh()
    # mel.eval('MLdeleteUnused')
    #
    # # Remove duplicate shading networks.
    # sys.stdout.write("Removing duplicate shading networks... \n")
    # cmds.refresh()
    # mel.eval('removeDuplicateShadingNetworks( 0 );')
    #
    # # Clean up shading network node names.
    # sys.stdout.write("Cleaning up shading network names... \n")
    # cmds.refresh()
    # doCleanUpShadingEngines()
    #
    # # Delete unused nodes.
    # sys.stdout.write("Deleting unused nodes... \n")
    # cmds.refresh()
    # mel.eval('MLdeleteUnused')
    #
    # # Delete history.
    # sys.stdout.write("Deleting history... \n")
    # cmds.refresh()
    # topNodes = cmds.ls(assemblies=True)
    # cmds.delete(topNodes, constructionHistory=True)
    #
    # cmds.waitCursor( state=False )

    # Optimize scene (all).
    # sys.stdout.write("Optimizing scene... \n")
    # cmds.refresh()
    # cmds.waitCursor( state=True )
    # mel.eval('cleanUpScene 3;')
    
    # # Remove remaining renderLayers.
    # sys.stdout.write("Removing render layers... \n")
    # cmds.refresh()
    # renderLayers = cmds.ls(type="renderLayer") or []
    # for renderLayer in renderLayers:
    #     if not renderLayer == "defaultRenderLayer":
    #         cmds.delete(renderLayer)
    #
    # # Remove duplicate script nodes.
    # sys.stdout.write("Removing duplicate script nodes... \n")
    # cmds.refresh()
    # uiConfigScriptNodes = cmds.ls("uiConfigurationScriptNode*") or []
    # for uiConfigScriptNode in uiConfigScriptNodes:
    #     if not uiConfigScriptNode == "uiConfigurationScriptNode":
    #         cmds.delete(uiConfigScriptNode)
    #
    # sceneConfigScriptNodes = cmds.ls("sceneConfigurationScriptNode*") or []
    # for sceneConfigScriptNode in sceneConfigScriptNodes:
    #     if not sceneConfigScriptNode == "sceneConfigScriptNodes":
    #         cmds.delete(sceneConfigScriptNode)
    #
    # # Remove stray nodes.
    # sys.stdout.write("Removing stray nodes... \n")
    # cmds.refresh()
    # nodeTypes = ["hyperGraphInfo", "hyperLayout", "hyperView", "objectMultiFilter", "objectScriptFilter", "transformGeometry", "blindDataTemplate", "unknown"]
    # for node in nodeTypes:
    #     strayNodes = cmds.ls(type=node)
    #     for strayNode in strayNodes:
    #         if not strayNode in ["hyperGraphInfo", "hyperGraphLayout"]:
    #             try:
    #                 cmds.delete(strayNode)
    #             except: pass
    #
    # ddDeleteUnknownNodes.do()
    #
    # # Remove mental ray nodes.
    # nodesToDelete = ["mentalrayGlobals", "mentalrayItemsList", "miDefaultFramebuffer", "miDefaultOptions"]
    # for nodeToDelete in nodesToDelete:
    #     if cmds.objExists(nodeToDelete):
    #         try:
    #             cmds.delete(nodeToDelete)
    #         except:
    #             sys.stdout.write("--> Unable to delete %s.\n" % nodeToDelete)
                

    
    # # Remove transform geometry nodes.
    # sys.stdout.write("Removing transform geometry nodes... \n")
    # cmds.refresh()
    # transformGeometryNodes = cmds.ls(type="transformGeometry") or []
    # for transformGeometryNode in transformGeometryNodes:
    #     cnxList = cmds.listConnections(transformGeometryNode)
    #     if not cnxList:
    #         cmds.delete(transformGeometryNode)
    #
    # # Remove stray object sets.
    # sys.stdout.write("Removing stray object sets... \n")
    # cmds.refresh()
    # objectSets = cmds.ls(type="objectSet")
    # for objectSet in objectSets:
    #     if not cmds.listConnections(objectSet):
    #         try:
    #             cmds.delete(objectSet)
    #         except:
    #             sys.stdout.write("Unable to delete %s\n" % objectSet)
    #
    # # Remove stray sets.
    # objectSets = cmds.ls("*ViewSelectedSet")
    # if objectSets:
    #     try:
    #         cmds.delete(objectSets)
    #     except:
    #         pass
            
    # cmds.waitCursor( state=False )
    # sys.stdout.write("Optimized and cleaned.\n")
    #
    # return True
    
# end (doOptimizeAndClean)


def doPublishScene(arg=None):
    '''
    Button: Publish Scene.
    Saves maya ascii and fbx files. Removes unused requires statements from ".ma" file.
    '''
    exported = False
    startingDirectory = ddConstants.LAYOUT_DIR
    startingFileName = ""
    envNull = [x for x in (cmds.listRelatives("env_master", children=True) or []) if cmds.nodeType(x) == "transform" and x.startswith("env")]
    if envNull:
        startingFileName = envNull[0].replace("env_", "").replace("_GRP", "")
        directory = os.path.join(ddConstants.LAYOUT_DIR, startingFileName.rpartition("_")[0])
        if os.path.isdir(directory):
            startingDirectory = directory
        if os.path.isdir(os.path.join(directory, "published")):
            startingDirectory = os.path.join(directory, "published")
            
    done = False
    filename = None
    while not done:
        result = cmds.promptDialog(
                title="Publish Layout File", messageAlign="center", 
                message='Publishing layout file as:', text=startingFileName, 
                button=["Ok", "Cancel"], defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                )
        
        if result == "Cancel":
            return
        filename = cmds.promptDialog(query=True, text=True)
        if filename and not os.path.isfile(os.path.join(startingDirectory, "%s.ma" % filename)):
            done = True
        else:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='File already exists: %s. Try incrementing version.' % filename, 
                    button=["Ok", "Cancel"], 
                    defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel":
                return
                
    if filename:
        if not filename == startingFileName:
            if envNull:
                cmds.rename(envNull[0], "env_%s_GRP" % filename)
        
        filename = os.path.join(startingDirectory, "%s.ma" % filename.partition(".")[0])
        if os.path.isfile(filename):
            sys.stdout.write("File already exists: %s. Cancelling...\n" % filename)
            return
            
        # Save ".ma" file
        sys.stdout.write('Saving "%s"...\n' % filename)
        cmds.file( rename=filename )
        exportedFile = cmds.file(save=True, type="mayaAscii")
        ddRemoveRequires.do(path=exportedFile)
        
        # Export fbx file
        fbxFilename = filename.replace(".ma", ".fbx").replace(os.sep, "/")
        sys.stdout.write('Exporting fbx file "%s" ...\n' % fbxFilename)
        exported = False
        cmds.select("scene_master", replace=True)
        
        try:
            sys.stdout.write("Exporting fbx file (1-FBXExport).\n")
            mel.eval('FBXExport -f "%s" -s' % fbxFilename)
            exported = True
        except:
            pass
            
        if not exported:
            try:
                sys.stdout.write("Exporting fbx file (2-FBX export).\n")
                cmds.file(fbxFilename, type="FBX export", exportSelected=True, force=force)
                exported = True
            except:
                pass
                
        if not exported:
            try:
                sys.stdout.write("Exporting fbx file (3-Fbx).\n")
                cmds.file(fbxFilename, type="Fbx", exportSelected=True, force=force)
                exported = True
            except:
                pass
                
        if not exported:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='Fbx "%s" was not exported.' % fbxFilename, 
                    button=["Ok"], 
                    defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                    )
                    
    if exported:
        sys.stdout.write("Layout scene published. \n")
        confirm = cmds.confirmDialog(
            title="Done", messageAlign="center", 
            message='Scene has been published.', 
            button=["Ok"], 
            defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
            )
    
# end (doPublishScene)


def doRefreshDisplay(arg=None):
    '''Button: Refresh.
    '''
    refreshFn = cmds.textField("currentlyShowingTFD", query=True, text=True)
    if refreshFn == "doGetInvalidNamesList":
        doGetInvalidNamesList()
    elif refreshFn == "doGetInvalidTexturesList":
        doGetInvalidTexturesList()
    elif refreshFn == "doGetUnpublishedTexturesList":
        doGetUnpublishedTexturesList()
    elif refreshFn == "doGetPivotOffsetsList":
        doGetPivotOffsetsList()
    elif refreshFn == "doGetNodesWithRefEdits":
        doGetNodesWithRefEdits()
    elif refreshFn == "doGetNodesWithVertexEdits":
        doGetNodesWithVertexEdits()
    elif refreshFn == "doGetReferencedNodes":
        doGetReferencedNodes()
    elif refreshFn == "doGetNonReferencedNodes":
        doGetNonReferencedNodes()
    elif refreshFn == "doGetDuplicateNodeNames":
        doGetDuplicateNodeNames()
    elif refreshFn == "doGetPublishedAssets":
        doGetPublishedAssets()
    elif refreshFn == "doGetUnpublishedAssets":
        doGetUnpublishedAssets()
    else:
        pass

# end (doRefreshDisplay)


def doRemoveReferenceEdits(nodes=None, arg=None):
    '''Attempt to remove reference edits.
    '''
    sys.stdout.write("Removing reference edits... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    cmds.undoInfo(openChunk=True)
    
    if not nodes:
        nodes = getSelectedItems() or []
    refNodes = list()
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            refNode = cmds.referenceQuery(node, referenceNode=True)
            refNodes.append(refNode)
        
    refNodes = list(set(refNodes))
    
    for refNode in refNodes:
        # Get top node of refNode.
        referencedNodes = cmds.referenceQuery(refNode, nodes=True)
        
        # Get namespace.
        namespace = cmds.referenceQuery(refNode, namespace=True)
        if namespace:
            namespace = namespace.replace(":", "")
            
        # Find top GRP of referenced nodes.
        referencedTopGrp = ""
        refTransforms = list()
        for item in referencedNodes:
            try:
                if cmds.nodeType(item) == "transform":
                    refTransforms.append(item)
            except:
                pass
                
        for refTransform in refTransforms:
            refParent = cmds.listRelatives(refTransform, parent=True, fullPath=True)
            if not refParent or not refParent[0].rpartition("|")[2] in refTransforms:
                referencedTopGrp = mel.eval('longNameOf("%s")' % refTransform)
        
        # Disconnect from any display layers.
        topGrpLayer = ddRemoveFromLayers.do(nodes=referencedTopGrp)[0]
        
        # Get the list of reference edits.
        refEditsStrings = cmds.referenceQuery(refNode, editStrings=True)
        skipEdits = ["parent"]
        skipEditStrings = ["%s.translate" % referencedTopGrp, "%s.rotate" % referencedTopGrp, "%s.scale" % referencedTopGrp]
        refEditStringsToFix = list()
        
        # Sort out the reference edits to be removed from those which must be kept.
        for refEditString in refEditsStrings:
            if "drawInfo" in refEditString:
                continue
            # The refEditString is a complete mel command. 
            tokens = refEditString.split(" ")
            if tokens[0] in skipEdits:
                continue
            for token in tokens:
                if (namespace in token) and not token in skipEditStrings:
                    # Store the complete string to verify if ref edit has been fixed. 
                    refEditStringsToFix.append(refEditString)
                    try:
                        # Try to remove the reference edits.
                        cmds.referenceEdit(refEditNode, failedEdits=True, successfulEdits=True, editCommand=refEditCmd, removeEdits=True)
                    except:
                        sys.stdout.write("Failed to remove reference edit on %s.\n" % token)
                
        # Check if reference edits have really been fixed. If not, try to replace with reference.
        refEditsStrings = cmds.referenceQuery(refNode, editStrings=True)
        for refEditString in refEditsStrings:
            if refEditString in refEditStringsToFix:
                try:
                    sys.stdout.write("Attempting to replace with clean reference: %s.\n" % referencedTopGrp)
                    importedNodes = ddImportFromReference.do(referencedTopGrp)
                    if importedNodes:
                        done = ddReplaceWithReference.do(importedNodes[0])
                except:
                    sys.stdout.write("Unable to fix reference edits on %s.\n" % referencedTopGrp)
            
        # Reconnect to any display layers.
        if topGrpLayer:
            try:
                cmds.editDisplayLayerMembers(topGrpLayer, referencedTopGrp, noRecurse=True)
            except:
                sys.stdout.write("Unable to reconnect to display layer.\n")
                
    cmds.undoInfo(closeChunk=True)
    cmds.waitCursor( state=False )

# end (doRemoveReferenceEdits)


def doRemoveVertexEdits(nodes=None, arg=None):
    '''Zero out vertex edits.
    '''
    sys.stdout.write("Removing vertex edits... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    cmds.undoInfo(openChunk=True)
    
    if not nodes:
        nodes = getSelectedItems() or []
    if nodes:
        edFindVertTransforms.edVtxChanges(transforms=nodes, reset=True, sel=False, debugOn=False)
    cmds.undoInfo(closeChunk=True)
    cmds.waitCursor( state=False )

# end (doRemoveVertexEdits)


def doReplaceAllWithReferences(arg=None):
    '''Button: Replace All With References.
    '''
    sys.stdout.write("Replacing all with references... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    
    topGrps = getTopGroups()
    done = ddReplaceWithReference.do(topGrps)
    
    try:
        mel.eval('MLdeleteUnused')
    except:
        pass
    
    cmds.waitCursor( state=False )
    sys.stdout.write("Finished replacing all with references.\n")
    
# end (doReplaceAllWithReferences)


def doResetInstanceNumber(nodes=None, arg=None):
    '''Renames node with lowest available instance number.
    '''
    sys.stdout.write("Resetting instance numbers to lowest available... \n")
    cmds.refresh()
    cmds.waitCursor( state=True )
    
    cmds.undoInfo(openChunk=True)
    
    if not nodes:
        nodes = getSelectedItems() or []
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            cmds.waitCursor( state=False )
            
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", message='Cannot fix instance numbers of referenced nodes.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        
        newNodeName = node.rpartition("|")[2]
        assetGrpName = newNodeName.rpartition("_")[0]
        found = False
        instanceNumber = 1
        while not found:
            newNodeName = "%s_%s" % (assetGrpName, instanceNumber)
            selection = cmds.ls("*|%s" % newNodeName)
            if selection:
                instanceNumber += 1
            else:
                found = True
                
        newNodeName = cmds.rename(node, newNodeName)
    cmds.undoInfo(closeChunk=True)
    cmds.waitCursor( state=False )
    
    return True

# end (doResetInstanceNumber)


def doSelectItems():
    '''Selects listed item in scene file.
    '''
    selectedItems = getSelectedItems()
    if selectedItems:
        try:
            cmds.select(selectedItems, replace=True)
        except:
            pass
            
# end (doSelectItems)


def getSelectedItems():
    '''Returns selected item from list.
    '''
    displayDataSL = "displayDataSL"
    selectedItems = cmds.textScrollList(displayDataSL, query=True, selectItem=True)
    
    return selectedItems
    
# end (getSelectedItems)


def getTopGroups(topGrps=None):
    '''Returns list of top group nodes in scene.
    '''
    removeGrps = list()
    if not topGrps:
        topGrps = [x for x in cmds.ls(type="transform", long=True) if not cmds.listRelatives(x, shapes=True)]
        
    for topGrp in topGrps:
        children = cmds.listRelatives(topGrp, children=True, path=True) or []
        if not children:
            removeGrps.append(topGrp)
            continue
            
        for child in children:
            if child in topGrps:
                removeGrps.append(topGrp)
                continue
            if not cmds.listRelatives(child, shapes=True):
                removeGrps.append(topGrp)
                continue
                
        if not (topGrp[-1].isdigit()) or not ("GRP" in topGrp):
            removeGrps.append(topGrp)
            continue
    
    removeGrps = list(set(removeGrps))
    for grp in removeGrps:
        if cmds.objExists(grp):
            topGrps.remove(grp)
        
    return topGrps

# end (getTopGroups)


def getTopGrpOfNode(nodes):
    '''Returns top groups of nodes.
    '''
    dividerTypes = ["GRP", "CPF", "CPO", "CPD"]
    nodeList = list()
    for node in nodes:
        searchPath = node
        found = False
        while not found and searchPath:
            currentLevel = searchPath.rpartition("|")[2]
            dividerFound = False
            for dividerType in dividerTypes:
                if dividerType in currentLevel:
                    dividerFound = True
            if dividerFound:
                nodeList.append(searchPath)
                found = True
                searchPath = None
            else:
                children = cmds.listRelatives(searchPath, shapes=True)
                if children:
                    searchPath = searchPath.rpartition("|")[0]
                else:
                    nodeList.append(searchPath)
                    found = True
                    searchPath = None     
                    
    nodeList = list(set(nodeList))
    
    return nodeList

# end (getTopGrpOfNode)


def scFixInvalidNames(arg=None):
    '''Menu Item: Fix Invalid Names.
    '''
    sys.stdout.write("Matching GEO names to GRP... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    if nodes:
        newNodes = ddRemoveNamespaces.do(nodes)
        newNodes = ddCheckGeoInstanceNumber.do(newNodes)
        if newNodes:
            doRefreshDisplay()
    cmds.undoInfo(closeChunk=True)

# end (scFixInvalidNames)


def scCheckTextures(arg=None):
    '''Menu Item: Check Textures.
    '''
    sys.stdout.write("Checking textures... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    if nodes:
        if len(nodes) > 1:
            cmds.warning("Select only one top group.")
        else:
            validTextures = ddCheckTexturePublished.do(nodes, verbose=True)
            if validTextures:
                doRefreshDisplay()
    cmds.undoInfo(closeChunk=True)

# end (scCheckTextures)


def scImportFromReference(arg=None):
    '''Menu Item: Import From Reference.
    '''
    sys.stdout.write("Importing from reference... \n")
    nodes = getSelectedItems()
    if nodes:
        newNodes = ddImportFromReference.do(nodes)
        sys.stdout.write("Finished importing from reference.\n")

# end (scImportFromReference)


def scRemoveNamespaces(arg=None):
    '''Menu Item: Remove Namespaces.
    '''
    sys.stdout.write("Removing namespaces... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    if nodes:
        newNodes = ddRemoveNamespaces.do(nodes)
        sys.stdout.write("Finished removing namespaces.\n")
    cmds.undoInfo(closeChunk=True)

# end (scRemoveNamespaces)


def scRemoveReferenceEdits(arg=None):
    '''Menu Item: Remove Reference Edits.
    '''
    sys.stdout.write("Removing reference edits... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    if nodes:
        doRemoveReferenceEdits(nodes)
        sys.stdout.write("Finished removing reference edits.\n")
    cmds.undoInfo(closeChunk=True)

# end (scRemoveReferenceEdits)


def scRemoveVertexEdits(arg=None):
    '''Menu Item: Remove Vertex Edits.
    '''
    sys.stdout.write("Removing vertex edits... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    if nodes:
        doRemoveVertexEdits(nodes)
        sys.stdout.write("Finished removing vertex edits.\n")
    cmds.undoInfo(closeChunk=True)

# end (scRemoveVertexEdits)


def scReplaceWithReference(arg=None):
    '''Menu Item: Replace With Reference.
    '''
    sys.stdout.write("Replacing with reference... \n")
    nodes = getSelectedItems()
    if nodes:
        newNodes = ddReplaceWithReference.do(nodes)

# end (scReplaceWithReference)


def scResetGeoMetadata(arg=None):
    '''Menu Item: Fix Invalid Pivots (Reset Metadata).
    '''
    sys.stdout.write("Resetting metadata... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectedItems()
    for node in nodes:
        if "_GRP_" in node.rpartition("|")[2]:
            valid = ddResetGeoMetadata.do(node)
        else:
            newNode = cmds.createNode("transform")
            parentNode = cmds.listRelatives(node, parent=True, path=True)
            if parentNode:
                cmds.parent(newNode, parentNode[0])
            cmds.delete(cmds.parentConstraint(node, newNode, maintainOffset=False))
            children = cmds.listRelatives(node, children=True, path=True)
            if children:
                cmds.parent(children, newNode)
            cmds.xform(node, objectSpace=True, rotatePivot=[0,0,0])
            cmds.xform(node, objectSpace=True, scalePivot=[0,0,0])
            cmds.delete(cmds.parentConstraint(newNode, node, maintainOffset=False))
            children = cmds.listRelatives(newNode, children=True, path=True)
            if children:
                cmds.parent(children, node)
            cmds.delete(newNode)
            
        sys.stdout.write("Finished resetting metadata.\n")
    cmds.undoInfo(closeChunk=True)

# end (scResetGeoMetadata)


def scSwapForReference(arg=None):
    '''Menu Item: Swap For Reference.
    '''
    sys.stdout.write("Swapping for reference... \n")
    nodes = getSelectedItems()
    if nodes:
        newNodes = ddSwapForReference.do(nodes)
        sys.stdout.write
        sys.stdout.write("Finished swapping for reference.\n")

# end (scSwapForReference)


def showPublishLayoutHelp(arg=None):
    '''Builds the help window.
    '''
    if cmds.window("layoutPublishHelpWIN", query=True, exists=True):
        cmds.deleteUI("layoutPublishHelpWIN")

    # Window.
    helpWindow = cmds.window(
            "layoutPublishHelpWIN", title="Layout Publish Help", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    helpFL = cmds.formLayout("layoutPublishHelpFL", numberOfDivisions=100, parent=helpWindow)
    helpSF = cmds.scrollField("layoutPublishHelpSF", editable=False, wordWrap=True, text='INSTRUCTIONS\n\n(1) First, do one of the following:\n\n    (A) Run the "Clean Scene" button.\n\n            - OR -\n\n    (B) Step through the following buttons:\n\n            - Show Unpublished Assets (Make sure all assets have been published)\n            - Show Referenced Edits / Fix Reference Edits\n            - Import All From Reference\n            - Show Invalid Names / Fix Invalid Names\n            - Show Invalid Textures\n            - Show Invalid Pivots / Fix Invalid Pivots\n            - Show Vertex Edits / Fix Vertex Edits\n            - Show Duplicate Node Names / Fix Duplicate Node Names\n            - Fix Instance Numbers\n            - Optimize and Clean\n            - Add GRP to Node Names\n            - Add Metadata to GRP Nodes\n            - Create Null Hierarchy\n\n(2) Next, take a look at the scene to make sure nothing has changed.\n\n(3) Clean out any unnecessary layers and sets.\n\n(4) Check that everything has been correctly parented under the master nodes.\n\n(5) Finally, click "Publish Scene".\n\n\n . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n' )

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Clean Scene\nSteps through the buttons in (B) above. Ideally all assets would be referenced before running this tool as proof of asset publish but it is not a requirement. An attempt is made to remove reference edits before all objects are imported from reference. Duplicate node names are removed by incrementing instance numbers. Pivot offsets are checked, metadata is added to the top group nodes and construction history is deleted. The scene is then optimized which may take a few minutes. Any remaining render layers and duplicate script nodes are removed.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Publish Scene\nSaves out a mayaAscii file and parses the file to remove extraneous data. The file name should match the name on the env_master null but without "env_" at the beginning and "_GRP" at the end. For example: 0230_UFJ_riverbank_v001. Also exports an FBX file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Clear Display\nClears the display window of any data.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Refresh\nUpdates the data in the display window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Unpublished Assets\nDisplays list of assets not found in the Asset Library.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Published Assets\nDisplays list of assets found in the Asset Library.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Reference Edits\nDisplays list of top group nodes which have reference edits including manual shader adjustments.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Reference Edits\nAttempts to remove reference edits from nodes listed in display window. If removal fails, will try to replace with a clean reference.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Referenced Nodes\nDisplays list of all referenced GRP nodes in scene file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Non-Referenced Nodes\nDisplays list of all non-referenced GRP nodes in scene file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Replace All With References\nReplaces all assets with clean references from the Asset Library.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Import All From Reference\nImports all assets from reference.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Names\nRuns the Check Names script on the entire scene file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Invalid Names\nAttempts to fix names listed in the display window by removing namespaces, checking geo instance numbers and fixing duplicate node names. Upon occasion it may be necessary to hit this button twice.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Textures\nChecks if textures have been published in the Shader Library.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Pivots\nRuns the Check Pivot Offsets script on the entire scene file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Invalid Pivots\nRuns the Reset Geo Metadata script on the items listed in the display window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Vertex Edits\nDisplays nodes which have vertex edits.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Vertex Edits\nRemoves vertex edits from nodes listed in display window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Duplicate Node Names\nChecks scene file for duplicate node names.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Duplicate Node Names\nFixes duplicate node names by incrementing instances.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Instance Numbers\nRuns Check Geo Instance Number script on all top groups.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Optimize and Clean\nRuns optimize scene, deletes unused nodes, deletes duplicate shading networks, cleans up shading network node names, deletes history and removes other stray nodes.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Add GRP to Node Names\nAdds "GRP" to names of all trackable nodes.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Add Metadata to GRP Nodes\nAdds metadata to all nodes ending with "_GRP".\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Create Null Hierarchy\nCreates the scene hierarchy nulls.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Wait Cursor\nIf a script errors, the wait cursor may get stuck in the spinning mode. Click this button to fix it. Avoid clicking this button if the script has not errored. It will not affect execution but the script has not finished.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText=' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='RIGHT CLICK MENU (DISPLAY WINDOW)\n\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='Select some items in the display window and right click for the following options:\n\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Check Textures (For invalid textures, provides name of connected geo.)\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Fix Duplicate Node Names (Increment Instance)\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Fix Invalid Names\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Fix Invalid Pivots (Reset Metadata)\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Import From Reference\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Remove Namespaces\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Remove Reference Edits\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Remove Vertex Edits\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Replace With Reference\n')
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='    - Swap For Reference\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

    cmds.formLayout(helpFL, edit=True, 
        attachForm=[ (helpSF, "top", 15), 
                     (helpSF, "left", 15), 
                     (helpSF, "right", 15),
                     (helpSF, "bottom", 15)])

    window = cmds.window("layoutPublishHelpWIN", edit=True, widthHeight=(700, 1000))

    cmds.showWindow(helpWindow)
# end (showPublishLayoutHelp)


def do():
    '''Builds the window.
    '''
    
    # Ideally all nodes should be referenced as a guarantee that assets have been published.
    
    buttonHeight = 28
    colorLt = [0.28, 0.337, 0.375]
    colorDk = [0.2, 0.2, 0.2]
    
    if cmds.window("layoutPublishWIN", query=True, exists=True):
        cmds.deleteUI("layoutPublishWIN")
        
    if cmds.window("layoutPublishHelpWIN", query=True, exists=True):
        cmds.deleteUI("layoutPublishHelpWIN")
    
    # Window.
    window = cmds.window(
            "layoutPublishWIN", title="Layout Publish", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    mainFL = cmds.formLayout("sceneCheckerFL", numberOfDivisions=100)
    
    # Buttons.
    buttonsFL = cmds.formLayout("buttonsFL", numberOfDivisions=100, parent=mainFL)
    
    clearDisplayBTN = cmds.button(
            "clearDisplayBTN", label="Clear Display", height=buttonHeight, annotation="Clears display", 
            parent=buttonsFL, backgroundColor=colorLt, c=partial(doClearDisplay)
            )
    refreshBTN = cmds.button(
            "refreshBTN", label="Refresh", height=buttonHeight, annotation="Refresh display", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doRefreshDisplay)
            )
            
    unpublishedAssetsBTN = cmds.button(
            "unpublishedAssetsBTN", label="Show Unpublished Assets", height=buttonHeight, 
            annotation="Shows list of published assets (one instance).", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetUnpublishedAssets)
            )
    publishedAssetsBTN = cmds.button(
            "publishedAssetsBTN", label="Show Published Assets", height=buttonHeight, 
            annotation="Shows list of published assets (one instance).", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetPublishedAssets)
            )
    
    referencedBTN = cmds.button(
            "referencedBTN", label="Show Referenced Nodes", height=buttonHeight, 
            annotation="Shows list of referenced GRP nodes", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doGetReferencedNodes)
            )
    nonReferencedBTN = cmds.button(
            "nonReferencedBTN", label="Show Non-Referenced Nodes", height=buttonHeight, 
            annotation="Shows list of non-referenced GRP nodes", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doGetNonReferencedNodes)
            )
            
    refEditsBTN = cmds.button(
            "refEditsBTN", label="Show Reference Edits", height=buttonHeight, 
            annotation="Shows list of nodes with reference edits", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetNodesWithRefEdits)
            )
    fixRefEditsBTN = cmds.button(
            "fixRefEditsBTN", label="Fix Reference Edits", height=buttonHeight, 
            annotation="Fix nodes with reference edits", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doFixRefEdits)
            )
            
    replaceAllWithRefBTN = cmds.button(
            "replaceAllWithRefBTN", label="Replace All With References", height=buttonHeight, 
            annotation="Replace all assets with referenced assets", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doReplaceAllWithReferences)
            )
    importAllWithRefBTN = cmds.button(
            "importAllWithRefBTN", label="Import All From Reference", height=buttonHeight, 
            annotation="Import all assets from reference", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doImportAllFromRef)
            )
            
    invalidNamesBTN = cmds.button(
            "invalidNamesBTN", label="Show Invalid Names", height=buttonHeight, 
            annotation="Shows list of nodes with invalid names", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetInvalidNamesList)
            )
    fixInvalidNamesBTN = cmds.button(
            "fixInvalidNamesBTN", label="Fix Invalid Names", height=buttonHeight, 
            annotation="Fix nodes with invalid names", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doFixInvalidNames)
            )
            
    invalidTexturesBTN = cmds.button(
            "invalidTexturesBTN", label="Show Invalid Textures", height=buttonHeight, 
            annotation="Shows list of invalid texture nodes", parent=buttonsFL,
            backgroundColor=colorLt, c=partial(doGetInvalidTexturesList)
            )

    unpublishedShadersBTN = cmds.button(
            "unpublishedShadersBTN", label="Show Unpublished Shaders", height=buttonHeight,
            annotation="Shows list of nodes with unpublished shaders", parent=buttonsFL,
            backgroundColor=colorLt, c=partial(doGetUnpublishedTexturesList)
            )
            
    invalidPivotsBTN = cmds.button(
            "invalidPivotsBTN", label="Show Invalid Pivots", height=buttonHeight, 
            annotation="Shows list of nodes with pivot offsets", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetPivotOffsetsList)
            )
    fixInvalidPivotsBTN = cmds.button(
            "fixInvalidPivotsBTN", label="Fix Invalid Pivots", height=buttonHeight, 
            annotation="Fix nodes with pivot offsets", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doFixInvalidPivots)
            )
            
    vertexEditsBTN = cmds.button(
            "vertexEditsBTN", label="Show Vertex Edits", height=buttonHeight, 
            annotation="Shows list of nodes with vertex edits", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doGetNodesWithVertexEdits)
            )
    fixVertexEditsBTN = cmds.button(
            "fixVertexEditsBTN", label="Fix Vertex Edits", height=buttonHeight, 
            annotation="Shows list of nodes with vertex edits", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doFixVertexEdits)
            )
            
    duplicateNodeNamesBTN = cmds.button(
            "duplicateNodeNamesBTN", label="Show Duplicate Node Names", height=buttonHeight, 
            annotation="Shows list of nodes with duplicate names", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doGetDuplicateNodeNames)
            )
    fixDuplicateNodeNamesBTN = cmds.button(
            "fixDuplicateNodeNamesBTN", label="Fix Duplicate Node Names", height=buttonHeight, 
            annotation="Fix nodes with duplicate names", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doFixAllDuplicateNodeNames)
            )
            
    fixInstanceNumbersBTN = cmds.button(
            "fixInstanceNumbersBTN", label="Fix Instance Numbers", height=buttonHeight, 
            annotation="Fix and reset instance numbers", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doFixInstanceNumbers)
            )
            
    optimizeAndCleanBTN = cmds.button(
            "optimizeAndCleanBTN", label="Optimize and Clean", height=buttonHeight, 
            annotation="Optimize and clean scene file", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doOptimizeAndClean)
            )
            
    addGrpToNamesBTN = cmds.button(
            "addGrpToNamesBTN", label="Add GRP to Node Names", height=buttonHeight, 
            annotation="Add GRP to Node Names", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doAddGrpToNodeNames)
            )
            
    addGrpMetadataBTN = cmds.button(
            "addGrpMetadataBTN", label="Add Metadata to GRP Nodes", height=buttonHeight, 
            annotation="Add Metadata to GRP Nodes", parent=buttonsFL, 
            backgroundColor=colorDk, c=partial(doAddGrpMetadata)
            )
            
    createNullHierarchyBTN = cmds.button(
            "createNullHierarchyBTN", label="Create Null Hierarchy", height=buttonHeight, 
            annotation="Create Null Hierarchy", parent=buttonsFL, 
            backgroundColor=colorLt, c=partial(doCreateNullHierarchy)
            )
    fixWaitCursorBTN = cmds.button(
            "fixWaitCursorBTN", label="Fix Wait Cursor", height=30, annotation="Fix wait cursor.", 
            parent=buttonsFL, backgroundColor=colorDk, c=partial(doFixWaitCursor)
            )
    showPublishHelpBTN = cmds.button(
            "showPublishHelpBTN", label="Help", height=30, annotation="Show instructions and other information.", 
            parent=buttonsFL, backgroundColor=colorDk, c=partial(showPublishLayoutHelp)
            )
    
    # Display form layout.
    displayDataFL = cmds.formLayout("displayDataFL", numberOfDivisions=100, parent=mainFL)
    displayDataSL = cmds.textScrollList(
            "displayDataSL", allowMultiSelection=True, parent=displayDataFL, 
            selectCommand=partial(doSelectItems)
            )
    
    # Popup menu items.
    menu = cmds.popupMenu('displayDataMenu', parent=displayDataSL)
    cmds.menuItem(p=menu, l="Check Textures", c=partial(scCheckTextures))
    cmds.menuItem(p=menu, l="Fix Duplicate Node Names (Increment Instance)", c=partial(doFixDuplicateNodeNames))
    cmds.menuItem(p=menu, l="Fix Invalid Names", c=partial(scFixInvalidNames))
    cmds.menuItem(p=menu, l="Fix Invalid Pivots (Reset Metadata)", c=partial(scResetGeoMetadata))
    cmds.menuItem(p=menu, l="Import From Reference", c=partial(scImportFromReference))
    cmds.menuItem(p=menu, l="Remove Namespaces", c=partial(scRemoveNamespaces))
    cmds.menuItem(p=menu, l="Remove Reference Edits", c=partial(scRemoveReferenceEdits))
    cmds.menuItem(p=menu, l="Remove Vertex Edits", c=partial(scRemoveVertexEdits))
    cmds.menuItem(p=menu, l="Replace With Reference", c=partial(scReplaceWithReference))
    cmds.menuItem(p=menu, l="Swap For Reference", c=partial(scSwapForReference))
    
    # Bottom buttons.
    cleanSceneBTN = cmds.button(
            "cleanSceneBTN", label="Clean Scene", height=30, annotation="Cleans and optimizes scene.", 
            parent=mainFL, backgroundColor=colorLt, c=partial(doCleanScene)
            )
    publishSceneBTN = cmds.button(
            "publishSceneBTN", label="Publish Scene", height=30, annotation="Publishes mayaAscii scene file.", 
            parent=mainFL, backgroundColor=colorLt, c=partial(doPublishScene)
            )
    currentlyShowingTFD = cmds.textField("currentlyShowingTFD", text="", visible=False, parent=mainFL)
    
    # Set up the form.
    c1 = 26
    c2 = 65
    cmds.formLayout(mainFL, edit=True, 
        attachForm=[ (buttonsFL, "top", 15), (buttonsFL, "bottom", 15), 
                     (cleanSceneBTN, "bottom", 15), (publishSceneBTN, "bottom", 15),
                     (displayDataFL, "top", 15)],
                     
        attachPosition=[ 
                         (displayDataFL, "left", 12, 0), (displayDataFL, "right", 3, c2),
                         (buttonsFL, "left", 10, c2), (buttonsFL, "right", 12, 100),
                         (cleanSceneBTN, "left", 12, 0), (cleanSceneBTN, "right", 3, c2/2),
                         (publishSceneBTN, "left", 3, c2/2), (publishSceneBTN, "right", 3, c2)
                        ],
        attachControl=[ (displayDataFL, "bottom", 12, cleanSceneBTN)]
                    )
                        
    cmds.formLayout(displayDataFL, edit=True,
        attachForm = [ (displayDataSL, "top", 0), (displayDataSL, "left", 0), 
                       (displayDataSL, "right", 0), (displayDataSL, "bottom", 0) ])
                       
    cmds.formLayout(buttonsFL, edit=True,
        attachForm=[ (clearDisplayBTN, "top", 0), (refreshBTN, "top", 0),
                     (fixWaitCursorBTN, "bottom", 0), 
                     (showPublishHelpBTN, "bottom", 0)
                   ],
        attachPosition = [ (clearDisplayBTN, "left", 0, 0), (clearDisplayBTN, "right", 3, 50),
                           (refreshBTN, "left", 3, 50), (refreshBTN, "right", 0, 100),
                           (unpublishedAssetsBTN, "left", 0, 0), (unpublishedAssetsBTN, "right", 3, 50), 
                           (publishedAssetsBTN, "left", 3, 50), (publishedAssetsBTN, "right", 0, 100),
                           (referencedBTN, "left", 0, 0), (referencedBTN, "right", 3, 50),
                           (nonReferencedBTN, "left", 3, 50), (nonReferencedBTN, "right", 0, 100),
                           (refEditsBTN, "left", 0, 0), (refEditsBTN, "right", 3, 50),
                           (fixRefEditsBTN, "left", 3, 50), (fixRefEditsBTN, "right", 0, 100),
                           (replaceAllWithRefBTN, "left", 0, 0), (replaceAllWithRefBTN, "right", 3, 50),
                           (importAllWithRefBTN, "left", 3, 50), (importAllWithRefBTN, "right", 0, 100),
                           (invalidNamesBTN, "left", 0, 0), (invalidNamesBTN, "right", 3, 50),
                           (fixInvalidNamesBTN, "left", 3, 50), (fixInvalidNamesBTN, "right", 0, 100),
                           (invalidTexturesBTN, "left", 0, 0), (invalidTexturesBTN, "right", 3, 50),
                           (unpublishedShadersBTN, "left", 3, 50), (unpublishedShadersBTN, "right", 0, 100),
                           (invalidPivotsBTN, "left", 0, 0), (invalidPivotsBTN, "right", 3, 50),
                           (fixInvalidPivotsBTN, "left", 3, 50), (fixInvalidPivotsBTN, "right", 0, 100),
                           (vertexEditsBTN, "left", 0, 0), (vertexEditsBTN, "right", 3, 50),
                           (fixVertexEditsBTN, "left", 3, 50), (fixVertexEditsBTN, "right", 0, 100),
                           (duplicateNodeNamesBTN, "left", 0, 0), (duplicateNodeNamesBTN, "right", 3, 50),
                           (fixDuplicateNodeNamesBTN, "left", 3, 50), (fixDuplicateNodeNamesBTN, "right", 0, 100),
                           (fixInstanceNumbersBTN, "left", 0, 0), (fixInstanceNumbersBTN, "right", 0, 100),
                           (optimizeAndCleanBTN, "left", 0, 0), (optimizeAndCleanBTN, "right", 0, 100),
                           (addGrpToNamesBTN, "left", 0, 0), (addGrpToNamesBTN, "right", 0, 100),
                           (addGrpMetadataBTN, "left", 0, 0), (addGrpMetadataBTN, "right", 0, 100),
                           (createNullHierarchyBTN, "left", 0, 0), (createNullHierarchyBTN, "right", 0, 100),
                           (fixWaitCursorBTN, "left", 0, 0), (fixWaitCursorBTN, "right", 3, 50),
                           (showPublishHelpBTN, "left", 3, 50), (showPublishHelpBTN, "right", 0, 100),
                          ], 
        attachControl=[ (unpublishedAssetsBTN, "top", 24, clearDisplayBTN), 
                        (publishedAssetsBTN, "top", 24, refreshBTN), 
                        (referencedBTN, "top", 7, unpublishedAssetsBTN),
                        (nonReferencedBTN, "top", 7, publishedAssetsBTN),
                        (refEditsBTN, "top", 7, referencedBTN), 
                        (fixRefEditsBTN, "top", 7, referencedBTN),
                        (replaceAllWithRefBTN, "top", 7, refEditsBTN),
                        (importAllWithRefBTN, "top", 7, fixRefEditsBTN),
                        (invalidNamesBTN, "top", 7, replaceAllWithRefBTN),
                        (fixInvalidNamesBTN, "top", 7, importAllWithRefBTN),
                        (invalidTexturesBTN, "top", 7, invalidNamesBTN),
                        (unpublishedShadersBTN, "top", 7, fixInvalidNamesBTN),
                        (invalidPivotsBTN, "top", 7, invalidTexturesBTN),
                        (fixInvalidPivotsBTN, "top", 7, unpublishedShadersBTN),
                        (vertexEditsBTN, "top", 7, invalidPivotsBTN),
                        (fixVertexEditsBTN, "top", 7, fixInvalidPivotsBTN),
                        (duplicateNodeNamesBTN, "top", 7, vertexEditsBTN), 
                        (fixDuplicateNodeNamesBTN, "top", 7, fixVertexEditsBTN),
                        (fixInstanceNumbersBTN, "top", 7, duplicateNodeNamesBTN),
                        (optimizeAndCleanBTN, "top", 7, fixInstanceNumbersBTN),
                        (addGrpToNamesBTN, "top", 7, optimizeAndCleanBTN),
                        (addGrpMetadataBTN, "top", 7, addGrpToNamesBTN),
                        (createNullHierarchyBTN, "top", 7, addGrpMetadataBTN)
                        ]
                    )
                        
    window = cmds.window("layoutPublishWIN", edit=True, widthHeight=(1000, 625))
    
    cmds.showWindow(window)
    
# end (do)
