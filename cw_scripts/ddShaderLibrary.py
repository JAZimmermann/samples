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
# $Date: 2014-06-14$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddShaderLibrary.py

DESC
    Tools for working with the Shader Library. 
    - Import selected shader and assign to selected objects.
    - Publish shader attached to selected mesh into a category folder.
    - Right-click on a selected shader swatch to move a shader into a category folder.
    - Ctrl-click on a selected shader swatch to rename or delete a shader.

USAGE
    ddShaderLibrary.do()
    
FUNCTIONS
    addSwatchToSelection()
    clearShadersDispay()
    closeWindow()
    deselectAll()
    doAdjustGridSize()
    doBuildMoveToList()
    doBuildShaderCategories()
    doCreateCategory()
    doDeleteShader()
    doImportShaders()
    doMoveShaderToFolder()
    doPublishShader()
    doRefreshSwatchDisplay()
    doRemoveShaders()
    doRenameShader()
    getAssetShaderLibrary()
    getCategoryFolder()
    getConnectedShadingEngine()
    getFileNames()
    getShaderCategories()
    moveShader()
    removeSwatchFromSelection()
    renameShaderNodes()
    showShaderLibraryHelp()
    do()

'''

# MAYA
import maya.cmds as cmds

# PYTHON
import os
import sys
import shutil
import math
from functools import partial

# VAD
import ddConstants; reload(ddConstants)
import ddCheckTexturePublished; reload(ddCheckTexturePublished)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddPublishShader; reload(ddPublishShader)


def addSwatchToSelection(swatchName, arg=None):
    '''Stores name of selected swatch into hidden textField to prevent multi-selection.
    '''
    # Get name of last selected swatch.
    swatch = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if swatch:
        # Deselect checkbox.
        cmds.iconTextCheckBox("%sBTN" % swatch, edit=True, value=False)
    
    # Update hidden textField with currently selected swatch.
    cmds.textField("currentlySelectedTFD", edit=True, text=swatchName)

# end (addSwatchToSelection)


def clearShadersDispay(arg=None):
    '''Remove all swatches from display window.
    '''
    swatchChildren = cmds.gridLayout("displaySwatchesGL", query=True, childArray=True) or []
    for child in swatchChildren:
        cmds.deleteUI(child)

# end (clearShadersDispay)


def closeWindow(arg=None):
    '''
    Button: Close Window.
    Deletes the UI.
    '''
    if cmds.window("ShaderLibraryWIN", query=True, exists=True):
        cmds.deleteUI("ShaderLibraryWIN")
    if cmds.window("shaderLibraryHelpWIN", query=True, exists=True):
        cmds.deleteUI("shaderLibraryHelpWIN")

# end (closeWindow)


def deselectAll(arg=None):
    '''Deselect the shaders.
    '''
    allItems = cmds.gridLayout("displaySwatchesGL", query=True, childArray=True)
    for item in allItems:
        cmds.iconTextCheckBox(item, edit=True, value=False)
    text = cmds.textField("currentlySelectedTFD", edit=True, text="")

# end (deselectAll)


def doAdjustGridSize(arg=None):
    '''Adjust the number of grid columns when size of window changed.
    '''
    # Get size of window.
    width=cmds.scrollLayout("displaySwatchesSL", query=True, width=True)
    cellWidth = 165
    # Calculate number of columns.
    numberOfColumns = math.ceil(width / cellWidth)
    cmds.gridLayout("displaySwatchesGL", edit=True, numberOfColumns=numberOfColumns)
    # Refresh swatch display.
    doRefreshSwatchDisplay()

# end (doAdjustGridSize)


def doBuildMoveToList(arg=None):
    '''Build list of categories shader can be moved to.
    '''
    swatchesMenu = "displaySwatchesMenu"
    # Get the selected category.
    selectedCategory = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True) or []
    
    # Initialize the menu.
    cmds.popupMenu(swatchesMenu, edit=True, deleteAllItems=True)
    cmds.menuItem(p=swatchesMenu, l="--> To Move Shader, Select A Folder")
    if not ("-- UNFILED --" in selectedCategory):
        cmds.menuItem(p=swatchesMenu, l="-- UNFILED --", c=partial(doMoveShaderToFolder, "-- UNFILED --"))
    
    # Get list of categories from disk.
    categories = getShaderCategories()
    for category in categories:
        # Exclude selected category from list.
        if not category in selectedCategory:
            cmds.menuItem(p=swatchesMenu, l=category, c=partial(doMoveShaderToFolder, category))

# end (doBuildMoveToList)


def doBuildShaderCategories(arg=None):
    '''
    Button: Refresh and called after create new category.
    Builds list of shader categories.
    '''
    shaderCategoriesSL = "shaderCategoriesSL"

    selectedCategory = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True)
    
    # Initialize list.
    cmds.textScrollList(shaderCategoriesSL, edit=True, removeAll=True)
    cmds.textScrollList(shaderCategoriesSL, edit=True, append="-- UNFILED --")
    
    # Get categories from disk and add to displayed list.
    categories = getShaderCategories()
    cmds.textScrollList(shaderCategoriesSL, edit=True, append=categories)
    
    # Refresh the swatch display using the previously selected category or default UNFILED category.
    if selectedCategory:
        cmds.textScrollList(shaderCategoriesSL, edit=True, selectItem=selectedCategory[0])
    else:
        cmds.textScrollList(shaderCategoriesSL, edit=True, selectItem="-- UNFILED --")
    doRefreshSwatchDisplay()

# end (doBuildShaderCategories)


def doCreateCategory(arg=None):
    '''Create a new category folder.
    '''
    currentShaderLibrary = getAssetShaderLibrary()
    found = False
    result = "Ok"
    categoryPath = None
    while not found and not result == "Cancel":
        result = cmds.promptDialog(
                title="Create New Category", messageAlign="center", 
                message='Enter a new category name.  ', text="", 
                button=["Ok", "Cancel"], 
                defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                )
        if result == "Cancel": 
            return
        
        # Create the new category path name.
        rootName = cmds.promptDialog(query=True, text=True)
        categoryPath = os.path.join(currentShaderLibrary, rootName)
        
        if not os.path.isdir(categoryPath):
            found = True
        else:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Category name already exists. Enter a new name.  ", 
                    button=["Ok", "Cancel"], 
                    defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirm == "Cancel":
                return
    
    if categoryPath:
        # Make the directory on disk.
        os.mkdir(categoryPath)
        # Refresh the category list.
        doBuildShaderCategories()

# end (doCreateCategory)


def doDeleteShader(arg=None):
    '''Delete the selected shader.
    '''
    # Get the selected shader.
    selectedShader = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if not selectedShader:
        sys.stdout.write("Select a shader.\n")
        return
    
    # Get the selected category folder.
    currentLocation = getCategoryFolder()
    
    # Create the file name dictionary.
    currentFile = getFileNames(shader=selectedShader, directory=currentLocation)
    
    if not os.path.isfile(currentFile["ma"]) or not os.path.isfile(currentFile["png"]):
        sys.stdout.write("Files not found for shader: %s\n" % selectedShader)
        return
        
    confirmDelete = cmds.confirmDialog(
            title="Warning", messageAlign="center", 
            message="You are about to delete an existing shader which might be in use.  ", 
            button=[" Continue to Delete ", "Cancel"], 
            defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
            )
    if confirmDelete == "Cancel":
        return False
    else:
        # Delete the swatch file, image file and meta files.
        for key in ["ma", "png", "maMeta", "pngMeta"]:
            if os.path.isfile(currentFile[key]):           
                os.remove(currentFile[key])
        sys.stdout.write('Shader "%s" has been deleted.\n' % (selectedShader))
        
    # Refresh the swatch display.
    doRefreshSwatchDisplay()

# end (doDeleteShader)


def doImportShaders(arg=None):
    '''
    Button: Import Shader.
    Imports selected shader from library if does not already exist in file and
    assigns shader to selected objects.
    '''
    selectedCategory = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True)

    selection = cmds.ls(selection=True, long=True) or []
    tempGrp = "tempImportedGrp"
    if cmds.objExists(tempGrp):
        cmds.delete(tempGrp)
        
    # Get selected swatch.
    swatch = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if not swatch:
        sys.stdout.write("Select a shader\n")
        return
    
    # Get selected category.
    directory = getCategoryFolder()
    
    # Check if selected swatch shader already exists in file.
    shadingEngine = "%s_SG" % swatch
    shader = "%s_SHD" % swatch
    
    validTexture = False
    if cmds.objExists(shadingEngine):
        meshList = [x for x in (cmds.listHistory(shadingEngine) or []) if cmds.nodeType(x) == "mesh"]
        if meshList:
            meshTransform = cmds.listRelatives(meshList[0], path=True, parent=True)[0]
            validTexture = ddCheckTexturePublished.do(nodes=meshTransform, confirm=False, assetCategory=selectedCategory)
        
    if cmds.objExists(shadingEngine) and cmds.objExists(shader) and validTexture:
        if selection:
            # Apply existing shader to selection.
            sys.stdout.write('Shader "%s_SG" already exists. Applying to selection... \n' % swatch)
            for sel in selection:
                selShape = sel
                if not (cmds.nodeType(sel) == "mesh"):
                    selShape = cmds.listRelatives(sel, shapes=True, path=True)
                    if selShape:
                        selShape = selShape[0]
                if selShape:
                    cmds.sets(selShape, forceElement=shadingEngine)
        else:
            sys.stdout.write('Shader "%s_SG" already exists. Skipping... \n' % swatch)
            
    else:
        meshList = list()
        connectedSurfaceShader = None
        # If shader has been deleted from Hypershade, shading engine and other nodes must also be deleted.
        if cmds.objExists(shadingEngine):
            meshList = [x for x in (cmds.listHistory(shadingEngine) or []) if cmds.nodeType(x) == "mesh"]
            connectedSurfaceShader = cmds.listConnections("%s.surfaceShader" % shadingEngine)
            cmds.delete(shadingEngine)
            
        if cmds.objExists(shader):
            connectedShadingEngine = cmds.listConnections("%s.outColor" % shader)
            if connectedShadingEngine:
                meshList = [x for x in (cmds.listHistory(connectedShadingEngine[0]) or []) if cmds.nodeType(x) == "mesh"]
            cmds.delete(shader)
            
        if connectedSurfaceShader and cmds.objExists(connectedSurfaceShader[0]):
            cmds.delete(connectedSurfaceShader[0])
        deleteNodes = cmds.ls("%s_*DIFF*" % swatch, "%s_*SPEC*" % swatch, "%s_*NRML*" % swatch)
        try:
            cmds.delete(deleteNodes)
        except: pass
        
        # Get the path to swatch file.
        fileName = os.path.join(directory, "%s.ma" % swatch)
        if os.path.isfile(fileName):
            # Import swatch file into tempGrp.
            cmds.file(fileName, i=True, groupReference=True, groupName=tempGrp)
            if cmds.objExists(tempGrp):
                # Remove any namespaces from imported nodes.
                tempGrp = ddRemoveNamespaces.doRemoveNamespaces(tempGrp)
                # Children consists of one swatch plane.
                children = cmds.listRelatives(tempGrp, children=True, path=True)
                if children:
                    # Get the connected shading engine.
                    shadingEngine = getConnectedShadingEngine(children[0])
                    meshList.extend(selection)
                    if shadingEngine:
                        # Assign shader to selected objects.
                        for sel in meshList:
                            selShape = sel
                            if not (cmds.nodeType(sel) == "mesh"):
                                selShape = cmds.listRelatives(sel, shapes=True, path=True)
                                if selShape:
                                    selShape = selShape[0]
                            if selShape:
                                cmds.sets(selShape, forceElement=shadingEngine)
                    else:
                        sys.stdout.write("Swatch shader for %s not found. Skipping...\n" % swatch)
                    
                    # Change the button font to oblique for imported shader.
                    try:
                        cmds.iconTextCheckBox("%sBTN" % swatch, edit=True, font = "obliqueLabelFont")
                    except: pass
                else:
                    sys.stdout.write("Swatch mesh for %s not found. Skipping...\n" % swatch)
                    
                cmds.delete(tempGrp)
            else:
                sys.stdout.write("Shader did not load properly. \n" % fileName)
        else:
            sys.stdout.write("Swatch file %s not found. Skipping... \n" % fileName)
    
    # Deselect the shader.
    deselectAll()
    
    # Reselect original selection.
    if selection:
        cmds.select(selection, replace=True)

# end (doImportShaders)


def doMoveShaderToFolder(newCategory, arg=None):
    '''
    Move selected shader into a category folder.
    @param newCategory: Category folder to move shader into.
    '''
    currentShaderLibrary = getAssetShaderLibrary()
    
    if newCategory == "--> To Move Shader, Select A Folder":
        return
    
    # Get selected shader.
    selectedShader = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if not selectedShader:
        sys.stdout.write("Select a shader.\n")
        return
    
    # Get selected category folder.
    currentLocation = getCategoryFolder()
    
    # Get the destination category folder.
    newLocation = os.path.join(currentShaderLibrary, newCategory)
    if newCategory == "-- UNFILED --":
        newLocation = currentShaderLibrary
        
    if not os.path.isdir(newLocation):
        sys.stdout.write("Directory does not exist: %s\n" % newLocation)
        return
    
    # Create the filename dictionaries.
    currentFile = getFileNames(shader=selectedShader, directory=currentLocation)
    newFile = getFileNames(shader=selectedShader, directory=newLocation)
    
    if os.path.isfile(newFile["ma"]) or os.path.isfile(newFile["png"]):
        # Shader already exists in new category.
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='Shader with same name already exists in category "%s".  ' % newCategory, 
                button=[" Move and Rename ", "Overwrite", "Cancel"], 
                defaultButton=" Move and Rename ", cancelButton="Cancel", dismissString="Cancel"
                )
        
        if confirm == "Cancel": return
        
        elif confirm == "Overwrite":
            confirmOverwrite = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Overwrite an existing shader which might be in use?  ", 
                    button=[" Continue to Overwrite ", "Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirmOverwrite == "Cancel": return
            else:
                # Overwrite currently existing shader.
                moveShader(currentFile, newFile)
                
        elif confirm == " Move and Rename ":
            found = False
            result = "Ok"
            newShaderName = ""
            while not found and not result == "Cancel":
                result = cmds.promptDialog(
                        title="Rename Shader", messageAlign="center", 
                        message='Enter a new shader name.  ', text=selectedShader, 
                        button=["Rename", "Cancel"], 
                        defaultButton="Rename", cancelButton="Cancel", dismissString="Cancel"
                        )
                if result == "Cancel": return
                
                # Get new shader name.
                newShaderName = cmds.promptDialog(query=True, text=True)
                # Create the new file name dictionary.
                newFile = getFileNames(shader=newShaderName, directory=newLocation)
                
                if not os.path.isfile(newFile["ma"]) and not os.path.isfile(newFile["png"]):
                    found = True
                else:
                    # New shader name already exists.
                    confirmName = cmds.confirmDialog(
                            title="Warning", messageAlign="center", 
                            message='Shader name "%s" already exists in category "%s". Enter a new name.  ' % (newShaderName, newCategory), 
                            button=["Ok", "Cancel"], 
                            defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                            )
                    if confirmName == "Cancel": return
            
            confirmMoveAndRename = cmds.confirmDialog(
                    title="Confirm", messageAlign="center", 
                    message="Rename an existing shader which might be in use?  ",
                    button=[" Continue to Rename ", "Cancel"], 
                    defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                    )
            if confirmMoveAndRename == "Cancel":
                return
            else:
                # Move and rename the shader.
                done = renameShaderNodes(selectedShader, newShaderName, currentFile["ma"])
                moveShader(currentFile, newFile)
    else:
        confirmMove = cmds.confirmDialog(
                title="Confirm", messageAlign="center", 
                message='Move %s to the %s category?  ' % (selectedShader, newCategory), 
                button=[" Continue to Move ", "Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel" 
                )
        if confirmMove == "Cancel": return
        
        # Move the shader.
        moveShader(currentFile, newFile)
    
    # Refresh the swatch display.
    doRefreshSwatchDisplay()

# end (doMoveShaderToFolder)


def doPublishShader(arg=None):
    '''
    Button: Publish Shader.
    Publish the selected shader and rebuild the shaders display window.
    '''
    ddPublishShader.do()
    doRefreshSwatchDisplay()

# end (doPublishShader)


def doRefreshSwatchDisplay(arg=None):
    '''Display swatches for selected category.
    '''
    # Get selected category folder.
    directory = getCategoryFolder()
    
    # Get the list of files on disk.
    swatchFiles = [x for x in os.listdir(directory) if x.endswith(".png")]
    
    clearShadersDispay()
    for swatch in swatchFiles:
        # Build the buttons. 
        swatchLabel = swatch.rpartition(os.sep)[2].replace(".png", "")
        imageFilePath = os.path.join(directory, swatch)
        button = cmds.iconTextCheckBox(
                "%sBTN" % swatchLabel, parent="displaySwatchesGL", style="iconAndTextVertical", 
                width=144, height=144, image=imageFilePath, label=swatchLabel, 
                onCommand=partial(addSwatchToSelection, swatchLabel), 
                offCommand=partial(removeSwatchFromSelection, swatchLabel)
                )
        # If shader exists in file, set display font to oblique.
        if cmds.objExists("%s_SG" % swatchLabel):
            cmds.iconTextCheckBox("%sBTN" % swatchLabel, edit=True, font="obliqueLabelFont")
    
    # Build the move to list for this category.
    doBuildMoveToList()
    # Clear hidden textField.
    cmds.textField("currentlySelectedTFD", edit=True, text="")

# end (doRefreshSwatchDisplay)


def doRemoveShaders(arg=None):
    '''
    Button: Remove Shaders.
    Removes unused Shader Library shaders from scene file.
    '''
    # Get selected shader
    swatches = cmds.textField("currentlySelectedTFD", query=True, text=True)
    
    # If no selected shader, select all of them.
    swatchShadingEngines = cmds.ls("*_SG", type="shadingEngine")
    for shadingEngine in swatchShadingEngines:
        # Get connected meshes.
        meshList = [x for x in (cmds.listConnections(shadingEngine) or []) if cmds.listRelatives(x, shapes=True)]
        if not meshList:
            # If shader not connected to a mesh, find connected shading network nodes and delete.
            historyNodes = [x for x in (cmds.listHistory(shadingEngine) or []) if not cmds.nodeType(x) == "mesh"]
            for node in historyNodes:
                try:
                    cmds.delete(node)
                except:
                    pass
            sys.stdout.write('Removed "%s".\n' % shadingEngine)
            
    # Deselect any selected shader
    deselectAll()
    
    # Rebuild the shaders display window.
    doRefreshSwatchDisplay()

# end (doRemoveShaders)


def doRenameShader(arg=None):
    '''Rename selected shader.
    '''
    # Get selected shader.
    selectedShader = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if not selectedShader:
        sys.stdout.write("Select a shader.\n")
        return
        
    # Get selected category folder.
    currentLocation = getCategoryFolder()
    
    # Create the file name dictionary.
    currentFile = getFileNames(shader=selectedShader, directory=currentLocation)
    if not os.path.isfile(currentFile["ma"]) or not os.path.isfile(currentFile["png"]):
        sys.stdout.write("Files not found for shader: %s\n" % selectedShader)
        return
        
    newFile = dict()
    found = False
    result = "Ok"
    newShaderName = ""
    while not found and not result == "Cancel":
        result = cmds.promptDialog(
                title="Rename Shader", messageAlign="center", 
                message='Enter a new shader name.  ', 
                text=selectedShader, button=["Rename", "Cancel"], 
                defaultButton="Rename", cancelButton="Cancel", dismissString="Cancel"
                )
        if result == "Cancel":
            return
        
        # Get the new shader name and create the file name dictionary.
        newShaderName = cmds.promptDialog(query=True, text=True)
        newFile = getFileNames(shader=newShaderName, directory=currentLocation)
        
        if not os.path.isfile(newFile["ma"]) and not os.path.isfile(newFile["png"]):
            found = True
        else:
            if newShaderName == selectedShader:
                # New name is old name.
                confirmName = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message='New name is same as old name. Enter a new name.  ', 
                    button=["Ok", "Cancel"], 
                    defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                    )
                if confirmName == "Cancel": 
                    return
            else:
                # Shader name already exists.
                confirmName = cmds.confirmDialog(
                        title="Warning", messageAlign="center", 
                        message='Shader name "%s" already exists. Enter a new name.  ' % newShaderName, 
                        button=["Ok", "Cancel"], 
                        defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                        )
                if confirmName == "Cancel": 
                    return
                
    confirmRename = cmds.confirmDialog(
            title="Warning", messageAlign="center", 
            message="You are about to rename an existing shader which might be in use.  ", 
            button=[" Continue to Rename ", "Cancel"], 
            defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
            )
    if confirmRename == "Cancel": 
        return
    else:
        done = renameShaderNodes(selectedShader, newShaderName, currentFile["ma"])

        # Rename the swatch file, image file and meta files.
        for key in ["ma", "png", "maMeta", "pngMeta"]:
            if os.path.isfile(currentFile[key]):
                os.rename(currentFile[key], newFile[key])
                
        sys.stdout.write('Shader "%s" has been renamed to "%s".\n' % (selectedShader, newFile["ma"].replace(".ma", "")))
        
    # Refresh the swatch display.
    doRefreshSwatchDisplay()

# end (doRenameShader)


def getAssetShaderLibrary(arg=None):
    '''Get selected asset category and return corresponding shader directory.
    '''
    selected = cmds.optionMenu("assetCategoryMenu", query=True, select=True)
    assetCategory = ddConstants.ASSET_CATEGORIES[selected-1]
    currentShaderLibrary = ddConstants.SHADER_DIRECTORIES[assetCategory]
    
    return currentShaderLibrary

# end (getAssetShaderLibrary)


def getCategoryFolder(arg=None):
    '''Returns selected category folder path.
    '''
    currentShaderLibrary = getAssetShaderLibrary()
    # Get selected category.
    category = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True)
    # If no category, use shaderLibrary directory.
    directory = currentShaderLibrary
    if category:
        category = category[0]
        if not (category == "-- UNFILED --"):
            # If category, create folder path.
            directory = os.path.join(currentShaderLibrary, category)
            
    return directory

# end (getCategoryFolder)


def getConnectedShadingEngine(node):
    '''Returns connected shading engine.
    '''
    # Get shape node.
    shapeNode = cmds.listRelatives(node, shapes=True, path=True)
    if shapeNode: 
        # Get shading engine connections.
        shadingEngines = cmds.listConnections(shapeNode[0], type="shadingEngine") or []
        if shadingEngines:
            return shadingEngines[0]
            
    return None

# end (getConnectedShadingEngine)


def getFileNames(shader, directory):
    '''Returns dictionary of shader file names for moving, renaming and deleting.
    '''
    current = dict()
    current["ma"] = os.path.join(directory, "%s.ma" % shader)
    current["png"] = os.path.join(directory, "%s.png" % shader)
    current["maMeta"] = os.path.join(directory, "%s.ma.meta" % shader)
    current["pngMeta"] = os.path.join(directory, "%s.png.meta" % shader)
    
    return current

# end (getFileNames)


def getShaderCategories(arg=None):
    '''Returns list of categories in shaderLibrary on disk.
    '''
    currentShaderLibrary = getAssetShaderLibrary()
    categories = [ x for x in (os.listdir(currentShaderLibrary) or []) if os.path.isdir(os.path.join(currentShaderLibrary, x)) 
               and not x.startswith(".") and not x in ["Keyboard", "Materials", "_Materials"] ]
               
    return categories

# end (getShaderCategories)


def moveShader(currentFile, newFile):
    ''' 
    Move the ".ma", ".png", ".ma.meta" and ".png.meta" files from one category folder to another.
    @param currentFile: Dictionary created by getFileNames.
    @param newFile: Dictionary created by getFilenames.    
    '''
    shaderName = currentFile["ma"].rpartition(os.sep)[2].replace(".ma", "")
    newDirectory = newFile["ma"].rpartition(os.sep)[0]
    
    for key in ["ma", "png", "maMeta", "pngMeta"]:
        # Check if file exists.
        if os.path.isfile(currentFile[key]):
            if not (currentFile[key] == newFile[key]):
                # Move the file if not already in correct location.
                shutil.move(currentFile[key], newFile[key])
                
    sys.stdout.write('Shader "%s" has been moved to "%s".\n' % (shaderName, newDirectory))

# end (moveShader)


def removeSwatchFromSelection(swatchName, arg=None):
    '''Removes name of selected swatch from hidden textField to prevent multi-selection.
    '''
    # Get name of last selected swatch.
    swatch = cmds.textField("currentlySelectedTFD", query=True, text=True)
    if swatch == swatchName:
        # Reset hidden textField.
        cmds.textField("currentlySelectedTFD", edit=True, text="")

# end (removeSwatchFromSelection)


def renameShaderNodes(oldSwatchName, newSwatchName, swatchPath):
    '''Renames shader nodes in the .ma file.
    '''
    tokens = ["_SG", "_SHD", "_DIFF", "_SPEC", "_NRML", ".ma", "_Swatch"]
    tifDir = os.path.join(ddConstants.ASSETLIBRARY, "tex", "tif").replace(os.sep, "/")
    
    # Work in a temp file. 
    outputPath = swatchPath.replace(".ma", "_o.ma")
    
    f = open(swatchPath, "r")
    o = open(outputPath, "w")
    for line in f:
        newLine = line
        if tifDir in line:
            filename = line.rpartition(tifDir)[2].rpartition('"')[0].rpartition("/")[2]  # dirtLight_DIFF_SL.tif
            newFilename = filename.replace(oldSwatchName, newSwatchName)
            shutil.move(os.path.join(tifDir, filename), os.path.join(tifDir, newFilename))
        for token in tokens:
            newLine = newLine.replace("%s%s" % (oldSwatchName, token), "%s%s" % (newSwatchName, token))
        o.write(newLine)
        
    f.close()
    o.close()
    
    # Move temp file over to original file.
    shutil.move(outputPath, swatchPath)
    
    return True

# end (renameShaderNodes)


def showShaderLibraryHelp(arg=None):
    '''Builds the help window.
    '''
    if cmds.window("shaderLibraryHelpWIN", query=True, exists=True):
        cmds.deleteUI("shaderLibraryHelpWIN")

    # Window.
    helpWindow = cmds.window(
            "shaderLibraryHelpWIN", title="Shader Library Help", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    helpFL = cmds.formLayout("shaderLibraryHelpFL", numberOfDivisions=100, parent=helpWindow)
    helpSF = cmds.scrollField("shaderLibraryHelpSF", editable=False, wordWrap=True, text='SHADER LIBRARY HELP\n\nSelect an asset type from the drop down menu to display the correct Shader Library. The available shader categories will be displayed in the left column. Right click in this column to create new categories.\n\n\n' )

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='Select a category from the left column to display available shaders or to publish a shader into the category. Left click on a swatch to select it. Right click on a selected swatch to move the shader to a different category. With a swatch selected, ctrl right click to rename or delete the shader.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText=' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Import Shader\nImports the selected shader and applies to selected meshes.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Remove Shaders\nIf a selected shader has already been imported into the scene file but is not attached to a mesh, it will be removed from the scene file. If no shaders are selected, this button will attempt to remove any unused Shader Library shaders from the scene file.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Publish Shaders\nPublishes the selected shader or the shader connected to the selected mesh into the currently visible Shader Library category. After entering a name for the shader, a dialog box will appear with the option of checking if a similar shader has already been published. "Continue With Check" will run a pixel comparison of the connected tif files to the published tif files for that category. If a match is found, a dialog box will appear naming the existing shader and providing the option of publishing the duplicate shader or cancelling the publish to import the already existing version.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Refresh\nRefreshes the category list and displayed shaders window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

    cmds.formLayout(helpFL, edit=True, 
        attachForm=[ (helpSF, "top", 15), 
                     (helpSF, "left", 15), 
                     (helpSF, "right", 15),
                     (helpSF, "bottom", 15)])

    window = cmds.window("shaderLibraryHelpWIN", edit=True, widthHeight=(700, 720))

    cmds.showWindow(helpWindow)
    
# end (showShaderLibraryHelp)


def do(defaultCategory="environments"):
    '''Builds the window.
    '''
    
    # Delete or close any existing Shader Library window.
    closeWindow()
    
    # Reset the default namespace to root.
    cmds.namespace(setNamespace=":")    
    
    window = cmds.window(
            "ShaderLibraryWIN", title="Shader Library", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(800, 450)
            )
    
    mainFL = cmds.formLayout("ShaderLibraryFL", numberOfDivisions=100)
    assetCategoryRL = cmds.rowLayout("assetCategoryRL", parent=mainFL)
    cmds.optionMenu("assetCategoryMenu", label="Asset Type ", changeCommand=partial(doBuildShaderCategories), parent=assetCategoryRL)
    for assetCategory in ddConstants.ASSET_CATEGORIES:
        cmds.menuItem("%sMI" % assetCategory, label=assetCategory)
    cmds.optionMenu("assetCategoryMenu", edit=True, value=defaultCategory)
    
    mainPL = cmds.paneLayout(
            "ShaderLibraryPL", configuration="vertical2", paneSize=[1,25,100], parent=mainFL
            )
    shaderCategoriesSL = cmds.textScrollList(
            "shaderCategoriesSL", parent=mainPL, selectCommand=partial(doRefreshSwatchDisplay)
            )
    displaySwatchesSL = cmds.scrollLayout(
            "displaySwatchesSL", childResizable=True, parent=mainPL, 
            resizeCommand=partial(doAdjustGridSize)
            )
    displaySwatchesGL = cmds.gridLayout(
            "displaySwatchesGL", cellWidthHeight=(165, 180), 
            numberOfColumns=4, parent=displaySwatchesSL
            )
    
    categoriesMenu = cmds.popupMenu("categoriesMenu", parent=shaderCategoriesSL)
    cmds.menuItem(p=categoriesMenu, l="Create New Category", c=partial(doCreateCategory))
    
    swatchesMenu = cmds.popupMenu('displaySwatchesMenu', parent=displaySwatchesGL)
    cmds.menuItem(p=swatchesMenu, l="--> To Move Shader, Select A Folder")
    
    swatchesOptionMenu = cmds.popupMenu(
            "displaySwatchesOptionMenu", ctrlModifier=True, parent=displaySwatchesGL
            )
    
    cmds.menuItem(p=swatchesOptionMenu, l="Rename Shader", c=partial(doRenameShader))
    cmds.menuItem(p=swatchesOptionMenu, l="Delete Shader", c=partial(doDeleteShader))
    
    importShadersBTN = cmds.button(
            "importShadersBTN", label="Import Shader", height=30, 
            annotation="Imports selected shaders or all shaders if no selection. Applies shader to selected object(s).", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doImportShaders)
            )
    removeShadersBTN = cmds.button(
            "removeShadersBTN", label="Remove Shaders", height=30, 
            annotation="Removes selected shaders or all unused library shaders if no selection.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doRemoveShaders)
            )
    publishShaderBTN = cmds.button(
            "publishShaderBTN", label="Publish Shader", height=30, 
            annotation="Publish shader from selected mesh to shader library", parent=mainFL, 
            backgroundColor=[0.28, 0.337, 0.375], c=partial(doPublishShader)
            )
    refreshShadersBTN = cmds.button(
            "refreshShadersBTN", label="Refresh", height=30, annotation="Refresh display", parent=mainFL, 
            backgroundColor=[0.28, 0.337, 0.375], c=partial(doBuildShaderCategories)
            )
    shadersHelpWindowBTN = cmds.button(
            "shadersHelpWindowBTN", label="Help", height=30, annotation="Show instructions and other information.", 
            parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(showShaderLibraryHelp)
            )
    currentlySelectedTFD = cmds.textField("currentlySelectedTFD", text="", visible=False, parent=mainFL)
    
    r1 = 89
    c1 = 20
    c2 = 40
    c3 = 60
    c4 = 80
    
    cmds.formLayout(mainFL, edit=True, 
        attachPosition=[ (assetCategoryRL, "top", 15, 0),
                         (mainPL, "top", 45, 0), 
                         (importShadersBTN, "bottom", 15, 100),
                         (removeShadersBTN, "bottom", 15, 100),
                         (publishShaderBTN, "bottom", 15, 100),
                         (refreshShadersBTN, "bottom", 15, 100),
                         (shadersHelpWindowBTN, "bottom", 15, 100),
                         
                         (assetCategoryRL, "left", 12, 0), (assetCategoryRL, "right", 12, 100),
                         (mainPL, "left", 12, 0), (mainPL, "right", 12, 100),
                         (importShadersBTN, "left", 12, 0), (importShadersBTN, "right", 3, c1),
                         (removeShadersBTN, "left", 3, c1), (removeShadersBTN, "right", 3, c2),
                         (publishShaderBTN, "left", 3, c2), (publishShaderBTN, "right", 3, c3),
                         (refreshShadersBTN, "left", 3, c3), (refreshShadersBTN, "right", 3, c4), 
                         (shadersHelpWindowBTN, "left", 3, c4), (shadersHelpWindowBTN, "right", 12, 100) 
                         ],
        attachControl=[ (mainPL, "bottom", 15, importShadersBTN) ]
        )
    
    window = cmds.window("ShaderLibraryWIN", edit=True, widthHeight=(800, 600))
    
    # Build the categories list and refresh the swatch display.
    doBuildShaderCategories()
    
    cmds.showWindow(window)
    
# end do()
