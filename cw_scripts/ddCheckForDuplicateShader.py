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
    ddCheckForDuplicateShader.py

DESC
    Checks if shader is identical to an already published shader.

USAGE
    ddCheckForDuplicateShader.do()
    
FUNCTIONS
    compareTifFiles()
    getAssetCategory()
    getAssetLibrary()
    getAssetShaderLibrary()
    getCategoryFolder()
    do()
    
'''

# MAYA
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

# PYTHON
import os
import sys

# VAD
import ddConstants; reload(ddConstants)


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


def getCategoryFolder(arg=None):
    '''Get selected category.
    '''
    category = cmds.textScrollList("shaderCategoriesSL", query=True, selectItem=True)
    directory = getAssetShaderLibrary()
    if category:
        category = category[0]
        if not (category == "-- UNFILED --"):
            directory = os.path.join(getAssetShaderLibrary(), category)
            
    return directory


def compareTifFiles(currentPath, publishedPath):
    tolerance = 0.0001
    
    # Load the paths.
    currentImage = om.MImage()
    try:
        currentImage.readFromFile(currentPath)
    except:
        sys.stdout.write('--> Unable to analyze data in %s. Verify that TIF file does NOT use ZIP compression.\n' % currentPath)
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='Unable to analyze data in %s. \n\nVerify that TIF file does NOT use ZIP compression.\n' % currentPath, 
                button=["Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
        return "Fail"
        
    publishedImage = om.MImage()
    try:
        publishedImage.readFromFile(publishedPath)
    except:
        sys.stdout.write('--> Unable to analyze data in %s. Verify that ".tif" file does NOT use "zip" compression.\n' % publishedPath)
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='Unable to analyze data in %s. \n\nVerify that ".tif" file does NOT use "zip" compression.\n' % currentPath, 
                button=["Cancel"], 
                defaultButton="Cancel", cancelButton="Cancel", dismissString="Cancel"
                )
        return "Fail"
        
    # Get the dimensions.
    utilWidth = om.MScriptUtil()
    utilWidth.createFromInt(0)
    ptrWidth = utilWidth.asUintPtr()
    
    utilHeight = om.MScriptUtil()
    utilHeight.createFromInt(0)
    ptrHeight = utilHeight.asUintPtr()
    
    currentImage.getSize(ptrWidth, ptrHeight)
    currentWidth = om.MScriptUtil.getUint(ptrWidth)
    currentHeight = om.MScriptUtil.getUint(ptrHeight)
    
    publishedImage.getSize(ptrWidth, ptrHeight)
    publishedWidth = om.MScriptUtil.getUint(ptrWidth)
    publishedHeight = om.MScriptUtil.getUint(ptrHeight)
    
    # Compare dimensions.
    if (abs(currentWidth - publishedWidth) > tolerance) or (abs(currentHeight - publishedHeight) > tolerance):
        # Dimensions are different.
        currentImage.release()
        publishedImage.release()
        return False
        
    # Compare the pixels.
    maxNumber = currentWidth * currentHeight * 4
    currentPixels = currentImage.pixels()
    publishedPixels = publishedImage.pixels()
    
    # Checking every 3rd pixel from center of image out with jumps.
    skip = 32
    #order = [0, 16, 8, 24, 4, 20, 12, 28, 6, 14, 22, 2, 26, 10, 18, 30, 5, 7, 1, 3, 13, 15, 9, 11, 21, 23, 17, 19, 29, 31, 25, 27]
    order = [0, 24, 12, 14, 2, 26, 1, 3, 13, 15, 25, 27]
    
    all = list()
    for j in order:
        for i in range(maxNumber/2 + j, maxNumber, skip):
            currentValue = om.MScriptUtil.getUcharArrayItem(currentPixels, i)
            publishedValue = om.MScriptUtil.getUcharArrayItem(publishedPixels, i)
            if abs(currentValue - publishedValue) > tolerance:
                # Pixels values are different.
                currentImage.release()
                publishedImage.release()
                return False
            
        for i in range(j, maxNumber/2, skip):
            currentValue = om.MScriptUtil.getUcharArrayItem(currentPixels, i)
            publishedValue = om.MScriptUtil.getUcharArrayItem(publishedPixels, i)
            if abs(currentValue - publishedValue) > tolerance:
                # Pixels values are different.
                currentImage.release()
                publishedImage.release()
                return False
            
    currentImage.release()
    publishedImage.release()
    return True
    
# end (compareTifFiles)


def do(currentFileNodes):
    sys.stdout.write("Checking if a similar shader has already been published. This might take a minute...\n")
    cmds.refresh()
    
    textureLabels = ["DIFF", "SPEC", "NRML"]
    currentAssetDirectory = getAssetLibrary()
    
    # Get selected category folder.
    directory = getCategoryFolder()
    # Get the list of files on disk.
    mayaShaderFiles = [x for x in os.listdir(directory) if x.endswith(".ma")]
    
    currentFiles = dict()
    for fileNode in currentFileNodes:
        found = False
        fileTextureName = cmds.getAttr("%s.fileTextureName" % fileNode)
        for label in textureLabels:
            if label in fileTextureName:
                currentFiles[label] = fileTextureName
                found = True
                
        if not found:
            cnxList = cmds.listConnections(fileNode, source=False, destination=True, plugs=True) or []
            for cnx in cnxList:
                attr = cnx.partition(".")[2]
                if attr in ddConstants.textureTypes.keys():        
                    currentFiles[ddConstants.textureTypes[attr]] = fileTextureName
    
    for mayaShaderFile in mayaShaderFiles:
        # Find the files attached to file nodes.
        publishedFiles = dict()
        f = open(os.path.join(directory, mayaShaderFile), "r")
        for line in f:
            if not ((currentAssetDirectory in line) or (currentAssetDirectory.replace(os.sep, "/") in line)):
                continue
            filename = os.path.join(currentAssetDirectory, "%s" % line.replace("/", os.sep).rpartition("%s\\" % currentAssetDirectory)[2].rpartition('"')[0])
            for label in textureLabels:
                if label in filename:
                    publishedFiles[label] = filename
        f.close()
        
        if not len(currentFiles) == len(publishedFiles):
            # MayaShaderFile does not contain the same number of file nodes.
            continue
        
        allSameFiles = True
        for label in textureLabels:
            if (label in currentFiles.keys()) and (label in publishedFiles.keys()):
                sameFile = compareTifFiles(currentPath=currentFiles[label], publishedPath=publishedFiles[label])
                if sameFile == "Fail":
                    return "Fail"
                if not sameFile:
                    allSameFiles = False
                    break
                    
        if allSameFiles:
            return mayaShaderFile.rpartition(os.sep)[2].replace(".ma", "")
    
    return None
    
# end (do)
