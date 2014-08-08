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
# 

'''
NAME
    ddCheckNames.py

DESC
    Checks names.
    
USAGE
    ddCheckNames.do()
    
FUNCTIONS
    checkGrpName()
    checkGeoName()
    checkCharName()
    do()
    
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys
import os

# VAD
import ddConstants; reload(ddConstants)


def checkGrpName(node=None, currentAssetCategory="environments"):
    '''Checks name tokens.
    '''
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[currentAssetCategory]
    if not node:
        selection = cmds.ls(selection=True, long=True)
        if selection:
            node = selection[0]
        else:
            return False
    
    tokens = node.rpartition("|")[2].split("_")
    nodeType = "GRP"
    path = tokens[0]
    endOfPath = False
    descriptorChecked = False
    correctNodeType = False
    correctAssetLetter = False
    correctVersionLetter = False
    correctAssetVariant = False
    correctVersionNumber = False
    correctInstance = False
    instanceNumber = ""
    validName = True
    
    currentDirectory = currentAssetLibrary
    currentDirectoryListing = os.listdir(currentDirectory)
    if path in currentDirectoryListing:     # char, env, old, prop, tex
        for i in range(len(tokens)):
            currentToken = tokens[i]
            if currentToken in currentDirectoryListing and not endOfPath:   # env
                # Checking the path tokens at beginning of name.
                currentDirectory = os.path.join(currentDirectory, tokens[i])
                currentDirectoryListing = os.listdir(currentDirectory)
                if currentDirectoryListing:
                    for dirname in currentDirectoryListing:
                        if os.path.isdir(os.path.join(currentDirectory, dirname)):
                            if ord(dirname[-1]) in range(65, 91):
                                # If directory name ends with a capital letter, then directory is an asset.
                                endOfPath = True
                                currentDirectoryListing = []
                                break
                else:
                    endOfPath = True
                    
            elif i == len(tokens)-1 and currentToken.isdigit():
                # Last token is instance number
                correctInstance = True
                instanceNumber = currentToken
            elif not descriptorChecked and not correctNodeType and not correctVersionNumber and not correctInstance:
                # Checking for the "AvA" part of "palmAvA"
                versionLetters = currentToken[-3:]
                letter, v, variant = versionLetters.partition("v")
                if len(letter) == 1 and len(v) == 1 and len(variant) ==1:
                    if ord(letter) in range(65,91):
                        correctAssetLetter = True
                    if v == "v":
                        correctVersionLetter = True
                    if ord(variant) in range(65,91):
                        correctAssetVariant = True
                descriptorChecked = True
            elif currentToken == nodeType and descriptorChecked and not correctVersionNumber and not correctInstance:
                correctNodeType = True
            elif descriptorChecked and nodeType == "GRP" and not correctInstance:
                # Version number, eg v001
                if len(currentToken) == 4 and currentToken.startswith("v"):
                    if currentToken[1].isdigit() and currentToken[2].isdigit() and currentToken[3].isdigit():
                        correctVersionNumber = True                 
        
        if not endOfPath or not correctNodeType or not correctAssetLetter or not correctVersionLetter or not correctAssetVariant or not correctVersionNumber or not correctInstance:
            validName = False
        else:
            validName = checkGeoName(node)
    else:
        validName = False
    
    return validName
    
# end (checkGrpName)


def checkGeoName(node):
    '''Checks if children of node (GEO nodes) are named correctly.
    '''
    divider = "_GRP_"
    chesspieceTypes = ["CPF", "CPO", "CPD", "CPS"]
    
    nodeSplits = node.rpartition("|")[2].split("_")
    for nodeSplit in nodeSplits:
        if nodeSplit in chesspieceTypes:
            divider = "_%s_GRP_" % nodeSplit

    assetName, grp, versionAndNumber = node.rpartition("|")[2].partition(divider)
    version, underscore, number = versionAndNumber.partition("_")
    divider = divider.replace("GRP", "GEO")
            
    # Check the child GEO nodes
    children = cmds.listRelatives(node, path=True, allDescendents=True) or []
    nodeList = [x for x in children if cmds.nodeType(x) == "transform"] or []
    for nodeName in nodeList:
        if "GRP" in nodeName:
            return False
            
        # Check the child GEO name: beginning of GEO name must match beginning of GRP name
        if not nodeName.rpartition("|")[2].startswith(assetName) or not divider in nodeName:
            return False
            
        mesh, suffix = nodeName.rpartition("|")[2].split(divider)
        # Check the child GEO name: must not contain version number. Option to rename.
        if suffix.startswith("v") or not suffix == number:
            return False
            
    return True

# end (checkGeoName)


def checkCharName(node, currentAssetCategory="characters"):
    '''Checks character name tokens.
    '''
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[currentAssetCategory]
    if not node:
        selection = cmds.ls(selection=True, long=True)
        if selection:
            node = selection[0]
        else:
            return False
            
    tokens = node.rpartition("|")[2].split("_")
    if (len(tokens) < 6):
        return False
    
    validName = True
    path = tokens[0]
    endOfPath = False
    chessPiece = False
    nodeType = "GRP"
    correctVersionNumber = False
    correctNodeType = False
    correctInstance = False
    instanceNumber = ""
    charType = { "hero": "hero", "bg": "background", "sec": "secondary" }
    chesspieceTypes = ["CPF", "CPD", "CPO", "CPS"]
    
    currentDirectory = currentAssetLibrary
    
    if path == "char":
        divider = ""
        for token in tokens:
            if token in chesspieceTypes:
                divider = token
                
        for i in range(1, len(tokens)):
            currentToken = tokens[i]
            if i == 1 and tokens[1] in charType.keys():
                # char_hero, char_bg, char_sec
                currentDirectory = os.path.join(currentDirectory, charType[tokens[1]])
                currentDirectoryListing = os.listdir(currentDirectory) or []
                if '%s_%s' % (tokens[2], tokens[3]) in currentDirectoryListing:
                    if os.path.isdir(os.path.join(currentDirectory,
                                            '%s_%s' % (tokens[2], tokens[3]))):
                        endOfPath = True
            elif currentToken in chesspieceTypes:
                chessPiece = True
            elif currentToken == nodeType:
                correctNodeType = True
            elif i == len(tokens)-1 and currentToken.isdigit():
                # Last token is instance number
                correctInstance = True
                instanceNumber = currentToken
            elif len(currentToken) == 4 and currentToken.startswith("v"):
                if currentToken[1].isdigit() and currentToken[2].isdigit() and currentToken[3].isdigit():
                    correctVersionNumber = True
        
        if not endOfPath or not correctVersionNumber or not correctNodeType or not correctInstance or not chessPiece:
            validName = False
        else:
            validName = checkGeoName(node)
    else:
        validName = False

    return validName

# end (checkCharName)


def do(nodes=None, currentAssetCategory="environments"):
    '''Checks name tokens.
    '''
    invalidNodeList = list()
    if not nodes:
        nodes = cmds.ls(selection=True, long=True)
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            sys.stdout.write("--> Unable to check names of referenced node %s. Skipping... \n" % node.rpartition("|")[2])
            invalidNodeList.append(node)
        else:
            validName = None
            if currentAssetCategory == "characters":
                validName = checkCharName(node, currentAssetCategory)
            else:
                validName = checkGrpName(node, currentAssetCategory)
                
            if not validName:
                invalidNodeList.append(node)
            
    return invalidNodeList 
    
# end (do)
