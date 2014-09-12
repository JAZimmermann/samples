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
    ddExportAssets.py

DESC
    Exports assets from scene file. 
    - Provides some node name checking.
    - Freezes transforms and removes pivot offsets. 
    - Checks if textures files are saved in assetLibrary and file format extension is ".tif".
    - Exports DIFF, SPEC, NRML map files per GEO, if exist
    - Exports ".ma" and ".fbx" files with the option of changing asset letter, 
      changing variant or versioning up if files already exist.
    - Replaces asset group with reference.
    - Moves referenced asset group back to its original position.
    
USAGE
    ddExportAssets.do()
    
FUNCTIONS
    exportAsset()
    exportCharacterAsset()
    exportMayaFiles()
    renameAssetNodes()
    do()
    
'''


# MAYA
import maya.cmds as cmds
import maya.mel as mel

# PYTHON
import os
import re
import sys
import shutil

# VAD
import ddConstants; reload(ddConstants)
import ddAddGeoMetadata; reload(ddAddGeoMetadata)
import ddCheckNames; reload(ddCheckNames)
import ddCheckTexturePublished; reload(ddCheckTexturePublished)
import ddCheckTextures; reload(ddCheckTextures)
import ddImportFromReference; reload(ddImportFromReference)
import ddLockGeoTransforms; reload(ddLockGeoTransforms)
import ddRemoveFromLayers; reload(ddRemoveFromLayers)
import ddRemoveNamespaces; reload(ddRemoveNamespaces)
import ddRemovePivotOffsets; reload(ddRemovePivotOffsets)
import ddRemoveRequires; reload(ddRemoveRequires)
import ddScreenGrab; reload(ddScreenGrab)
import ddUnlockGeoTransforms; reload(ddUnlockGeoTransforms)

# apath = "B:/home/johnz/scripts/jbtools"
# if apath not in sys.path:
#     sys.path.insert(2, apath)
#
# from common.vp_mail import publish_email as pub_mail
# from common.vp_mail import publish_notes
# from vp_environ import vp_environment as vpe

apath = os.getenv("PYTHONPATH")
if apath not in sys.path:
    sys.path.insert(2, apath)

from vir_prod.vp_mail import publish_email as pub_mail
from vir_prod.vp_mail import publish_notes
from vir_prod.vp_environ import vp_environment as vpe


# PLUGINS
if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
    cmds.loadPlugin("fbxmaya")


def exportAsset(node, override=False, currentAssetCategory="environments"):
    '''Exports ".ma" and ".fbx" files with the option of versioning up if files already exist.
       Validates textures after renaming nodes and prior to exporting. Updates file node path.
    '''
    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[currentAssetCategory]
    # Create asset path
    dirs = node.rpartition("|")[2].split("_GRP")[0].split("_")
    version = node.rpartition("|")[2].split("_GRP_")[1].split("_")[0]
    fileName = dirs[-1]
    fileVersionName = "%s_%s" % (fileName, version)
    
    assetPath = currentAssetLibrary
    for d in dirs:
        assetPath = os.path.join(assetPath, d)
        if not os.path.isdir(assetPath):
            os.mkdir(assetPath)
        
    # Export assets
    confirmSave = "Replace"
    assetFilePath = os.path.join(assetPath, "%s.ma" % fileVersionName)
    if os.path.isfile(assetFilePath):
        confirmSave = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='File "%s" already exists.' % fileVersionName, 
                button=["Change asset letter", "Change variant", "Version Up", "Replace", "Cancel"], 
                defaultButton="Change asset letter", cancelButton="Cancel", dismissString="Cancel"
                )
                
        if confirmSave == "Version Up":
            # Find next version number
            found = False
            number = int(version.replace("v", ""))
            assetPath = os.path.join(assetPath, fileName)
            while not found:
                number += 1
                newFileName = "%s_v%03d" % (fileName, number)
                assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newFileName)
                if not os.path.isfile("%s.ma" % assetPath):
                    found = True
                    break
            
            # Rename top GRP node
            renamedNode = "%s_GRP_v%03d_1" % (node.rpartition("|")[2].split("_GRP")[0], number)
            node = cmds.rename(node, renamedNode)
            
            # # Export textures
            # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
            #
            # if validTextures:
            #     # Export files
            #     cmds.select(node, r=1)
            #     validExport = exportMayaFiles(assetPath=assetPath, force=False)
            #     if not validExport:
            #         assetPath = None
            # else:
            #     assetPath = None
            # Export files
            cmds.select(node, r=1)
            validExport = exportMayaFiles(assetPath=assetPath, force=False)
            if not validExport:
                assetPath = None
            
        elif confirmSave == "Change asset letter":
            # Find next asset letter
            asset, grp, version = node.rpartition("|")[2].partition("_GRP")
            asset = asset.rpartition("|")[2]
            assetOnly = asset.rpartition("_")[2][:-3]
            assetVariant = asset.rpartition("_")[2][-3:].partition("v")
            
            newAssetIndex = ord(assetVariant[0]) + 1
            found = False
            
            for i in range(newAssetIndex, 91):
                newAssetLetter = chr(i)
                newAsset = "%s%sv%s" % (asset[:-3], newAssetLetter, assetVariant[2])
                newAssetVariant = newAsset.rpartition("_")[2]
                assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newAssetVariant)
                if not os.path.isdir(assetPath):
                    found = True
                    break
                    
            if not found:
                for i in range(65, newAssetIndex-1):
                    newAssetLetter = chr(i)
                    newAsset = "%s%sv%s" % (asset[:-3], newAssetLetter, assetVariant[2])
                    newAssetVariant = newAsset.rpartition("_")[2]
                    assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newAssetVariant)
                    if not os.path.isdir(assetPath):
                        found = True
                        break
                      
            if not found:
                confirmChange = cmds.confirmDialog(
                        title="Warning", messageAlign="center", 
                        message='All asset letters have been used. Cancelling...', 
                        button=["Ok"], defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                        )
                if confirmChange == "Ok":
                    sys.stdout.write("Export cancelled.\n")
                    return node, None, override
            
            # Create new asset name and directory
            if not os.path.isdir(assetPath):
                os.mkdir(assetPath)
            assetPath = os.path.join(assetPath, "%s_v001" % newAssetVariant)
            
            # Rename top GRP node and child GEO nodes
            node = renameAssetNodes(node=node, oldName=asset, newName=newAsset, versionStr="v001")
            
            # Export textures
            # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
            #
            # if validTextures:
            #     # Export files
            #     cmds.select(node, r=1)
            #     validExport = exportMayaFiles(assetPath=assetPath, force=False)
            #     if not validExport:
            #         assetPath = None
            # else:
            #     assetPath = None
            # Export files
            cmds.select(node, r=1)
            validExport = exportMayaFiles(assetPath=assetPath, force=False)
            if not validExport:
                assetPath = None
                
        elif confirmSave == "Change variant":
            # Find next variant letter
            asset, grp, version = node.rpartition("|")[2].partition("_GRP")
            asset = asset.rpartition("|")[2]
            assetOnly = asset.rpartition("_")[2][:-3]
            assetVariant = asset.rpartition("_")[2][-3:].partition("v")
            
            newVariantIndex = ord(assetVariant[2]) + 1
            found = False
            
            for i in range(newVariantIndex, 91):
                newVariantLetter = chr(i)
                newAsset = "%s%sv%s" % (asset[:-3], assetVariant[0], newVariantLetter)
                newAssetVariant = newAsset.rpartition("_")[2]
                assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newAssetVariant)
                if not os.path.isdir(assetPath):
                    found = True
                    break
                    
            if not found:
                for i in range(65, newVariantIndex-1):
                    newVariantLetter = chr(i)
                    newAsset = "%s%sv%s" % (asset[:-3], assetVariant[0], newVariantLetter)
                    newAssetVariant = newAsset.rpartition("_")[2]
                    assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newAssetVariant)
                    if not os.path.isdir(assetPath):
                        found = True
                        break
                        
            if not found:
                confirmChange = cmds.confirmDialog(
                        title="Warning", messageAlign="center", 
                        message='All asset letters have been used. Cancelling...', 
                        button=["Ok"], 
                        defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                        )
                if confirmChange == "Ok":
                    sys.stdout.write("Export cancelled.\n")
                    return node, None, override
            
            # Create new asset name and directory
            if not os.path.isdir(assetPath):
                os.mkdir(assetPath)
            assetPath = os.path.join(assetPath, "%s_v001" % newAssetVariant)
            
            # Rename top GRP node and child GEO nodes
            node = renameAssetNodes(node=node, oldName=asset, newName=newAsset, versionStr="v001")
            
            # # Export textures
            # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
            #
            # if validTextures:
            #     # Export files
            #     cmds.select(node, r=1)
            #     validExport = exportMayaFiles(assetPath=assetPath, force=False)
            #     if not validExport:
            #         assetPath = None
            # else:
            #     assetPath = None
            # Export files
            cmds.select(node, r=1)
            validExport = exportMayaFiles(assetPath=assetPath, force=False)
            if not validExport:
                assetPath = None
                
        elif confirmSave == "Cancel":
            assetPath = None
            
    if confirmSave == "Replace":
        assetPath = os.path.join(assetPath, fileVersionName)
        # # Export textures
        # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
        # if validTextures:
        #     cmds.select(node, r=1)
        #     validExport = exportMayaFiles(assetPath=assetPath, force=True)
        #     if not validExport:
        #         assetPath = None
        # else:
        #     assetPath = None
        cmds.select(node, r=1)
        validExport = exportMayaFiles(assetPath=assetPath, force=True)
        if not validExport:
            assetPath = None
            
    return node, assetPath, override
    
# end (exportAsset)


def exportCharacterAsset(node):
    '''Exports ".ma" and ".fbx" files with the option of versioning up if files already exist.
       Validates textures after renaming nodes and prior to exporting. Updates file node path.
    '''
    currentAssetCategory = "characters"
    currentAssetLibrary=ddConstants.ASSET_DIRECTORIES[currentAssetCategory]
    charType = { "hero": "hero", "bg": "background", "sec": "secondary" }
    chesspieceTypes = ["CPF", "CPO", "CPD", "CPS"]
    
    # Create asset path
    divider = ""
    dividerGRP = ""
    version = ""
    
    nodeSplits = node.split("_")
    for nodeSplit in nodeSplits:
        if nodeSplit in chesspieceTypes:
            divider = nodeSplit
            
    dividerGRP = "%s_GRP" % divider
    
    dirs = node.rpartition("|")[2].split("_%s" % dividerGRP)[0].split("_")
    fileVersionName = ""
    dirList = list()
    version = node.rpartition("|")[2].split("_%s_" % dividerGRP)[1].split("_")[0]
    fileName = dirs[-1]
    if len(dirs) == 4:
        fileName = "%s_%s" % (dirs[-2], dirs[-1])
    fileVersionName = "%s_%s_%s" % (fileName, divider, version)
    dirList = [charType[dirs[1]], "%s_%s" % (dirs[2], dirs[3]),
                                                    "chesspiece", "published"]
        
    assetPath = currentAssetLibrary
    for dirName in dirList:
        assetPath = os.path.join(assetPath, dirName)
        if not os.path.isdir(assetPath):
            os.mkdir(assetPath)
    
    # Export assets
    confirmSave = "Replace"
    assetFilePath = os.path.join(assetPath, "%s.ma" % fileVersionName)
    if os.path.isfile(assetFilePath):
        confirmSave = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='File "%s" already exists.' % fileVersionName, 
                button=["Version Up", "Replace", "Cancel"], 
                defaultButton="Version Up", cancelButton="Cancel", dismissString="Cancel"
                )
        
        if confirmSave == "Version Up":
            # Find next version number
            found = False
            number = int(version.replace("v", ""))
            assetPath = os.path.join(assetPath, fileName)
            while not found:
                number += 1
                newFileName = "%s_%s_v%03d" % (fileName, divider, number)
                assetPath = os.path.join(assetPath.rpartition(os.sep)[0], newFileName)
                if not os.path.isfile("%s.ma" % assetPath):
                    found = True
                    break
            
            # Rename node
            renamedNode = "%s_%s_v%03d_1" % (node.rpartition("|")[2].split("_%s" % dividerGRP)[0], dividerGRP, number)
            node = cmds.rename(node, renamedNode)
            
            # # Export textures
            # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
            #
            # if validTextures:
            #     # Export files
            #     cmds.select(node, r=1)
            #     validExport = exportMayaFiles(assetPath=assetPath, force=False)
            #     if not validExport:
            #         assetPath = None
            # else:
            #     assetPath = None
            # Export files
            cmds.select(node, r=1)
            validExport = exportMayaFiles(assetPath=assetPath, force=False)
            if not validExport:
                assetPath = None
                
        elif confirmSave == "Cancel":
            assetPath = None

    if confirmSave == "Replace":
        assetPath = os.path.join(assetPath, fileVersionName)
        # # Export textures
        # validTextures = ddCheckTexturePublished.do(nodes=node, assetCategory=currentAssetCategory)
        # if validTextures:
        #     cmds.select(node, r=1)
        #     validExport = exportMayaFiles(assetPath=assetPath, force=True)
        #     if not validExport:
        #         assetPath = None
        # else:
        #     assetPath = None
        cmds.select(node, r=1)
        validExport = exportMayaFiles(assetPath=assetPath, force=True)
        if not validExport:
            assetPath = None

    return node, assetPath


def exportMayaFiles(assetPath, force=False):
    '''Exports selection to the ".ma" and ".fbx" files
    '''
    asciiPath = "%s.ma" % assetPath
    sys.stdout.write('Exporting "%s"...\n' % asciiPath)
    try:
        exportedFile = cmds.file(asciiPath, type="mayaAscii", exportSelected=True, force=force)
    except:
        sys.stdout.write('Export cancelled.\n')
        return False
        
    # Remove unused requires from ".ma" file
    ddRemoveRequires.do(path=asciiPath)
    
    # Export fbx
    sys.stdout.write('Exporting "%s.fbx"...\n' % assetPath)
    exported = False
    
    try:
        sys.stdout.write("Exporting fbx file (1-FBXExport).\n")
        mel.eval('FBXExport -f "%s.fbx" -s' % assetPath.replace(os.sep, "/"))
        exported = True
    except:
        pass
    
    if not exported:
        try:
            sys.stdout.write("Exporting fbx file (2-FBX export).\n")
            cmds.file("%s.fbx" % assetPath, type="FBX export", exportSelected=True, force=force)
            exported = True
        except:
            pass
    
    if not exported:
        try:
            sys.stdout.write("Exporting fbx file (3-Fbx).\n")
            cmds.file("%s.fbx" % assetPath, type="Fbx", exportSelected=True, force=force)
            exported = True
        except:
            pass
    
    if not exported:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message='Fbx "%s" was not exported.' % assetPath, 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
    
    # Remove stray ".mayaSwatches" and "Keyboard" directories
    dirPath = asciiPath.rpartition(os.sep)[0]
    swatchPath = os.path.join(dirPath, ".mayaSwatches")
    keyboardPath = os.path.join(dirPath, "Keyboard")
    
    if os.path.isdir(swatchPath):
        try:
            swatchList = os.listdir(swatchPath)
            for swatch in swatchList:
                os.remove(os.path.join(swatchPath, swatch))
            os.rmdir(swatchPath)
            os.rmdir(keyboardPath)
        except: pass
        
    return True
    
# end (exportMayaFiles)


def renameAssetNodes(node, oldName, newName, versionStr):
    '''Renames asset top node and children by replacing oldName with newName.
    '''
    children = cmds.listRelatives(node, path=True, allDescendents=True) or []
    nodeList = [x for x in children if cmds.nodeType(x) == "transform"] or []
    for nodeName in nodeList:
        newNodeName = "%s_1" % nodeName.rpartition("|")[2].replace(oldName, newName).rpartition("_")[0]
        cmds.rename(nodeName, newNodeName)
        
    currentVersion = node.split("_GRP_")[1]
    nodeName = cmds.rename(node, node.rpartition("|")[2].replace(oldName, newName).replace(currentVersion, "%s_1" % versionStr))
    
    return nodeName
    
# end (renameAssetNodes)


def do(nodes=None, replaceWithReference=True, export=True, currentAssetCategory="environments", notify=True):
    # double check if necessary environment variables exist before continuing
    print "should we notify? %s" % str(notify)
    vpe.VP_Environment().test()

    currentAssetLibrary = ddConstants.ASSET_DIRECTORIES[currentAssetCategory]

    # Check if assetLibrary folder exists
    if not os.path.isdir(currentAssetLibrary):
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="AssetLibrary path does not exist: %s" % currentAssetLibrary, 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    # Get selection
    if not nodes:
        nodes = cmds.ls(selection=True, objectsOnly=True, long=True)
        if len(nodes ) == 0:
            confirm = cmds.confirmDialog(
                    title="Warning", messageAlign="center", 
                    message="Select at least one group object.", 
                    button=["Ok"], 
                    defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                    )
            return

    if not isinstance(nodes, list):
        nodes = [nodes]
    
    invalidNodes = list()
    invalid_textured_nodes = list()
    override = False
    resultTopNodes = list()
    
    # Clean and export
    for sel in nodes:
        sys.stdout.write("\n--> %s\n" % sel.rpartition("|")[2])
        
        currentNode = sel
        nodeParent = cmds.listRelatives(sel, parent=True, path=True)
        if cmds.referenceQuery(currentNode, isNodeReferenced=True):
            currentNode = ddImportFromReference.do(currentNode)[0]
        
        invalidNode = ddCheckNames.do(nodes=currentNode, currentAssetCategory=currentAssetCategory)
        valid_textures = ddCheckTextures.do(node=currentNode)[0]
        if not invalidNode and valid_textures:
            publish_details = {}
            # no need to grab notes from user if not sending email
            if notify:
                publish_details["Notes"] = publish_notes.PublishNotes().notes

            validNode = ddRemoveNamespaces.doRemoveNamespaces(node=currentNode)
            topGrpLayer = ddRemoveFromLayers.do(nodes=validNode)[0]
            
            pos = cmds.xform(validNode, query=True, worldSpace=True, absolute=True, rotatePivot=True)
            rot = cmds.getAttr("%s.r" % validNode)[0]
            scl = cmds.getAttr("%s.s" % validNode)[0]
            
            ddUnlockGeoTransforms.do(nodes=validNode)
            returnedNodes = ddRemovePivotOffsets.do(nodes=validNode, returnToPos=False, currentAssetCategory=currentAssetCategory)
            if returnedNodes:
                validNode = returnedNodes[0]
            
            ddAddGeoMetadata.do(nodes=validNode)
            ddLockGeoTransforms.do(nodes=validNode)
            advancedAssets = cmds.ls(type="container", long=True)
            if advancedAssets:
                sys.stdout.write("Deleting advanced assets...\n")
                cmds.delete(advancedAssets)
            
            unknownNodes = cmds.ls(type="unknown", long=True)
            if unknownNodes:
                try:
                    sys.stdout.write("Deleting unknown nodes...\n")
                    cmds.delete(unknownNodes)
                except:
                    cmds.warning("Unable to delete unknown nodes.")
                    
            if not export:
                continue
            
            if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
                exportedNode, exportedPath = exportCharacterAsset(sel)
                # attempt to collect publish details for character piece
                charType = {"hero": "hero",
                            "bg": "background",
                            "sec": "secondary"}
                scene_patt = re.compile("char_(%s)_[A-Z]{3}_[a-z]+"
                                                % "|".join(charType.values()))
                char_patt = re.compile("[A-Z]{3}_[a-zA-Z]+")

                if scene_patt.search(exportedNode):
                    publish_details["Character"] = \
                                        char_patt.search(exportedNode).group()
                publish_details["Template_Category"] = "vad_chesspiece"
            else:
                exportedNode, exportedPath, override = exportAsset(node=validNode, override=False, currentAssetCategory=currentAssetCategory)
                env_patt = re.compile(
                        "[a-z]{3}_[a-z]{3}(_[a-z]+)*_([a-zA-Z]+[A-Z]v[A-Z])_*")
                if env_patt.search(exportedNode):
                    publish_details["Enviro_Asset"] = \
                                    env_patt.search(exportedNode).groups()[-1]
                publish_details["Template_Category"] = "vad_enviro_asset"

            if exportedPath:
                ddScreenGrab.do(nodes=exportedNode.rpartition("|")[2], currentAssetCategory=currentAssetCategory)
            else:
                if currentNode != sel:
                    cmds.delete(currentNode)
                sys.stdout.write("Export of %s was Canceled..." % exportedNode)
                return

            # update publish details with version, file
            #   and file path information
            version_patt = re.compile("_v([0-9]{2,4})_*")
            if version_patt.search(exportedNode):
                publish_details["Version"] =\
                            version_patt.search(exportedNode).groups()[0]
            publish_details["FILEPATH"] = "%s.ma" % exportedPath
            publish_details["FILE"] = os.path.basename(
                                                    publish_details["FILEPATH"])

            if replaceWithReference and exportedPath:
                currentSceneFile = cmds.file(query=True, sceneName=True).replace("/", os.sep)
                exportedFile = "%s.ma" % exportedPath
                if currentSceneFile == exportedFile:
                    confirm = cmds.confirmDialog(
                            title="Warning", messageAlign="center", 
                            message="Scene file is already open. Cannot reference a file into itself.", 
                            button=["Ok"], 
                            defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                            )
                    if confirm == "Ok":
                        continue
                
                # Delete original GRP
                confirm = cmds.confirmDialog(
                        title="Warning", messageAlign="center", 
                        message="Delete original GRP?", 
                        button=["Ok", "Cancel"], 
                        defaultButton="Ok", cancelButton="Cancel", dismissString="Cancel"
                        )
                if confirm == "Ok":
                    cmds.delete(exportedNode)
                else:
                    # Move group back.
                    cmds.xform(exportedNode, worldSpace=True, absolute=True, translation=pos)
                    cmds.setAttr("%s.r" % exportedNode, rot[0], rot[1], rot[2])
                    cmds.setAttr("%s.s" % exportedNode, scl[0], scl[1], scl[2])                
                    
                # Reference a copy of the exported file
                namespace = os.path.split(exportedPath)[1].partition(".")[0]
                
                newReferencedNodes = cmds.file("%s.ma" % exportedPath, reference=True, namespace=namespace, returnNewNodes=True)
                referencedTopGrp = ""
                refTransforms = [x for x in newReferencedNodes if cmds.nodeType(x) == "transform"]
                for refTransform in refTransforms:
                    refParent = cmds.listRelatives(refTransform, parent=True, fullPath=True)
                    if not refParent or not refParent[0] in refTransforms:
                        referencedTopGrp = refTransform
                cmds.xform(referencedTopGrp, worldSpace=True, absolute=True, translation=pos)
                cmds.setAttr("%s.r" % referencedTopGrp, rot[0], rot[1], rot[2])
                cmds.setAttr("%s.s" % referencedTopGrp, scl[0], scl[1], scl[2])
                
                if topGrpLayer:
                    cmds.editDisplayLayerMembers(topGrpLayer, referencedTopGrp, noRecurse=True)
                if nodeParent:
                    referencedTopGrp = cmds.parent(referencedTopGrp, nodeParent[0])[0]
                
                resultTopNodes.append(referencedTopGrp.rpartition("|")[2])
            else:
                # Move group back.
                cmds.xform(exportedNode, worldSpace=True, absolute=True, translation=pos)
                cmds.setAttr("%s.r" % exportedNode, rot[0], rot[1], rot[2])
                cmds.setAttr("%s.s" % exportedNode, scl[0], scl[1], scl[2])                
                resultTopNodes.append(exportedNode.rpartition("|")[2])
                if topGrpLayer:
                    cmds.editDisplayLayerMembers(topGrpLayer, exportedNode, noRecurse=True)
                if nodeParent:
                    exportedNode = cmds.parent(exportedNode, nodeParent[0])[0]

            # prep and send publish email
            publish_details["SHOW"] = os.getenv("SHOW")
            publish_details["ARTIST"] = os.getenv("ARTIST") \
                                    if os.getenv("ARTIST") else "Some Artist"

            # send publish email if user specified notification
            if notify:
                sys.stdout.write("Sending email. \n")
                set_email = pub_mail.PublishEmail(
                                        publish_details["Template_Category"])
                set_email.publish_details = publish_details
                set_email.build_email()
                set_email.send_mail()
            else:
                sys.stdout.write(
                        "Holding off on sending publish email by request. \n")

        else:
            if invalidNode:
                sys.stdout.write("Invalid name %s. Skipping...\n" % invalidNode[0].rpartition("|")[2])
                invalidNodes.append(sel)
            elif not valid_textures:
                sys.stdout.write("Invalid texture found on node %s. Skipping...\n" % sel.rpartition("|")[2])
                invalid_textured_nodes.append(sel)


    if invalidNodes:
        nodeString = ""
        for invalidNode in invalidNodes:
            nodeString += "%s, " % invalidNode.rpartition("|")[2]
        
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="Please legalize the %s names of the following groups and re-export:\n\n%s" % (currentAssetCategory[:-1], nodeString[:-2]), 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        cmds.select(invalidNodes, replace=True)

    # report back any nodes found with invalid textures
    if invalid_textured_nodes:
        node_string = ", ".join(invalid_textured_nodes)

        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center",
                message="Please fix the textures of the following groups and re-export:\n\n%s" % (node_string),
                button=["Ok"],
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        if invalidNodes:
            # add to selection of other invalid nodes
            cmds.select(invalid_textured_nodes, add=True)
        else:
            # select only these invalid nodes
            cmds.select(invalid_textured_nodes, replace=True)


    if resultTopNodes:
        try:
            cmds.select(resultTopNodes, r=1)
        except:
            pass
        
# end (do)
