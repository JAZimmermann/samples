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
    ddScreenGrab.py

DESC
    Saves out an image of the asset.
    
USAGE
    ddScreenGrab.do()
    
FUNCTIONS
    doScreenGrab()
    do()
    
'''


# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import re
import sys

# VAD
import ddConstants; reload(ddConstants)
import ddCheckNames; reload(ddCheckNames)


def doScreenGrab(node, currentAssetCategory="environments"):
    '''Saves out an image of the asset.
    '''
    nodeName = node.rpartition("|")[2]
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[currentAssetCategory]
    currentImageLibrary = ddConstants.IMAGE_DIRECTORIES[currentAssetCategory]
    charType = { "hero": "hero", "bg": "background", "sec": "secondary" }
    chesspieceTypes = ["CPF", "CPO", "CPD", "CPS"]
    
    invalidNodes = ddCheckNames.do(nodes=node, currentAssetCategory=currentAssetCategory)
    if invalidNodes:
        sys.stdout.write("Legalize names before taking screen grab.\n")
        return
    
    dirs = list()
    version = ""
    divider = ""
    dividerGRP = ""
    
    imagePath = currentAssetLibrary
    smallImagesPath = currentImageLibrary 
    
    if currentAssetCategory == "environments":
        dirs = nodeName.rpartition("|")[2].split("_GRP")[0].split("_")
        version = nodeName.rpartition("|")[2].split("_GRP_")[1].split("_")[0]
        
        imagePath = currentAssetLibrary
        smallImagesPath = currentImageLibrary 
        
        for i in range(len(dirs)):
            if not os.path.isdir(smallImagesPath):
                os.mkdir(smallImagesPath)
            imagePath = os.path.join(imagePath, dirs[i])
            smallImagesPath = os.path.join(smallImagesPath, dirs[i])

        imagePath = "%s_%s.jpg" % (imagePath, version)
        smallImagesPath = "%s_%s.jpg" % (smallImagesPath, version)

    elif currentAssetCategory == "characters":
        nodeSplits = nodeName.split("_")
        for nodeSplit in nodeSplits:
            if nodeSplit in chesspieceTypes:
                divider = nodeSplit
                
        dirParts = nodeName.split("_%s" % divider)[0].split("_")
        imagePath = currentAssetLibrary
        smallImagesPath = currentImageLibrary 

        dividerGRP = "%s_GRP" % divider
        version = nodeName.split("_%s_" % dividerGRP)[1].split("_")[0]

        for i in range(2):
            # eg bg (background) and buffalo
            if dirParts[i+1] in charType.keys():
                dirs.append(charType[dirParts[i+1]])
            elif re.search('^[A-Z]+', dirParts[i+1]):
                print '%s_%s' % (dirParts[i+1], dirParts[i+2])
                dirs.append('%s_%s' % (dirParts[i+1], dirParts[i+2]))
            else:
                dirs.append(dirParts[i+1])

        fileName = nodeName.rpartition("_%s" % dividerGRP)[0].replace("%s_%s_" % (dirParts[0], dirParts[1]), "")
        fileVersionName = "%s_%s_%s" % (fileName, divider, version) 
            
        for i in range(len(dirs)):
            if not os.path.isdir(smallImagesPath):
                os.mkdir(smallImagesPath)
            imagePath = os.path.join(imagePath, dirs[i])
            smallImagesPath = os.path.join(smallImagesPath, dirs[i])

        imagePath = os.path.join(imagePath, "chesspiece", "published")
        imagePath = os.path.join(imagePath, "%s.jpg" % fileVersionName)
        smallImagesPath = os.path.join(smallImagesPath.rpartition(os.sep)[0], "%s.jpg" % fileVersionName)
        
        
    cmds.select(node, replace=True)
    
    currentPanel = "modelPanel4"
    if not cmds.modelEditor(currentPanel, exists=True):
        currentPanel = cmds.getPanel(withFocus=True)
        
    mel.eval('enableIsolateSelect %s true;' % currentPanel)
    cmds.isolateSelect(currentPanel, state=1)
    mel.eval('lookThroughModelPanel persp %s' % currentPanel)
    cmds.viewFit()
    if not currentAssetCategory == "characters":
        cmds.setAttr("perspShape.preScale", 1.5)
    nearClipPlane = cmds.getAttr("perspShape.nearClipPlane")
    farClipPlane = cmds.getAttr("perspShape.farClipPlane")
    cmds.setAttr("perspShape.nearClipPlane", 0.1)
    cmds.setAttr("perspShape.farClipPlane", 100000)
    
    cmds.select(clear=True)
    cmds.modelEditor(currentPanel, edit=True, displayAppearance="smoothShaded", displayTextures=True, displayLights="default")
    
    cmds.playblast(
        frame=1, format="image", completeFilename=smallImagesPath, clearCache=True, viewer=False, 
        showOrnaments=False, compression="jpg", quality=40, percent=100, widthHeight=[144,144]
        )
    
    cmds.playblast(
        frame=1, format="image", completeFilename=imagePath, clearCache=True, viewer=False, 
        showOrnaments=False, compression="jpg", quality=40, percent=100, widthHeight=[1024,768]
        )
    
    cmds.isolateSelect(currentPanel, state=0)
    cmds.setAttr("perspShape.preScale", 1.0)
    cmds.setAttr("perspShape.nearClipPlane", nearClipPlane)
    cmds.setAttr("perspShape.farClipPlane", farClipPlane)
    
    sys.stdout.write("Screen grab saved to: %s\n" % imagePath)
    
# end (doScreenGrab)


def do(nodes=None, currentAssetCategory="environments"):
    '''Saves out an image of the asset.
    '''
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to create screen grab of referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            continue
        
        doScreenGrab(node, currentAssetCategory=currentAssetCategory)
        
# end (do)
