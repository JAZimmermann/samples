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
# $Date: 2014-06-12$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddTextureManager.py

DESC
    Displays shaders attached to child meshes of selected group node.
    Displays locations of texture files.

USAGE
    ddTextureManager.do()

FUNCTIONS
    doBuildShadingEnginesList()
    doClearShaderDisplay()
    doClearTextureDisplay()
    doCloseWindow()
    doDisplayShadersList()
    doDisplayTexturesList()
    doOpenShaderLibrary()
    doRefreshShadersDisplay()
    doRefreshTexturesDisplay()
    doReplaceShader()
    doSelectShaders()
    doShowShadersForSelection()
    getAllShadingEngines()
    getConnectedShadingEngine()
    getCurrentNodeList()
    getFileTextureData()
    getSelectedShader()
    getSelectedTexture()
    getShaderData()
    getTopGrpOfNode()
    showTextureManagerHelp()
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
from functools import partial

# VAD
import ddConstants; reload(ddConstants)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddRemoveFromObjectSets; reload(ddRemoveFromObjectSets)
import ddCheckNames; reload(ddCheckNames)
import ddShaderLibrary; reload(ddShaderLibrary)
import ddCheckTexturePublished; reload(ddCheckTexturePublished)


def doBuildShadingEnginesList(arg=None):
    '''Builds list of all shading engines in scene file.
    '''
    shadersMenu = "displayShadersMenu"
    displayShaderSL = "displayShaderSL"
    
    # Initialize shading engines list
    shadingEngines = getAllShadingEngines()
    for shadingEngine in shadingEngines:
        cmds.menuItem(p=shadersMenu, l=shadingEngine, c=partial(doReplaceShader, shadingEngine))

# end (doBuildShadingEnginesList)
     
        
def doClearShaderDisplay(arg=None):
    '''Clears the upper portion of the display window.
    '''
    cmds.textScrollList("displayShaderSL", edit=True, removeAll=True)
    doClearTextureDisplay()

# end (doClearShaderDisplay)


def doClearTextureDisplay(arg=None):
    '''Clears the lower portion of the display window.
    '''
    cmds.textScrollList("displayTextureSL", edit=True, removeAll=True)

# end (doClearTextureDisplay)


def doCloseWindow(arg=None):
    '''Closes the windows.
    '''
    if cmds.window("textureManagerWIN", query=True, exists=True):
        cmds.deleteUI("textureManagerWIN")
    if cmds.window("textureManagerHelpWIN", query=True, exists=True):
        cmds.deleteUI("textureManagerHelpWIN")

# end (doCloseWindow)


def doDisplayShadersList(nodeList):
    '''Displays the GEO names and assigned shaders in the upper portion of the display window.
    '''
    displayShaderSL = "displayShaderSL"
    doClearShaderDisplay()
    if nodeList:
        nodeList.sort()
        cmds.textScrollList(displayShaderSL, edit=True, append=nodeList)
        for i in range(len(nodeList)):
            node, shader = nodeList[i].split("    -->    ")
            published = True
            if shader == "None":
                published = False
            else:
                published = ddCheckTexturePublished.doCheckTexturePublished(node=node, verbose=False)
            if published:
                cmds.textScrollList(displayShaderSL, edit=True, lineFont=[i+1, "obliqueLabelFont"])
    else:
        cmds.textScrollList(displayShaderSL, edit=True, append=["No nodes found"])
        
# end (doDisplayShadersList)


def doDisplayTexturesList(shadingEngines):
    '''Displays the file nodes and connected texture file locations in the lower portion of the display window.
    '''
    displayTextureSL = "displayTextureSL"
    doClearTextureDisplay()
    if not shadingEngines: return

    shadingEngines, fileNodes, attrs, fileTextureNames, publishedList = getFileTextureData(shadingEngines)
    texturesList = list()
    for shadingEngine, fileNode, attr, fileTextureName, published in zip(shadingEngines, fileNodes, attrs, fileTextureNames, publishedList):
        texturesList.append("%s  --  %s (%s)  --  %s" % (shadingEngine, fileNode, attr, fileTextureName))
    if texturesList:
        texturesList.sort()
        cmds.textScrollList(displayTextureSL, edit=True, append=texturesList)
    else:
        cmds.textScrollList(displayTextureSL, edit=True, append=["No nodes found"])

# end (doDisplayTexturesList)


def doOpenShaderLibrary(arg=None):
    '''Opens the Shader Library window.
    '''
    ddShaderLibrary.do()

# end (doOpenShaderLibrary)


def doRefreshShadersDisplay(arg=None):
    '''Refreshes the display of the GEO nodes and assigned shaders in the upper portion of the display window.
    '''
    currentTopNodes = getCurrentNodeList()
    if not currentTopNodes: return
    
    geoNodes, shaders = getShaderData(currentTopNodes)
    nodeAndShaderList = list()
    for geoNode, shader in zip(geoNodes, shaders):
        shadingEngine = getConnectedShadingEngine(geoNode)
        nodeAndShaderList.append("%s    -->    %s" % (geoNode, shader))
    
    doDisplayShadersList(nodeAndShaderList)
    doBuildShadingEnginesList()

# end (doRefreshShadersDisplay)

    
def doRefreshTexturesDisplay(arg=None):
    '''Refreshes the display of the file nodes and connected texture file locations in the lower portion of the display window.
    '''
    shapeNodeList, shadingEngineList = getSelectedShader()
    if shadingEngineList:
        doDisplayTexturesList(shadingEngineList)

# end (doRefreshTexturesDisplay)


def doReplaceShader(shader, arg=None):
    '''Assign another shader to the GEO nodes in the selected line(s).
    '''
    shapeNodes, shaders = getSelectedShader()
    for shapeNode in shapeNodes:
        if shapeNode and shader:
            cmds.sets(shapeNode, forceElement=shader)
    doRefreshShadersDisplay()

# end (doReplaceShader)


def doSelectShaders(arg=None):
    '''Selects listed item in scene file.
    '''
    shapeNodes, shadingEngines = getSelectedShader()
    if shapeNodes:
        try:
            cmds.select(shapeNodes, replace=True)
            doDisplayTexturesList(shadingEngines)
        except:
            pass
            
# end (doSelectShaders)


def doShowShadersForSelection(nodes=None, arg=None):
    '''Button: Show Shaders For Selection.
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
    
    # Get the top GRP node of selected node.
    nodeList = getTopGrpOfNode(nodes)
    nodeList = list(set(nodeList))
    
    nodeStr = ""
    for node in nodeList:
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            nodeStr = "%s, " % node
        else:
            sys.stdout.write("Node %s is referenced. Skipping... \n" % node)
            
    cmds.textField("currentNodesTFD", edit=True, text=nodeStr[:-2])
    doRefreshShadersDisplay()

# end (doShowShadersForSelection)


def getAllShadingEngines(arg=None):
    '''Get list of all shading engines in scene file.
    '''
    allShadingEngines = [x for x in (cmds.ls(type="shadingEngine") or []) if not x.startswith("initial")]
    return allShadingEngines

# end (getAllShadingEngines)


def getConnectedShadingEngine(node):
    '''Returns connected shading engine.
    '''
    shapeNode = cmds.listRelatives(node, shapes=True, path=True)
    if shapeNode: 
        shadingEngines = cmds.listConnections(shapeNode[0], type="shadingEngine") or []
        shadingEngines = list(set(shadingEngines))
        if shadingEngines:
            return shadingEngines[0]
    return None

# end (getConnectedShadingEngine)


def getCurrentNodeList(arg=None):
    '''Returns list of nodes in current selection.
    '''
    currentNodesStr = cmds.textField("currentNodesTFD", query=True, text=True)
    if not currentNodesStr: 
        return None
    currentNodes = currentNodesStr.split(", ")
    return currentNodes

# end (getCurrentNodeList)


def getFileTextureData(shadingEngines):
    '''Gets the connected file nodes and file texture files.
    '''
    shadingEngineList = list()
    fileNodes = list()
    attrs = list()
    fileTextureNames = list()
    publishedList = list()
    
    for shadingEngine in shadingEngines:
        historyList = cmds.listHistory(shadingEngine) or []
        fileNodesInHistory = [x for x in historyList if cmds.nodeType(x) == "file"] or []
        for fileNode in fileNodesInHistory:
            published = ""
            fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
            fileTextureName = fileTextureName.replace("/", os.sep)
            if fileTextureName.startswith(ddConstants.ASSETLIBRARY):
                published = "    (Published in AssetLibrary)"
                fileTextureName = fileTextureName.replace(ddConstants.ASSETLIBRARY, "ASSETLIBRARY")
                
            # Determine shader attribute file node is connected to
            surfaceShader = cmds.listConnections("%s.surfaceShader" % shadingEngine)
            if surfaceShader:
                surfaceShader = surfaceShader[0]
                cnxList = cmds.listConnections(fileNode, source=False, destination=True, plugs=True) or []
                fileNodeCnx = [x for x in cnxList if surfaceShader in x or "bumpValue" in x]
                
                if fileNodeCnx:
                    for nodeCnx in fileNodeCnx:
                        attr = nodeCnx.partition(".")[2]
                        if attr in ddConstants.textureTypes.keys():
                            shadingEngineList.append(shadingEngine)
                            fileNodes.append(fileNode)
                            attrs.append(ddConstants.textureTypes[attr])
                            fileTextureNames.append(fileTextureName)
                            publishedList.append(published)
                            
    return shadingEngineList, fileNodes, attrs, fileTextureNames, publishedList

# end (getFileTextureData)


def getSelectedShader(arg=None):
    '''Returns selected shape nodes and shading engines.
    '''
    displayShaderSL = "displayShaderSL"
    selectedItems = cmds.textScrollList(displayShaderSL, query=True, selectItem=True) or []
    shapeNodeList = list()
    shadingEngineList = list()
    for selectedItem in selectedItems:
        node, shadingEngine = selectedItem.split("    -->    ")
        shapeNode = cmds.listRelatives(node, shapes=True, path=True)
        if shapeNode:
            shapeNodeList.append(shapeNode[0])
            shadingEngineList.append(shadingEngine)
        
    return shapeNodeList, shadingEngineList

# end (getSelectedShader)


def getSelectedTexture(arg=None):
    '''Returns selected item from list. Not used at present.
    '''
    displayTextureSL = "displayTextureSL"
    selectedItems = cmds.textScrollList(displayTextureSL, query=True, selectItem=True) or []
    shadingEngineList = list()
    fileNodeList = list()
    channelList = list()
    textureFileList = list()
    publishedList = list()
    for selectedItem in selectedItems:
        shader, fileChannel, textureFile = selectedItem.split("  --  ")
        fileNode, channel = fileChannel.split(" ")
        channel = channel.replace("(", "").replace(")", "")
        published = False
        if textureFile.endswith("    (Published in AssetLibrary)"):
            textureFile = textureFile.replace("    (Published in AssetLibrary)", "")
            published = True
        shadingEngineList.append(shader)
        fileNodeList.append(fileNode)
        channelList.append(channel)
        textureFileList.append(textureFile)
        publishedList.append(published)
        
    return shadingEngineList, fileNodeList, channelList, textureFileList, publishedList

# end (getSelectedTexture)


def getShaderData(nodes):
    '''Returns the list of GEO nodes and connected shading engines.
    '''
    geoNodes = list()
    shaders = list()
    for node in nodes:
        meshList = cmds.listRelatives(node, path=True, allDescendents=True, type="mesh") or []
        for mesh in meshList:
            meshTransform = cmds.listRelatives(mesh, parent=True, path=True)
            if meshTransform:
                geoNodes.append(meshTransform[0])
    geoNodes = list(set(geoNodes))
    geoNodes.sort()
    
    for geoNode in geoNodes:
        shadingEngine = getConnectedShadingEngine(geoNode)
        shaders.append(shadingEngine)
        
    return geoNodes, shaders

# end (getShaderData)


def getTopGrpOfNode(nodes):
    '''Returns top groups of nodes.
    '''
    nodeList = list()
    for node in nodes:
        if not "|" in node:
            node = cmds.ls(node, long=True)[0]
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
                    if searchPath == "|":
                        searchPath = None
                else:
                    nodeList.append(searchPath)
                    found = True
                    searchPath = None     
            
    nodeList = list(set(nodeList))
    
    return nodeList

# end (getTopGrpOfNode)

    
def showTextureManagerHelp(arg=None):
    '''Builds the help window.
    '''
    if cmds.window("textureManagerHelpWIN", query=True, exists=True):
        cmds.deleteUI("textureManagerHelpWIN")

    # Window.
    helpWindow = cmds.window(
            "textureManagerHelpWIN", title="Texture Manager Help", sizeable=True, 
            resizeToFitChildren=True, widthHeight=(900, 450)
            )
            
    # Main form layout.
    helpFL = cmds.formLayout("textureManagerHelpFL", numberOfDivisions=100, parent=helpWindow)
    helpSF = cmds.scrollField("textureManagerHelpSF", editable=False, wordWrap=True, text='TEXTURE MANAGER HELP\n\nSelect a GEO or GRP node and launch the tool or launch the tool first and click the Show Shaders For Selection button to display a list of GEO nodes parented under the connected GRP node and the assigned shaders. Clicking on one or more GEO lines in the upper part of the window will display the connected file nodes and texture file locations in the lower part of the window. Right click on one or more selected GEO lines to change shader assignments.\n\n\n' )

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText=' . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Shaders For Selection\nSelect a GEO or GRP node and click this button to display the list of GEO nodes parented under the connected GRP node and the assigned shaders.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Open Shader Library\nOpens the Shader Library window.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Refresh\nRefreshes the display of the GEO nodes.\n\n\n')

    cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

    cmds.formLayout(helpFL, edit=True, 
        attachForm=[ (helpSF, "top", 15), 
                     (helpSF, "left", 15), 
                     (helpSF, "right", 15),
                     (helpSF, "bottom", 15)])

    window = cmds.window("textureManagerHelpWIN", edit=True, widthHeight=(700, 500))

    cmds.showWindow(helpWindow)
    
# end (showTextureManagerHelp)


def do(nodes=None):
    '''Builds the window.
    '''
    doCloseWindow()
    cmds.namespace(setNamespace=":")    

    window = cmds.window("textureManagerWIN", title="Texture Manager", sizeable=True, resizeToFitChildren=True, widthHeight=(800, 450))
    mainFL = cmds.formLayout("textureManagerFL", numberOfDivisions=100)

    displayShaderFL = cmds.formLayout("displayShaderFL", numberOfDivisions=100, parent=mainFL)
    displayShaderSL = cmds.textScrollList("displayShaderSL", allowMultiSelection=True, parent=displayShaderFL, selectCommand=partial(doSelectShaders))
    shadersMenu = cmds.popupMenu('displayShadersMenu', parent=displayShaderSL)

    displayTextureFL = cmds.formLayout("displayTextureFL", numberOfDivisions=100, parent=mainFL)
    displayTextureSL = cmds.textScrollList("displayTextureSL", allowMultiSelection=True, parent=displayTextureFL)

    showShadersForSelectionBTN = cmds.button("showShadersForSelectionBTN", label="Show Shaders For Selection", height=30, annotation="Show shaders for selected GEO or GRP", parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doShowShadersForSelection))
    openShaderLibraryBTN = cmds.button("openShaderLibraryBTN", label="Open Shader Library", height=30, annotation="Open Shader Library", parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doOpenShaderLibrary))
    refreshTexturesBTN = cmds.button("refreshTexturesBTN", label="Refresh", height=30, annotation="Refresh display", parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(doRefreshShadersDisplay))
    textureManagerHelpBTN = cmds.button("textureManagerHelpBTN", label="Help", height=30, annotation="Show instructions and other information.", parent=mainFL, backgroundColor=[0.28, 0.337, 0.375], c=partial(showTextureManagerHelp))
    currentNodesTFD = cmds.textField("currentNodesTFD", text="", visible=False, parent=mainFL)
    
    c1 = 25
    c2 = 50
    c3 = 75
    r1 = 50
    r2 = 89
    
    cmds.formLayout(mainFL, edit=True, 
        attachPosition=[ (displayShaderFL, "top", 15, 0), (displayShaderFL, "bottom", 4, r1), 
                         (displayTextureFL, "top", 4, r1), (displayTextureFL, "bottom", 6, r2),
                         (showShadersForSelectionBTN, "top", 6, r2), (showShadersForSelectionBTN, "bottom", 15, 100),
                         (openShaderLibraryBTN, "top", 6, r2), (openShaderLibraryBTN, "bottom", 15, 100),
                         (refreshTexturesBTN, "top", 6, r2), (refreshTexturesBTN, "bottom", 15, 100),
                         (textureManagerHelpBTN, "top", 6, r2), (textureManagerHelpBTN, "bottom", 15, 100),
                         
                         (displayShaderFL, "left", 12, 0), (displayShaderFL, "right", 12, 100),
                         (displayTextureFL, "left", 12, 0), (displayTextureFL, "right", 12, 100),
                         (showShadersForSelectionBTN, "left", 12, 0), (showShadersForSelectionBTN, "right", 3, c1),
                         (openShaderLibraryBTN, "left", 3, c1), (openShaderLibraryBTN, "right", 3, c2), 
                         (refreshTexturesBTN, "left", 3, c2), (refreshTexturesBTN, "right", 3, c3), 
                         (textureManagerHelpBTN, "left", 3, c3), (textureManagerHelpBTN, "right", 12, 100) ])
                        
    cmds.formLayout(displayShaderFL, edit=True,
        attachForm = [ (displayShaderSL, "top", 0), (displayShaderSL, "left", 0), 
                       (displayShaderSL, "right", 0), (displayShaderSL, "bottom", 0) ])

    cmds.formLayout(displayTextureFL, edit=True,
        attachForm = [ (displayTextureSL, "top", 0), (displayTextureSL, "left", 0), 
                       (displayTextureSL, "right", 0), (displayTextureSL, "bottom", 0) ])
                       
    window = cmds.window("textureManagerWIN", edit=True, widthHeight=(800, 464))
    
    # Initialize current node list
    doShowShadersForSelection()

    # Initialize shading engines list
    doBuildShadingEnginesList()
    
    cmds.showWindow(window)

# end (do)
