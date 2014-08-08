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
# $Date: 2014-06-20$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddAssetLibrary.py

DESC
    Tools for working with the Asset Library. 
    - Import or reference assets.

USAGE
    ddAssetLibrary.do()

FUNCTIONS
    addAssetToSelection()
    clearAssetsDisplay()
    deselectAllAssets()
    doAdjustGridSize()
    doBuildAssetCategories()
    doChangeAssetType()
    doCleanUpSwatches()
    doCloseAssetWindow()
    doImportAsset()
    doReferenceAsset()
    doRefreshAssetDisplay()
    doSwapAsset()
    getAssetCategories()
    getCategoryFolder()
    getAssetLibrary()
    getImageLibrary()
    getSelectionList()
    removeAssetFromSelection()
    do()
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import os
import re
import sys
import math
from functools import partial

# VAD
import ddConstants; reload(ddConstants)
import ddRemoveDuplicateShaders; reload(ddRemoveDuplicateShaders)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddSwapForReference; reload(ddSwapForReference)

# CONSTANTS
INDENT1 = "           >  "
INDENT2 = "                         >  "


def addAssetToSelection(assetName, arg=None):
    '''Stores name of selected asset into hidden textField to prevent multi-selection.
    '''
    # Get name of currently stored selectedAsset.
    selectedAsset = cmds.textField("currentAssetTFD", query=True, text=True)
    if selectedAsset:
        cmds.iconTextCheckBox("%sBTN" % selectedAsset, edit=True, value=False)
    
    # Update hidden textField with currently selected selectedAsset.
    cmds.textField("currentAssetTFD", edit=True, text=assetName)
    sys.stdout.write("--> %s\n" % assetName)

# end (addAssetToSelection)


def clearAssetsDisplay(arg=None):
    '''Remove all assets from display window.
    '''
    assetChildren = cmds.gridLayout("displayAssetsGL", query=True, childArray=True) or []
    for child in assetChildren:
        cmds.deleteUI(child)

# end (clearAssetsDisplay)


def deselectAllAssets(arg=None):
    '''Deselect the assets.
    '''
    allItems = cmds.gridLayout("displayAssetsGL", query=True, childArray=True) or []
    for item in allItems:
        cmds.iconTextCheckBox(item, edit=True, value=False)
    text = cmds.textField("currentAssetTFD", edit=True, text="")

# end (deselectAllAssets)


def doAdjustGridSize(arg=None):
    '''Adjust the number of grid columns when size of window changed.
    '''
    # Get size of window.
    width=cmds.scrollLayout("displayAssetsSL", query=True, width=True)
    cellWidth = 165
    # Calculate number of columns.
    numberOfColumns = math.ceil(width / cellWidth)
    cmds.gridLayout("displayAssetsGL", edit=True, numberOfColumns=numberOfColumns)
    # Refresh asset display.
    doRefreshAssetDisplay()

# end (doAdjustGridSize)


def doBuildAssetCategories(arg=None):
    '''
    Button: Refresh and Asset Type change. 
    Builds list of asset categories.
    '''
    doCleanUpSwatches()
    
    selectedDirectory = cmds.textScrollList("assetCategoriesSL", query=True, selectUniqueTagItem=True)

    # Initialize list.
    cmds.textScrollList("assetCategoriesSL", edit=True, removeAll=True)
    
    # Get categories from disk and add to displayed list.
    categories = getAssetCategories()
    for category in categories:
        categoryName = category.replace("env|veg|", INDENT2).replace("env|", INDENT1)
        cmds.textScrollList("assetCategoriesSL", edit=True, append=categoryName, uniqueTag=category)
    
    if not selectedDirectory:
        clearAssetsDisplay()
    else:
        selectedDirectory = cmds.textScrollList("assetCategoriesSL", edit=True, selectUniqueTagItem=selectedDirectory[0])
        doRefreshAssetDisplay()

# end (doBuildAssetCategories)


def doChangeAssetType(arg=None):
    '''When Asset Type changed, deselect all and build categories list.
    '''
    cmds.textScrollList("assetCategoriesSL", edit=True, deselectAll=True)
    deselectAllAssets()
    doBuildAssetCategories()

# end (doChangeAssetType)


def doCleanUpSwatches(arg=None):
    sys.stdout.write("Cleaning up asset swatches...\n")
    
    currentImageLibrary = getImageLibrary()
    currentAssetLibrary = getAssetLibrary()
    categories = getAssetCategories()

    
    for category in categories:
        directory = os.path.join(currentImageLibrary, category.replace("|", os.sep))
        assetFiles = [x for x in os.listdir(directory) if x.endswith(".jpg")]
        
        assetLibDirectory = directory.replace(currentImageLibrary, currentAssetLibrary)
        
        for assetFile in assetFiles:
            mayaFile = assetFile.replace(".jpg", ".ma")
            assetDirectory = assetFile.partition("_")[0]
            filename = os.path.join(assetLibDirectory, assetDirectory, mayaFile)
            if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
                # due to character naming 'CHAR_character',
                #   assetDirectory needs to be more accurate
                char_patt = re.compile("^([A-Z]{3}_[a-zA-Z]+)\w*$")
                asset_file_name = assetFile.replace(".jpg", "")
                if char_patt.match(asset_file_name):
                    assetDirectory = \
                                char_patt.search(asset_file_name).groups()[0]
                filename = os.path.join(assetLibDirectory, assetDirectory, "chesspiece", "published", mayaFile)
            if not os.path.isfile(filename):
                sys.stdout.write("Deleting asset swatch: %s\n" % assetFile.replace(".jpg", ""))
                swatchFile = os.path.join(directory, assetFile)
                if os.path.isfile(swatchFile):
                    os.remove(swatchFile)
                

# end (doCleanUpSwatches)


def doCloseAssetWindow(arg=None):
    '''
    Button: Close Window. 
    Deletes the UI.
    '''
    if cmds.window("AssetLibraryWIN", query=True, exists=True):
        cmds.deleteUI("AssetLibraryWIN")
    if cmds.window("assetLibraryHelpWIN", query=True, exists=True):
        cmds.deleteUI("assetLibraryHelpWIN")
# end (doCloseAssetWindow)


def doImportAsset(arg=None):
    '''
    Button: Import Asset. 
    Imports the asset using namespaces, then removes the namespaces.
    '''
    currentImageLibrary = getImageLibrary()
    currentAssetLibrary = getAssetLibrary()
    chesspieceTypes = ["CPF", "CPO", "CPD"]

    cmds.namespace(setNamespace=":")
    directory = getCategoryFolder()
    if not directory:
        return
    
    directory = directory.replace(currentImageLibrary, currentAssetLibrary)
    selected = cmds.textField("currentAssetTFD", query=True, text=True)
    if not selected:
        sys.stdout.write("Select an asset.\n")
        return
    
    assetDirectory = selected.partition("_")[0]
    filename = os.path.join(directory, assetDirectory, "%s.ma" % selected)
    if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
        # due to character naming 'CHAR_character',
        #   assetDirectory needs to be more accurate
        char_patt = re.compile("^([A-Z]{3}_[a-zA-Z]+)\w*$")
        if char_patt.match(selected):
            assetDirectory = char_patt.search(selected).groups()[0]
        filename = os.path.join(directory, assetDirectory, "chesspiece", "published", "%s.ma" % selected)
    if not os.path.isfile(filename):
        sys.stdout.write("File not found: %s.\n" % filename)
        return
        
    importedNodes = cmds.file(filename, i=True, namespace=selected, returnNewNodes=True)
    
    topNode = [x for x in importedNodes if cmds.nodeType(x) == "transform" and not cmds.listRelatives(x, shapes=True)]
    if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
        topNode = [x for x in importedNodes if cmds.nodeType(x) == "transform"]
    if topNode:
        topNode = ddRemoveNamespaces.do(topNode[0])
        ddRemoveDuplicateShaders.do(topNode)
    deselectAllAssets()

# end (doImportAsset)


def doReferenceAsset(arg=None):
    '''
    Button: Reference Asset. 
    References the assets using namespaces.
    '''
    currentImageLibrary = getImageLibrary()
    currentAssetLibrary = getAssetLibrary()
    cmds.namespace(setNamespace=":")
    directory = getCategoryFolder()
    if not directory:
        return
    
    directory = directory.replace(currentImageLibrary, currentAssetLibrary)
    selected = cmds.textField("currentAssetTFD", query=True, text=True)
    if not selected:
        sys.stdout.write("Select an asset.\n")
        return
    
    assetDirectory = selected.partition("_")[0]
    filename = os.path.join(directory, assetDirectory, "%s.ma" % selected)
    if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
        # due to character naming 'CHAR_character',
        #   assetDirectory needs to be more accurate
        char_patt = re.compile("^([A-Z]{3}_[a-zA-Z]+)\w*$")
        if char_patt.match(selected):
            assetDirectory = char_patt.search(selected).groups()[0]
        filename = os.path.join(directory, assetDirectory, "chesspiece", "published", "%s.ma" % selected)

    if os.path.isfile(filename):
        cmds.file(filename, reference=True, namespace=selected)
    else:
        sys.stdout.write("File not found: %s.\n" % filename)
        return

    deselectAllAssets()

# end (doReferenceAsset)


def doRefreshAssetDisplay(arg=None):
    '''Display assets for selected category.
    '''
    currentImageLibrary = getImageLibrary()

    # Get selected category folder.
    directory = getCategoryFolder()
    if not directory:
        return
    
    # Get the list of files on disk.
    assetFiles = [x for x in os.listdir(directory) if x.endswith(".jpg")]
    clearAssetsDisplay()
    for assetFile in assetFiles:
        # Build the buttons. 
        assetLabel = assetFile.rpartition(os.sep)[2].replace(".jpg", "")
        imageFilePath = os.path.join(directory, assetFile)
        button = cmds.iconTextCheckBox(
                "%sBTN" % assetLabel, parent="displayAssetsGL", style="iconAndTextVertical", 
                width=144, height=144, image=imageFilePath, label=assetLabel, annotation=assetLabel,
                onCommand=partial(addAssetToSelection, assetLabel), 
                offCommand=partial(removeAssetFromSelection, assetLabel)
                )
    
    # Clear hidden textField.
    cmds.textField("currentAssetTFD", edit=True, text="")

# end (doRefreshAssetDisplay)


def doSwapAsset(arg=None):
    '''
    Button: Swap For Reference. 
    Swaps current selection for referenced asset.
    '''
    currentImageLibrary = getImageLibrary()
    currentAssetLibrary = getAssetLibrary()
    cmds.namespace(setNamespace=":")
    directory = getCategoryFolder()
    if not directory:
        return
    
    directory = directory.replace(currentImageLibrary, currentAssetLibrary)
    selected = cmds.textField("currentAssetTFD", query=True, text=True)
    if not selected:
        sys.stdout.write("Select an asset.\n")
        return
        
    assetDirectory = selected.partition("_")[0]
    filename = os.path.join(directory, assetDirectory, "%s.ma" % selected)
    if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
        # due to character naming 'CHAR_character',
        #   assetDirectory needs to be more accurate
        char_patt = re.compile("^([A-Z]{3}_[a-zA-Z]+)\w*$")
        if char_patt.match(selected):
            assetDirectory = char_patt.search(selected).groups()[0]
        filename = os.path.join(directory, assetDirectory, "chesspiece", "published", "%s.ma" % selected)
    
    nodes = getSelectionList(topGrps=False)
    if nodes:
        ddSwapForReference.do(nodes=nodes, filename=filename)

# end (doSwapAsset)


def getAssetCategories(arg=None):
    '''Returns list of categories in assetLibrary on disk.
    '''
    currentImageLibrary = getImageLibrary()
    currentAssetLibrary = getAssetLibrary()
    categories = list()
    directories = [ x for x in (os.listdir(currentImageLibrary) or []) if os.path.isdir(os.path.join(currentImageLibrary, x)) 
               and not x.startswith(".") and not x in ["tex", "old"]]
    categories.extend(directories)
    
    subDir = os.path.join(currentImageLibrary, "env")
    if os.path.isdir(subDir):
        directories = [ x for x in (os.listdir(subDir) or []) if os.path.isdir(os.path.join(subDir, x)) 
               and not x.startswith(".") and not x in ["old"]]
        for directory in directories:
            categories.append("env|%s" % directory)
            
    subDir = os.path.join(subDir, "veg")
    if os.path.isdir(subDir):
        directories = [ x for x in (os.listdir(subDir) or []) if os.path.isdir(os.path.join(subDir, x)) 
               and not x.startswith(".") and not x in ["old"]]
        for directory in directories:
            categories.append("env|veg|%s" % directory)
            
    categories.sort()
    
    return categories

# end (getAssetCategories)


def getAssetLibrary(arg=None):
    '''Get selected asset category and return corresponding asset directory.
    '''
    selected = cmds.optionMenu("imageLibraryCategoryMenu", query=True, select=True)
    assetCategory = ddConstants.ASSET_CATEGORIES[selected-1]
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[assetCategory]
    
    return currentAssetLibrary

# end (getAssetLibrary)

    
def getImageLibrary(arg=None):
    '''Get selected asset category and return corresponding image directory.
    '''
    selected = cmds.optionMenu("imageLibraryCategoryMenu", query=True, select=True)
    assetCategory = ddConstants.ASSET_CATEGORIES[selected-1]
    currentImageLibrary = ddConstants.IMAGE_DIRECTORIES[assetCategory]
    
    return currentImageLibrary

# end (getImageLibrary)


def getCategoryFolder(arg=None):
    '''Returns selected directory folder path.
    '''
    currentImageLibrary = getImageLibrary()
    directory = cmds.textScrollList("assetCategoriesSL", query=True, selectUniqueTagItem=True)
    if not directory:
        return None
    directory = os.path.join(currentImageLibrary, directory[0].replace("|", os.sep))
    
    return directory

# end (getCategoryFolder)


def getSelectionList(topGrps=True):
    '''Returns list of selected nodes or top groups of selected nodes.
    '''
    selectionList = cmds.ls(selection=True, long=True)
    if not selectionList:
        cmds.warning("Select a node")
    else:
        if topGrps:
            topGrpList = getTopGrpOfNode(selectionList)
            return topGrpList
            
    return selectionList

# end (getSelectionList)


def removeAssetFromSelection(assetName, arg=None):
    '''Removes name of selected asset from hidden textField to prevent multi-selection.
    '''
    # Get name of currently stored selectedAsset.
    selectedAsset = cmds.textField("currentAssetTFD", query=True, text=True)
    if selectedAsset == assetName:
        # Reset hidden textField.
        cmds.textField("currentAssetTFD", edit=True, text="")

# end (removeAssetFromSelection)

    
def showAssetLibraryHelp(arg=None):
    '''Builds the help window.
    '''
    if cmds.window("assetLibraryHelpWIN", query=True, exists=True):
        cmds.deleteUI("assetLibraryHelpWIN")

    # Window.
    helpWindow = cmds.window(
            "assetLibraryHelpWIN", title="Asset Library Help", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    helpFL = cmds.formLayout("assetLibraryHelpFL", numberOfDivisions=100, parent=helpWindow)
    helpSF = cmds.scrollField("assetLibraryHelpSF", editable=False, wordWrap=True, text='ASSET LIBRARY HELP\n\nSelect an asset type from the drop down menu to display the correct Asset Library. The available asset categories will be displayed in the left column.\n\n\n' )

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='Select a category from the left column to display available assets. Left click on a swatch to select it. Right click on a selected swatch for the popup menu options: Import Asset, Reference Asset, Swap for Reference. These options are identical to the buttons at the bottom of the window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText=' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Import Asset\nImports the selected asset.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Reference Asset\nReferences the selected asset.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Swap for Reference\nSwaps selection for referenced asset(s). By default, the script will swap out the entire group. To swap out single meshes, unparent the meshes from a group before running. The selection can include one or more referenced or non-referenced nodes.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Refresh\nRefreshes the category list and displayed assets window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

    cmds.formLayout(helpFL, edit=True, 
        attachForm=[ (helpSF, "top", 15), 
                     (helpSF, "left", 15), 
                     (helpSF, "right", 15),
                     (helpSF, "bottom", 15)])

    window = cmds.window("assetLibraryHelpWIN", edit=True, widthHeight=(700, 610))

    cmds.showWindow(helpWindow)
    
# end (showAssetLibraryHelp)


def do(defaultCategory="environments"):
    '''Builds the Asset Library window.
    '''
    # Delete or close any existing Asset Library window.
    doCloseAssetWindow()
    
    # Reset the default namespace to root.
    cmds.namespace(setNamespace=":")    
    
    window = cmds.window(
            "AssetLibraryWIN", title="Asset Library", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(800, 450)
            )
            
    mainFL = cmds.formLayout("AssetLibraryFL", numberOfDivisions=100)
    
    assetCategoryRL = cmds.rowLayout("assetLibraryCategoryRL", parent=mainFL)
    cmds.optionMenu(
            "imageLibraryCategoryMenu", label="Asset Type ", 
            changeCommand=partial(doChangeAssetType), parent=assetCategoryRL
            )
    for assetCategory in ddConstants.ASSET_CATEGORIES:
        cmds.menuItem("%sMI" % assetCategory, label=assetCategory)
    cmds.optionMenu("imageLibraryCategoryMenu", edit=True, value=defaultCategory)
    
    mainPL = cmds.paneLayout(
            "AssetLibraryPL", configuration="vertical2", paneSize=[1,25,100], parent=mainFL
            )
    assetCategoriesSL = cmds.textScrollList(
            "assetCategoriesSL", parent=mainPL, selectCommand=partial(doRefreshAssetDisplay)
            )
    
    displayAssetsSL = cmds.scrollLayout(
            "displayAssetsSL", childResizable=True, parent=mainPL, 
            resizeCommand=partial(doAdjustGridSize)
            )
            
    displayAssetsGL = cmds.gridLayout(
            "displayAssetsGL", cellWidthHeight=(165, 180), 
            numberOfColumns=4, parent=displayAssetsSL
            )
    
    displayAssetsMenu = cmds.popupMenu('displayAssetsMenu', parent=displayAssetsGL)
    cmds.menuItem(p=displayAssetsMenu, l="Import Asset", c=partial(doImportAsset))
    cmds.menuItem(p=displayAssetsMenu, l="Reference Asset", c=partial(doReferenceAsset))
    cmds.menuItem(p=displayAssetsMenu, l="Swap For Reference", c=partial(doSwapAsset))

    
    importAssetBTN = cmds.button(
            "importAssetBTN", label="Import Asset", height=30, 
            annotation="Imports selected asset.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doImportAsset)
            )
    referenceAssetBTN = cmds.button(
            "referenceAssetBTN", label="Reference Asset", height=30, 
            annotation="References selected asset.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doReferenceAsset)
            )
    
    swapForReferenceAssetBTN = cmds.button(
            "swapForReferenceBTN", label="Swap for Reference", height=30, 
            annotation="Swap current asset for another.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doSwapAsset)
            )
    
    refreshAssetsBTN = cmds.button(
            "refreshAssetsBTN", label="Refresh", height=30, 
            annotation="Refresh asset display.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doBuildAssetCategories)
            )
    
    assetLibraryHelpBTN = cmds.button(
            "assetLibraryHelpBTN", label="Help", height=30, 
            annotation="Show instructions and other information.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(showAssetLibraryHelp)
            )
    currentAssetTFD = cmds.textField("currentAssetTFD", text="", visible=False, parent=mainFL)
    
    r1 = 89
    c1 = 20
    c2 = 40
    c3 = 60
    c4 = 80
    
    cmds.formLayout(mainFL, edit=True, 
        attachPosition=[ (assetCategoryRL, "top", 15, 0),
                         (mainPL, "top", 45, 0), 
                         (importAssetBTN, "bottom", 15, 100),
                         (referenceAssetBTN, "bottom", 15, 100),
                         (swapForReferenceAssetBTN, "bottom", 15, 100),
                         (refreshAssetsBTN, "bottom", 15, 100),
                         (assetLibraryHelpBTN, "bottom", 15, 100),
                         
                         (assetCategoryRL, "left", 12, 0), (assetCategoryRL, "right", 12, 100),
                         (mainPL, "left", 12, 0), (mainPL, "right", 12, 100),
                         (importAssetBTN, "left", 12, 0), (importAssetBTN, "right", 3, c1),
                         (referenceAssetBTN, "left", 3, c1), (referenceAssetBTN, "right", 3, c2),
                         (swapForReferenceAssetBTN, "left", 3, c2), (swapForReferenceAssetBTN, "right", 3, c3), 
                         (refreshAssetsBTN, "left", 3, c3), (refreshAssetsBTN, "right", 3, c4), 
                         (assetLibraryHelpBTN, "left", 3, c4), (assetLibraryHelpBTN, "right", 12, 100) 
                         ],
        attachControl=[ (mainPL, "bottom", 15, importAssetBTN) ]
        )
        
    window = cmds.window("AssetLibraryWIN", edit=True, widthHeight=(800, 600))
    
    # Build the categories list and refresh the selectedAsset display.
    doBuildAssetCategories()
    
    cmds.showWindow(window)
    
# end (do)
