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
    ddLegalizeAssets.py
    
DESC
    Tools for legalizing assets.
    
USAGE
    ddLegalizeAssets.do()

FUNCTIONS
    doAddGeoMetadata()
    doAssetNamer()
    doChangeAssetCategory()
    doCheckGeoInstance()
    doCheckNames()
    doCheckPivotOffsets()
    doCheckTextures()
    doCreateReference()
    doDeleteRefObject()
    doDuplicateRefObject()
    doExportAssets()
    doImportFromReference()
    doLockGeoTransforms()
    doRemoveFromLayers()
    doRemoveNamespaces()
    doRemovePivotOffsets()
    doReplaceWithReference()
    doResetGeoMetadata()
    doScreenGrab()
    doSnap()
    doSwapReference()
    doTransferTransforms()
    doUnlockGeoTransforms()
    getAssetCategory()
    getAssetLibrary()
    getSelectionList()
    getTopGrpOfNode()
    showLegalizeAssetHelp()
    do()

'''


# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import sys
from functools import partial

apath = "B:/home/johnz/scripts/jbtool/cw_scripts"
if not apath in sys.path:
    sys.path.insert(2, apath)


# VAD
import ddConstants; reload(ddConstants)
import ddAddGeoMetadata; reload(ddAddGeoMetadata)
import ddAssetNamer; reload(ddAssetNamer)
import ddCheckGeoInstanceNumber; reload(ddCheckGeoInstanceNumber)
import ddCheckNames; reload(ddCheckNames)
import ddCheckPivotOffsets; reload(ddCheckPivotOffsets)
import ddCheckTextures; reload(ddCheckTextures)
import ddCheckTexturePublished; reload(ddCheckTexturePublished)
import ddCreateReference; reload(ddCreateReference)
import ddDeleteRefObject; reload(ddDeleteRefObject)
import ddDuplicateRefObject; reload(ddDuplicateRefObject)
import ddExportAssets; reload(ddExportAssets)
import ddImportFromReference; reload(ddImportFromReference)
import ddLockGeoTransforms; reload(ddLockGeoTransforms)
import ddRemoveFromLayers; reload(ddRemoveFromLayers)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddRemovePivotOffsets; reload(ddRemovePivotOffsets)
import ddReplaceWithReference; reload(ddReplaceWithReference)
import ddResetGeoMetadata; reload(ddResetGeoMetadata)
import ddScreenGrab; reload(ddScreenGrab)
import ddSnap; reload(ddSnap)
import ddSwapForReference; reload(ddSwapForReference)
import ddTransferTransformsFromGeo; reload(ddTransferTransformsFromGeo)
import ddUnlockGeoTransforms; reload(ddUnlockGeoTransforms)


def doAddGeoMetadata(arg=None):
    '''Button: Add Metadata.
    '''
    sys.stdout.write("Adding metadata... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddAddGeoMetadata.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doAddGeoMetadata)


def doAssetNamer(arg=None):
    '''Button: Asset Namer.
    '''
    sys.stdout.write("Naming assets... \n")
    cmds.undoInfo(openChunk=True)
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    if nodes:
        if len(nodes) > 1:
            sys.stdout.write("Select only one top group.\n")
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", message='Select only one top group.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        else:
            ddAssetNamer.do(nodes[0], currentAssetCategory=currentAssetCategory)
    else:
        if cmds.ls(selection=True):
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", message='Verify asset type is set correctly for selection.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
        else:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", message='Select a node to rename.', 
                    button=["Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel": 
                return False
             
    cmds.undoInfo(closeChunk=True)

# end (doAssetNamer)


def doChangeAssetCategory(arg=None):
    '''Disable/enable some buttons depending on asset category.
    '''
    currentAssetCategory = getAssetCategory()
    
    if currentAssetCategory == "characters":
        cmds.window("legalizeAssetWIN", edit=True, backgroundColor=[0.367, 0.367, 0.367])
    elif currentAssetCategory == "environments":
        cmds.window("legalizeAssetWIN", edit=True, backgroundColor=[0.267, 0.267, 0.267])

# end (doChangeAssetCategory)


def doCheckGeoInstance(arg=None):
    '''Button: Check Geo Instance No.
    '''
    sys.stdout.write("Matching GEO name to GRP... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddCheckGeoInstanceNumber.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doCheckGeoInstance)


def doCheckNames(arg=None):
    '''Button: Check Names.
    '''
    sys.stdout.write("Checking names... \n")
    cmds.undoInfo(openChunk=True)
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    if nodes:
        invalidNodes = ddCheckNames.do(nodes=nodes, currentAssetCategory=currentAssetCategory)
        if invalidNodes:
            cmds.warning("%s%s names are not valid." % (currentAssetCategory[0].upper(), currentAssetCategory[1:-1]))
        else:
            sys.stdout.write("%s%s names are valid.\n" % (currentAssetCategory[0].upper(), currentAssetCategory[1:-1]))
    cmds.undoInfo(closeChunk=True)

# end (doCheckNames)


def doCheckPivotOffsets(arg=None):
    '''Button: Check Pivot Offsets.
    '''
    sys.stdout.write("Checking pivot offsets... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        invalidNodes = ddCheckPivotOffsets.do(nodes)
        if invalidNodes:
            nodeStr = ""
            for node in invalidNodes:
                nodeStr += "%s, " % node
            sys.stdout.write("Pivot offsets found on: %s\n" % nodeStr[:-2])
        else:
            sys.stdout.write("Pivot offsets checked.\n")
    cmds.undoInfo(closeChunk=True)

# end (doCheckPivotOffsets)


def doCheckTextures(arg=None):
    '''Button: Check Textures.
    '''
    sys.stdout.write("Checking textures... \n")
    cmds.undoInfo(openChunk=True)
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    for node in nodes:
        texturesPublished = False
        validTextures, override = ddCheckTextures.do(node=node, override=False, publish=False)
        if validTextures:
            sys.stdout.write("Textures are valid for %s.\n" % node.rpartition("|")[2])
            texturesPublished = ddCheckTexturePublished.do(nodes=node, verbose=True, assetCategory=currentAssetCategory)
        if validTextures and texturesPublished:
            sys.stdout.write("Textures are valid and published for %s.\n" % node.rpartition("|")[2])
        elif not validTextures:
            sys.stdout.write("Textures are not valid for %s.\n" % node.rpartition("|")[2])
    cmds.undoInfo(closeChunk=True)

# end (doCheckTextures)


def doCreateReference(arg=None):
    '''Button: Create Reference.
    '''
    sys.stdout.write("Creating reference... \n")
    currentAssetLibrary = getAssetLibrary()
    ddCreateReference.do(currentAssetLibrary)

# end (doCreateReference)


def doDeleteRefObject(arg=None):
    '''Button: Delete Reference(s).
    '''
    sys.stdout.write("Deleting reference... \n")
    nodes = getSelectionList()
    if nodes:
        ddDeleteRefObject.do(nodes)

# end (doDeleteRefObject)


def doDuplicateRefObject(arg=None):
    '''Button: Duplicate Reference(s).
    '''
    sys.stdout.write("Duplicating reference... \n")
    nodes = getSelectionList()
    if nodes:
        ddDuplicateRefObject.do(nodes)

# end (doDuplicateRefObject)


def doExportAssets(arg=None):
    '''Button: Export Asset(s).
    '''
    sys.stdout.write("Exporting assets... \n")
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    if nodes:
        ddExportAssets.do(nodes=nodes, currentAssetCategory=currentAssetCategory)

# end (doExportAssets)


def doImportFromReference(arg=None):
    '''Button: Import From Reference.
    '''
    sys.stdout.write("Importing from reference... \n")
    mel.eval('MLdeleteUnused')
    nodes = getSelectionList()
    if nodes:
        ddImportFromReference.do(nodes)
    mel.eval('MLdeleteUnused')

# end (doImportFromReference)


def doLockGeoTransforms(arg=None):
    '''Button: Lock Transforms.
    '''
    sys.stdout.write("Locking GEO transforms... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddLockGeoTransforms.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doLockGeoTransforms)


def doRemoveFromLayers(arg=None):
    '''Button: Remove From Layers.
    '''
    sys.stdout.write("Removing from layers... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddRemoveFromLayers.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doRemoveFromLayers)


def doRemoveNamespaces(arg=None):
    '''Button: Remove Namespaces.
    '''
    sys.stdout.write("Removing namespaces... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddRemoveNamespaces.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doRemoveNamespaces)


def doRemovePivotOffsets(arg=None):
    '''Button: Remove Pivot Offsets.
    '''
    sys.stdout.write("Removing pivot offsets... \n")
    cmds.undoInfo(openChunk=True)
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    if nodes:
        ddRemovePivotOffsets.do(nodes=nodes, returnToPos=True, currentAssetCategory=currentAssetCategory)
    cmds.undoInfo(closeChunk=True)

# end (doRemovePivotOffsets)


def doReplaceWithReference(arg=None):
    '''Button: Replace With Reference.
    '''
    sys.stdout.write("Replacing from reference... \n")
    currentAssetLibrary = getAssetLibrary()
    nodes = getSelectionList()
    if nodes:
        ddReplaceWithReference.do(nodes=nodes, currentAssetLibrary=currentAssetLibrary)

# end (doReplaceWithReference)


def doResetGeoMetadata(arg=None):
    '''Button: Reset Metadata.
    '''
    sys.stdout.write("Resetting metadata... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddResetGeoMetadata.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doResetGeoMetadata)


def doScreenGrab(arg=None):
    '''Button: Screen Grab.
    '''
    sys.stdout.write("Taking screen grab... \n")
    currentAssetCategory = getAssetCategory()
    nodes = getSelectionList()
    if nodes:
        ddScreenGrab.do(nodes=nodes, currentAssetCategory=currentAssetCategory)

# end (doScreenGrab)


def doSnap(arg=None):
    '''Button: Snap.
    '''
    sys.stdout.write("Snapping... \n")
    ddSnap.do()

# end (doSnap)


def doSwapReference(arg=None):
    '''Button: Swap For Reference.
    '''
    sys.stdout.write("Swapping for reference... \n")
    currentAssetLibrary = getAssetLibrary()
    nodes = getSelectionList(topGrps=False)
    if nodes:
        ddSwapForReference.do(nodes=nodes, startingDirectory=currentAssetLibrary)

# end (doSwapReference)


def doTransferTransforms(arg=None):
    '''Button: Transfer Transforms.
    '''
    sys.stdout.write("Transferring transforms from GEO to GRP... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddTransferTransformsFromGeo.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doTransferTransforms)


def doUnlockGeoTransforms(arg=None):
    '''Button: Unlock Transforms.
    '''
    sys.stdout.write("Unlocking GEO transforms... \n")
    cmds.undoInfo(openChunk=True)
    nodes = getSelectionList()
    if nodes:
        ddUnlockGeoTransforms.do(nodes)
    cmds.undoInfo(closeChunk=True)

# end (doUnlockGeoTransforms)


def getAssetCategory(arg=None):
    '''Return selected asset category.
    '''
    selected = cmds.optionMenu("legalizeAssetCategoryMenu", query=True, select=True)
    assetCategory = ddConstants.ASSET_CATEGORIES[selected-1]
    return assetCategory

# end (getAssetCategory)


def getAssetLibrary(arg=None):
    '''Get selected asset category and return corresponding shader directory.
    '''
    assetCategory = getAssetCategory()
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[assetCategory]
    return currentAssetLibrary

# end (getAssetLibrary)


def getSelectionList(topGrps=True):
    '''Gets selection list.
    '''
    assetCategory = getAssetCategory()
    #if assetCategory in ["characters"]:
    #    topGrps = False
        
    selectionList = cmds.ls(selection=True, long=True)
    if not selectionList:
        cmds.warning("Select a node")
    else:
        if topGrps:
            topGrpList = getTopGrpOfNode(selectionList)
            if not topGrpList:
                if assetCategory == "characters":
                    return selectionList
                else:
                    cmds.warning("No top GRP nodes found for selected objects")
                    return topGrpList
            else:
                return topGrpList
    return selectionList

# end (getSelectionList)


def getTopGrpOfNode(nodes):
    '''Gets the top group of the node.
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
                    nodeList.append(searchPath)
                    found = True
                    searchPath = None     
                    
    nodeList = list(set(nodeList))
    
    return nodeList

# end (getTopGrpOfNode)


def showLegalizeAssetHelp(arg=None):
    '''Builds the help window.
    '''
    if cmds.window("legalizeAssetHelpWIN", query=True, exists=True):
        cmds.deleteUI("legalizeAssetHelpWIN")

    # Window.
    helpWindow = cmds.window(
            "legalizeAssetHelpWIN", title="Legalize Asset Help", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    helpFL = cmds.formLayout("legalizeAssetHelpFL", numberOfDivisions=100, parent=helpWindow)
    helpSF = cmds.scrollField("legalizeAssetHelpSF", editable=False, wordWrap=True, text='LEGALIZE ASSET HELP\n\nSelect an asset type from the drop down menu. Then select one or more GEO or GRP nodes. For the Asset Namer, select only one node.\n\n\n' )

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText=' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Check Names\nChecks if names are valid for publishing. Used by the Export Asset tool.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Check Textures\nChecks if texture files are "tif" format and dimensions are square, less than 2K and powers of 2. Also checks if shader has been published to the Shader Library.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Asset Namer\nNames the assets. Right click on the drop down menus to select the various subfolders.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Check Geo Instance No\nIf the instance numbers on the GEO nodes do not match the GRP node, this script will check and fix them.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Transfer Transforms\nAttempts to transfer transformation data from one GEO node to its GRP node. There can be only one GEO node under the GRP node to run this script.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Check Pivot Offsets\nCompares transformation values of the GEO nodes to the stored metadata.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Remove Pivot Offsets\nFreezes transforms, removes pivot offsets, deletes history and removes empty group nodes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Add Metadata\nSaves the translation values of the GEO nodes into the "originalPivot" attributes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Reset Metadata\nResets the translation values of the GEO nodes to the values stored in the "originalPivot" attributes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Import From Reference\nImports selection from reference, removes namespaces, fixes GEO instance numbers, reassigns any already existing shaders and deletes unused nodes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Replace With Reference\nReplaces selection with reference(s) of published asset(s) using namespaces to handle name clashes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Create Reference\nCreates reference using namespaces to handle name clashes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Swap For Reference\nSwaps selection for referenced asset(s). By default, the script will swap out the entire group. To swap out single meshes, unparent the meshes from a group before running. The selection can include one or more referenced or non-referenced nodes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Duplicate Reference(s)\nDuplicates selected reference(s) using namespaces to handle name clashes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Delete Reference(s)\nDeletes selected reference(s) and removes the namespace(s).\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Unlock Transforms\nUnlocks the transformation channels on the GEO nodes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Lock Transforms\nLocks the transformation channels on the GEO nodes.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Remove Namespaces\nRemoves namespaces from nodes that have been imported using the default Maya tools.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Remove From Layers\nRemoves selection from any layers. Used by the Export Asset tool.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Snap\nSelect two objects. The second object will be snapped to the first, matching translation, rotation and scale. This script will only work if the second object has unlocked transformation channels (eg. GRP nodes).\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Screen Grab\nSaves out a basic image of the asset using the perspective camera and the current angle. Also saves out a smaller version for the Asset Library thumbnails. The script will attempt to fit the object into the frame and sets the appearance to smooth shaded with textures. Used by the Export Asset tool but user can change the camera angle and redo the screen grab. \n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Export Asset(s)\nChecks names and shaders, removes pivot offsets, adds metadata, locks transforms, cleans out unknown nodes, and exports mayaAscii and fbx files. Replaces nodes with references. If "Delete original GRP" is cancelled, both the referenced and original objects should return to the original position. The exported mayaAscii file is parsed to remove extraneous data.\n\n\n')
    
    cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

    cmds.formLayout(helpFL, edit=True, 
        attachForm=[ (helpSF, "top", 15), 
                     (helpSF, "left", 15), 
                     (helpSF, "right", 15),
                     (helpSF, "bottom", 15)])

    window = cmds.window("legalizeAssetHelpWIN", edit=True, widthHeight=(700, 1000))

    cmds.showWindow(helpWindow)
    
# end (showLegalizeAssetHelp)


def do(defaultCategory="environments"):    
    '''Builds the window.
    '''
    buttonHeight = 30
    colorLt = [0.28, 0.337, 0.375]
    colorDk = [0.2, 0.2, 0.2]

    if cmds.window("legalizeAssetWIN", query=True, exists=True):
        cmds.deleteUI("legalizeAssetWIN")
    if cmds.window("legalizeAssetHelpWIN", query=True, exists=True):
        cmds.deleteUI("legalizeAssetHelpWIN")
    
    # Window.
    window = cmds.window(
            "legalizeAssetWIN", title="Legalize Asset", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(300, 450), backgroundColor=[0.267, 0.267, 0.267]
            )
            
    # Main form layout.
    mainFL = cmds.formLayout("legalizeAssetFL", numberOfDivisions=100)
    
    # Asset category.
    assetCategoryRL = cmds.rowLayout("legalizeAssetCategoryRL", parent=mainFL)
    cmds.optionMenu(
            "legalizeAssetCategoryMenu", label="Asset Type ", 
            changeCommand=partial(doChangeAssetCategory), parent=assetCategoryRL
            )
    for assetCategory in ddConstants.ASSET_CATEGORIES:
        cmds.menuItem("%sMI" % assetCategory, label=assetCategory)
    cmds.optionMenu("legalizeAssetCategoryMenu", edit=True, value=defaultCategory)
    
    # Buttons.
    checkNamesBTN = cmds.button(
            "checkNamesBTN", label="Check Names", height=buttonHeight, 
            annotation="Checks if names are legal. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doCheckNames)
            )
    checkTexturesBTN = cmds.button(
            "checkTexturesBTN", label="Check Textures", height=buttonHeight, 
            annotation="Checks if textures files are file format is proper tifs, no color node modifications and can also state if published in assetLibrary. Select one or more GEO or GRP nodes.",
            parent=mainFL, backgroundColor=colorDk, command=partial(doCheckTextures)
            )
    
    assetNamerBTN = cmds.button(
            "assetNamerBTN", label="Asset Namer", height=buttonHeight,  parent=mainFL, 
            annotation="Names assets. Select one top group.", 
            backgroundColor=colorLt, command=partial(doAssetNamer)
            )
    
    checkGeoInstanceBTN = cmds.button(
            "fixGeoInstanceBTN", label="Check Geo Instance No.", 
            annotation="Checks GEO name against GRP name. Select one or more GEO or GRP nodes.", 
            height=buttonHeight, parent=mainFL, backgroundColor=colorDk, 
            command=partial(doCheckGeoInstance)
            )
    transferTransformsBTN = cmds.button(
            "transferTransformsBTN", label="Transfer Transforms", height=buttonHeight, 
            annotation="Transfers transformation data from GEO to GRP node. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doTransferTransforms)
            )
    
    checkPivotOffsetsBTN = cmds.button(
            "checkPivotOffsetsBTN", label="Check Pivot Offsets", height=buttonHeight, 
            annotation="Checks if there are any pivot offsets on the node and children. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doCheckPivotOffsets)
            )
    removePivotOffsetsBTN = cmds.button(
            "removePivotOffsetsBTN", label="Remove Pivot Offsets", height=buttonHeight, 
            annotation="Freezes transforms and removes pivot offsets. Deletes history and removes empty group nodes. Returns to position. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doRemovePivotOffsets)
            )
    
    addGeoMetadataBTN = cmds.button(
            "addGeoMetadataBTN", label="Add Metadata", height=buttonHeight, 
            annotation="Adds metadata to selected GEO nodes. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doAddGeoMetadata)
            )
    resetGeoMetadataBTN = cmds.button(
            "resetGeoMetadataBTN", label="Reset Metadata", height=buttonHeight, 
            annotation="Resets position of GEO nodes to metadata. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doResetGeoMetadata)
            )
    
    importFromReferenceBTN = cmds.button(
            "importFromReferenceBTN", label="Import From Reference", height=buttonHeight, 
            annotation="Imports selected nodes from reference. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doImportFromReference)
            )
    replaceWithReferenceBTN = cmds.button(
            "replaceWithReferenceBTN", label="Replace With Reference", height=buttonHeight, 
            annotation="Replaces selected nodes with references. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doReplaceWithReference)
            )
    
    createReferenceBTN = cmds.button(
            "createReferenceBTN", label="Create Reference", height=buttonHeight, 
            annotation="Creates reference to asset.", parent=mainFL, backgroundColor=colorDk, 
            command=partial(doCreateReference)
            )
    swapReferenceBTN = cmds.button(
            "swapReferenceBTN", label="Swap For Reference", height=buttonHeight, 
            annotation="Swap current asset for another. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doSwapReference)
            )
    
    duplicateRefObjectBTN = cmds.button(
            "duplicateRefObjectBTN", label="Duplicate Reference(s)", 
            annotation="Duplicates references of selected object(s). Select one or more GEO or GRP nodes.", 
            height=buttonHeight,  parent=mainFL, backgroundColor=colorLt, 
            command=partial(doDuplicateRefObject)
            )
    deleteRefObjectBTN = cmds.button(
            "deleteRefObjectBTN", label="Delete Reference(s)", height=buttonHeight, 
            annotation="Deletes selected referenced object(s) from scene. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doDeleteRefObject)
            )
    
    unlockGeoTransformsBTN = cmds.button(
            "unlockGeoTransformsBTN", label="Unlock Transforms", height=buttonHeight, 
            annotation="Unlocks transform channels on GEO nodes. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doUnlockGeoTransforms)
            )
    lockGeoTransformsBTN = cmds.button(
            "lockGeoTransformsBTN", label="Lock Transforms", height=buttonHeight, 
            annotation="Locks transform channels on GEO nodes. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doLockGeoTransforms)
            )
    
    removeNamespacesBTN = cmds.button(
            "removeNamespacesBTN", label="Remove Namespaces", height=buttonHeight, 
            annotation="Removes namespaces from nodes. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doRemoveNamespaces)
            )
    removeFromLayersBTN = cmds.button(
            "removeFromLayersBTN", label="Remove From Layers", height=buttonHeight, 
            annotation="Disconnect layers from nodes. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorLt, command=partial(doRemoveFromLayers)
            )
    
    snapBTN = cmds.button(
            "snapBTN", label="Snap", height=buttonHeight, 
            annotation="Snaps second object to first. Select two objects.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doSnap)
            )
    screenGrabBTN = cmds.button(
            "screenGrabBTN", label="Screen Grab", height=buttonHeight, 
            annotation="Saves out an image of the asset. Select one or more GEO or GRP nodes.", 
            parent=mainFL, backgroundColor=colorDk, command=partial(doScreenGrab)
            )
    
    exportAssetBTN = cmds.button(
            "exportAssetBTN", label="Export Asset(s)", height=buttonHeight, 
            annotation="Exports assets from scene file. Select one or more GEO or GRP nodes.",  
            parent=mainFL, backgroundColor=colorLt, command=partial(doExportAssets)
            )

    helpBTN = cmds.button(
            "helpBTN", label="Help", height=buttonHeight, 
            annotation="Show instructions and other information.",  
            parent=mainFL, backgroundColor=colorDk, command=partial(showLegalizeAssetHelp)
            )
            
    # Set up the form.
    cmds.formLayout(mainFL, edit=True, 
        attachForm=[ (assetCategoryRL, "top", 15),
                     (exportAssetBTN, "left", 12), (exportAssetBTN, "right", 12), 
                     (helpBTN, "left", 12), (helpBTN, "right", 12) ],
        
        attachPosition=[ (assetCategoryRL, "left", 12, 0), (assetCategoryRL, "right", 12, 100),
                         
                         (checkNamesBTN, "left", 12, 0), (checkNamesBTN, "right", 3, 51),
                         (checkTexturesBTN, "left", 3, 51), (checkTexturesBTN, "right", 12, 100),
                         
                         (assetNamerBTN, "left", 12, 0), (assetNamerBTN, "right", 12, 100),                         
                         (checkGeoInstanceBTN, "left", 12, 0), (checkGeoInstanceBTN, "right", 3, 51),
                         (transferTransformsBTN, "left", 3, 51), (transferTransformsBTN, "right", 12, 100),
                         
                         (checkPivotOffsetsBTN, "left", 12, 0), (checkPivotOffsetsBTN, "right", 3, 51),
                         (removePivotOffsetsBTN, "left", 3, 51), (removePivotOffsetsBTN, "right", 12, 100),
                         
                         (addGeoMetadataBTN, "left", 12, 0), (addGeoMetadataBTN, "right", 3, 51),
                         (resetGeoMetadataBTN, "left", 3, 51), (resetGeoMetadataBTN, "right", 12, 100),
                         
                         (importFromReferenceBTN, "left", 12, 0), (importFromReferenceBTN, "right", 3, 51),
                         (replaceWithReferenceBTN, "left", 3, 51), (replaceWithReferenceBTN, "right", 12, 100),
                         
                         (createReferenceBTN, "left", 12, 0), (createReferenceBTN, "right", 3, 51),
                         (swapReferenceBTN, "left", 3, 51), (swapReferenceBTN, "right", 12, 100),
                         
                         (duplicateRefObjectBTN, "left", 12, 0), (duplicateRefObjectBTN, "right", 3, 51),
                         (deleteRefObjectBTN, "left", 3, 51), (deleteRefObjectBTN, "right", 12, 100),
                         
                         (unlockGeoTransformsBTN, "left", 12, 0), (unlockGeoTransformsBTN, "right", 3, 51),
                         (lockGeoTransformsBTN, "left", 3, 51), (lockGeoTransformsBTN, "right", 12, 100),
                         
                         (removeNamespacesBTN, "left", 12, 0), (removeNamespacesBTN, "right", 3, 51),
                         (removeFromLayersBTN, "left", 3, 51), (removeFromLayersBTN, "right", 12, 100),
                         
                         (snapBTN, "left", 12, 0), (snapBTN, "right", 3, 51),
                         (screenGrabBTN, "left", 3, 51), (screenGrabBTN, "right", 12, 100)
                        ],
        attachControl=[ 
                        (checkNamesBTN, "top", 14, assetCategoryRL),
                        (checkTexturesBTN, "top", 14, assetCategoryRL),
                        
                        (assetNamerBTN, "top", 7, checkNamesBTN),
                        
                        (checkGeoInstanceBTN, "top", 7, assetNamerBTN),
                        (transferTransformsBTN, "top", 7, assetNamerBTN),
                        
                        (checkPivotOffsetsBTN, "top", 7, checkGeoInstanceBTN),
                        (removePivotOffsetsBTN, "top", 7, checkGeoInstanceBTN),
                        
                        (addGeoMetadataBTN, "top", 7, checkPivotOffsetsBTN),
                        (resetGeoMetadataBTN, "top", 7, removePivotOffsetsBTN),
                        
                        (importFromReferenceBTN, "top", 7, addGeoMetadataBTN),
                        (replaceWithReferenceBTN, "top", 7, resetGeoMetadataBTN),
                        
                        (createReferenceBTN, "top", 7, importFromReferenceBTN),
                        (swapReferenceBTN, "top", 7, replaceWithReferenceBTN),
                        
                        (duplicateRefObjectBTN, "top", 7, createReferenceBTN),
                        (deleteRefObjectBTN, "top", 7, swapReferenceBTN),
                        
                        (unlockGeoTransformsBTN, "top", 7, duplicateRefObjectBTN),
                        (lockGeoTransformsBTN, "top", 7, deleteRefObjectBTN),
                        
                        (removeNamespacesBTN, "top", 7, unlockGeoTransformsBTN),
                        (removeFromLayersBTN, "top", 7, lockGeoTransformsBTN),
                        
                        (snapBTN, "top", 7, removeNamespacesBTN),
                        (screenGrabBTN, "top", 7, removeFromLayersBTN),
                        
                        (exportAssetBTN, "top", 7, screenGrabBTN), 

                        (helpBTN, "top", 7, exportAssetBTN) ] )
    
    # Jiggle window.
    window = cmds.window("legalizeAssetWIN", e=1, widthHeight=(300, 538))
    
    cmds.showWindow(window)
    
# end do()
