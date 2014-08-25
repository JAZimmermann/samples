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
    ddAssetNamer.py

DESC
    Names assets. Artist creates a group above meshes, selects group and runs script.
    - Provides drop downs for each folder in asset library to create file path.
    - Fields for descriptor name, asset letter, asset variant, version number. 
    - Asks for mesh descriptor for each mesh in group.
    - Checks if textures files are saved in assetLibrary and file format extension is ".tif".
    - Exports DIFF, SPEC, NRML map files per GEO, if exist

USAGE
    ddAssetNamer.do()
    
FUNCTIONS
    buildSDir01()
    updateSDir01()
    buildSDir02()
    updateSDir02()
    buildSDir03()
    updateSDir03()
    buildAssetLetter()
    updateAssetLetter()
    buildAssetVariant()
    updateAssetVariant()
    doRenameNodes()
    doRenameChesspiece()
    doRenameGroup()
    doRenameGeo()
    getMeshDescriptor()
    do()
    
'''


# MAYA
import maya.cmds as cmds

# PYTHON
import os
import sys
from functools import partial

# VAD
import ddConstants; reload(ddConstants)


def buildSDir01(currentAssetLibrary=ddConstants.ASSETLIBRARY):
    '''Build first subdirectory list.
    '''
    tfg = "sDir01TFG"
    kids = cmds.textFieldGrp(tfg, query=True, popupMenuArray=True)
    if kids:
        cmds.deleteUI(kids)
    menu = cmds.popupMenu('%s_menu' % tfg, parent=tfg)
    ignoreList = ["tex", ".DS_Store", "DELETE", "old characters", "reference_misc", "old"]
    
    dataList = [x for x in (os.listdir(currentAssetLibrary) or []) if not x in ignoreList and not x.startswith("_")]
    dataList.sort()
    defaultLabel = "Select folder"
    cmds.menuItem(parent=menu, label=defaultLabel, command=partial(updateSDir01, defaultLabel, currentAssetLibrary))
    for data in dataList:
        cmds.menuItem("%sMI" % data, parent=menu, label=data, command=partial(updateSDir01, data, currentAssetLibrary))
    cmds.textFieldGrp(tfg, edit=True, text=defaultLabel)
    
# end (buildSDir01)


def updateSDir01(data, currentAssetLibrary=ddConstants.ASSETLIBRARY, arg=None):
    '''Update first subdirectory field.
    '''
    defaultLabel = "Select folder"
    cmds.textFieldGrp("sDir01TFG", edit=True, text=data)
    if not data == defaultLabel:
        buildSDir02(sDir01=data, currentAssetLibrary=currentAssetLibrary)

    if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
        if data == "hero":
            cmds.textFieldGrp("descriptorTFG", edit=True, enable=False)
        elif data == "secondary" or data == "background":
            cmds.textFieldGrp("descriptorTFG", edit=True, enable=True, text="(optional variant)")

# end updateSDir01


def buildSDir02(sDir01, currentAssetLibrary=ddConstants.ASSETLIBRARY):
    '''Build second subdirectory list.
    '''
    tfg = "sDir02TFG"
    dataList = None
    if not sDir01 == "---":
        dirPath = ""
        if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
            # characters
            dirPath = os.path.join(currentAssetLibrary, sDir01)
            dataList = [x for x in (os.listdir(dirPath) or []) if not (x == ".DS_Store") and not x.startswith("_")]
            dataList.sort()
        else:
            # environments
            dirPath = os.path.join(currentAssetLibrary, sDir01)
            if sDir01 in ["prop", "char"]:
                dataList = {}
            else:
                dataList = [x for x in (os.listdir(dirPath) or []) if not (x == ".DS_Store")]
                dataList.sort()
    
    kids = cmds.textFieldGrp(tfg, query=True, popupMenuArray=True)
    if kids:
        cmds.deleteUI(kids)
    menu = cmds.popupMenu('%s_menu' % tfg, parent=tfg)
    
    if dataList:
        defaultLabel = "Select subfolder"
        if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
            defaultLabel = "Select character"

        cmds.menuItem(parent=menu, label=defaultLabel, command=partial(updateSDir02, sDir01, defaultLabel, currentAssetLibrary))
        for data in dataList:
            cmds.menuItem("%sMI" % data, parent=menu, label=data, command=partial(updateSDir02, sDir01, data, currentAssetLibrary))
        cmds.textFieldGrp(tfg, edit=True, text=defaultLabel)
    else:
        cmds.menuItem(parent=menu, label="---", command=partial(updateSDir02, sDir01, "---", currentAssetLibrary))
        cmds.textFieldGrp(tfg, edit=True, text="---")
        updateSDir02(sDir01=sDir01, data="---", currentAssetLibrary=currentAssetLibrary)
        
# end (buildSDir02)


def updateSDir02(sDir01, data, currentAssetLibrary=ddConstants.ASSETLIBRARY, arg=None):
    '''Update second subdirectory field.
    '''
    cmds.textFieldGrp("sDir02TFG", edit=True, text=data)
    if not data == "Select folder":
        buildSDir03(sDir01=sDir01, sDir02=data, currentAssetLibrary=currentAssetLibrary)
                
# end updateSDir02


def buildSDir03(sDir01, sDir02, currentAssetLibrary=ddConstants.ASSETLIBRARY):
    '''Build third subdirectory list.
    '''
    tfg = "sDir03TFG"
    dataList = None

    if not sDir02 == "---":
        if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
            # characters
            dataList = ["CPF (full, riggable)", "CPD (dirty, decimated)", "CPO (origami)", "CPS (segmented)"]
        else:
            # environments
            dirPath = os.path.join(currentAssetLibrary, sDir01, sDir02)
            if sDir02 in ["arc", "dom", "fx", "ter"]:
                dataList = {}
            else:
                dataList = [x for x in (os.listdir(dirPath) or []) if not (x == ".DS_Store") and not x.startswith("_")]
                dataList.sort()
    
    kids = cmds.textFieldGrp(tfg, query=True, popupMenuArray=True)
    if kids:
        cmds.deleteUI(kids)
    menu = cmds.popupMenu('%s_menu' % tfg, parent=tfg)
    
    if dataList:
        defaultLabel = "Select subfolder"
        if currentAssetLibrary == ddConstants.CHAR_ASSETLIBRARY:
            defaultLabel = "Select chesspiece type"
        cmds.menuItem(parent=menu, label=defaultLabel, command=partial(updateSDir03, defaultLabel, currentAssetLibrary))
        for data in dataList:
            cmds.menuItem("%sMI" % data, parent=menu, label=data, command=partial(updateSDir03, data, currentAssetLibrary))
        cmds.textFieldGrp(tfg, edit=True, text=defaultLabel)
    else:
        cmds.menuItem(parent=menu, label="---", command=partial(updateSDir03, "---", currentAssetLibrary))
        cmds.textFieldGrp(tfg, edit=True, text="---")
        
# end (buildSDir03)


def updateSDir03(data, currentAssetLibrary=ddConstants.ASSETLIBRARY, arg=None):
    '''Update third subdirectory field.
    '''
    cmds.textFieldGrp("sDir03TFG", edit=True, text=data)
    
# end (updateSDir03)


def buildAssetLetter():
    '''Build asset letter list.
    '''
    tfg = "assetLetterTFG"
    kids = cmds.textFieldGrp(tfg, query=True, popupMenuArray=True)
    if kids:
        cmds.deleteUI(kids)
    menu = cmds.popupMenu('%s_menu' % tfg, parent=tfg)
    
    for i in range(65, 91):
        cmds.menuItem("%sLMI" % chr(i), parent=menu, label=chr(i), command=partial(updateAssetLetter, chr(i)))
    cmds.textFieldGrp(tfg, edit=True, text="A")
    
# end (buildAssetLetter)


def updateAssetLetter(data, arg=None):
    '''Update asset letter field.
    '''
    cmds.textFieldGrp("assetLetterTFG", edit=True, text=data)
    
# end (updateAssetLetter)


def buildAssetVariant():
    '''Build asset letter list.
    '''
    tfg = "assetVariantTFG"
    kids = cmds.textFieldGrp(tfg, query=True, popupMenuArray=True)
    if kids:
        cmds.deleteUI(kids)
    menu = cmds.popupMenu('%s_menu' % tfg, parent=tfg)
    
    for i in range(65, 91):
        cmds.menuItem("%sVMI" % chr(i), parent=menu, label=chr(i), command=partial(updateAssetVariant, chr(i)))
    cmds.textFieldGrp(tfg, edit=True, text="A")
    
# end (buildAssetVariant)


def updateAssetVariant(data, arg=None):
    '''Update asset letter field.
    '''
    cmds.textFieldGrp("assetVariantTFG", edit=True, text=data)
    
# end (updateAssetVariant)


def doRenameNodes(node, currentAssetCategory="environments", arg=None):
    '''Generates appropriate names for category and renames nodes.
    '''
    if currentAssetCategory == "characters":
        doRenameChesspieceGroup(node)
    elif currentAssetCategory == "environments":
        doRenameGroup(node)


def doRenameChesspieceGroup(node):
    '''
    Renames character chessPiece group, creating the group if necessary.
    
    Naming for the CPS (segmented) chesspiece is non-standard for rigging purposes.
    The version is stored as an attribute and there is no instance number.
    '''
    geoNode = ""
    grpNode = ""
    
    # Determine if node is a GEO node or a GRP node.
    children = cmds.listRelatives(node, shapes=True)
    if children:
        # Node is a GEO node.
        geoNode = node
    
        # Determine if node has a parent and node is only child.
        parent = cmds.listRelatives(node, parent=True)
        if parent:
            children = [x for x in cmds.listRelatives(parent[0], children=True) if not x == node]
            if not children:
                grpNode = parent[0]
        
        # If node does not have a valid parent, create one and parent the node to the new parent.
        if not parent:
            grpNode = cmds.createNode("transform")
            #cmds.delete(cmds.parentConstraint(node, grpNode, maintainOffset=False))
            cmds.parent(node, grpNode)
    else:
        # Node is a GRP node.
        grpNode = node
    
    # Select the GRP node for the user to see.
    cmds.select(grpNode, r=1)
    cmds.refresh()
    result = "OK"
    meshDescriptor = ""
    meshName = ""
    
    sDir01 = cmds.textFieldGrp("sDir01TFG", query=True, text=True)
    sDir02 = cmds.textFieldGrp("sDir02TFG", query=True, text=True)
    sDir03 = cmds.textFieldGrp("sDir03TFG", query=True, text=True)
    descriptor = cmds.textFieldGrp("descriptorTFG", query=True, text=True)
    versionNumber = cmds.textFieldGrp("versionNumberTFG", query=True, text=True)
    
    if sDir02 == "Select character":
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="No character has been selected.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    if sDir03 == "Select chesspiece type":
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="No chesspiece type has been selected.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
        
    if not versionNumber.isdigit():
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="Version number must be a number.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
        
    charType = { "hero": "hero", "background": "bg", "secondary": "sec" }
    chesspieceType = sDir03.partition(" ")[0]
    name = "char_%s_%s" % (charType[sDir01], sDir02)
    
    if descriptor and not descriptor == "(optional variant)":
        descriptor = "%s%s" % (descriptor[0].lower(), descriptor[1:])
        name += "_%s_%s_GRP_v%03d_1" % (descriptor.replace("_", ""), chesspieceType, int(versionNumber))
    else:
        name += "_%s_GRP_v%03d_1" % (chesspieceType, int(versionNumber))
    
    divider = "%s_GRP" % chesspieceType               
    newNode = cmds.rename(grpNode, name)
    
    if not newNode.rpartition("|")[2] == name:
        cmds.warning("Name %s exists: choose a new name or parent to a different group." % name)
        cmds.deleteUI("assetNamerWIN")
        return
    
    # Rename geo
    children = cmds.listRelatives(newNode, path=True, allDescendents=True) or []
    nodeList = [x for x in children if cmds.nodeType(x) == "transform"]
    if nodeList:
        if cmds.window("assetNamerWIN", query=True, exists=True):
            cmds.deleteUI("assetNamerWIN")
        
        override = False
        result = ""
        for nodeName in nodeList:
            result, override = doRenameGeo(geoNode=nodeName, grpNode=newNode, override=override, divider=divider)
            if result == "Cancel All":
                return
    
    return result
    
# end (doRenameChesspiece)


def doRenameGroup(node, arg=None):
    '''Generates name and renames group.
    '''
    sDir01 = cmds.textFieldGrp("sDir01TFG", query=True, text=True)
    sDir02 = cmds.textFieldGrp("sDir02TFG", query=True, text=True)
    sDir03 = cmds.textFieldGrp("sDir03TFG", query=True, text=True)
    descriptor = cmds.textFieldGrp("descriptorTFG", query=True, text=True)
    assetLetter = cmds.textFieldGrp("assetLetterTFG", query=True, text=True)
    assetVariant = cmds.textFieldGrp("assetVariantTFG", query=True, text=True)
    versionNumber = cmds.textFieldGrp("versionNumberTFG", query=True, text=True)
    
    if sDir01 == "Select folder":
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="No folder has been selected.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    if sDir02 == "Select subfolder":
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="No subfolder has been selected.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    if descriptor == "":
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="No descriptor has been entered.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    if not versionNumber.isdigit():
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="Version number must be a number.", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
    
    name = sDir01
    for item in [sDir02, sDir03]:
        if not item == "---":
            name += "_%s" % item
            
    descriptor = "%s%s" % (descriptor[0].lower(), descriptor[1:])
    name += "_%s%sv%s_GRP_v%03d_1" % (descriptor, assetLetter, assetVariant, int(versionNumber))
    
    newNode = cmds.rename(node, name)
    if not newNode.rpartition("|")[2] == name:
        cmds.warning("Name %s exists: choose a new name or parent to a different group." % name)
        cmds.deleteUI("assetNamerWIN")
        return
    
    # Rename geo
    children = cmds.listRelatives(newNode, path=True, allDescendents=True) or []
    nodeList = [x for x in children if cmds.nodeType(x) == "transform"]
    if nodeList:
        if cmds.window("assetNamerWIN", query=True, exists=True):
            cmds.deleteUI("assetNamerWIN")
        
        override = False
        result = ""

        result, override = do_rename_geo_nodes(nodeList, newNode)
        if result == "Cancel All":
            return

        # for nodeName in nodeList:
        #     result, override = doRenameGeo(geoNode=nodeName, grpNode=newNode, override=override, divider="GRP")
        #     if result == "Cancel All":
        #         return
    
    cmds.select(newNode, r=1)
    sys.stdout.write("Assets named. \n")
    
# end (doRenameGroup)


def do_rename_geo_nodes(node_list, group_node):
    '''
    renames provided geo nodes

    :type   node_list: C{list}
    :param  node_list: list of transforms under group to process
    :type   group_node: C{str}
    :param  group_node: name of parent group node
    '''
    print "testing new rename geo nodes"
    all_mesh_descriptor = ''
    override = False
    result = ""
    divider = "GRP"

    for node_num, node_name in enumerate(node_list):
        cmds.select(node_name, r=1)
        cmds.refresh()
        result = "OK"
        meshDescriptor = ""
        meshName = ""
        children = cmds.listRelatives(group_node, children=True)
        baseChildren = list()

        for child in children:
            baseChildren.append(child.rpartition("|")[2])

        if not (divider == "GRP") and len(children) == 1:
            meshName = "%s_GEO_1" % group_node.rpartition("|")[2].partition("_GRP")[0]
        else:
            while result == "OK" and meshDescriptor == "":
                result, meshDescriptor, override = getMeshDescriptor(node_name, group_node, override, divider)

                if result == "Cancel All":
                    return result, override

                if result == "OK To All":
                    all_mesh_descriptor = "%s%s" % (meshDescriptor[0].lower(), meshDescriptor[1:])
                    result = "OK"

                if result == "OK" and not meshDescriptor == "":
                    if all_mesh_descriptor:
                        meshDescriptor = "%s%03d" % (all_mesh_descriptor, node_num)

                    meshDescriptor = "%s%s" % (meshDescriptor[0].lower(), meshDescriptor[1:])
                    meshName = "%s%s_%s_1" % (group_node.rpartition("|")[2].partition(divider)[0], meshDescriptor, divider.replace("GRP", "GEO"))
                    if (meshName in children) and not(meshName == node_name.rpartition("|")[2]):
                        cmds.confirmDialog(
                                title="Warning", messageAlign="center",
                                message="Enter a unique mesh descriptor.",
                                button=["Ok"],
                                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                                )
                        result = "OK"
                        meshDescriptor = ""
                        override = False

        if result == "OK":
            newMeshName = cmds.rename(node_name, meshName)
            shapeNodes = [x for x in (cmds.listRelatives(newMeshName, path=True, shapes=True) or []) if cmds.nodeType(x) == "mesh"]
            for shapeNode in shapeNodes:
                if cmds.getAttr("%s.intermediateObject" % shapeNode):
                    continue
                cmds.rename(shapeNode, "%sShape" % meshName)

    cmds.select(cl=1)

    return result, override


# def doRenameGeo(geoNode, grpNode, override=False, divider="GRP"):
#     '''Renames geo node to match group above plus mesh descriptor.
#     '''
#     cmds.select(geoNode, r=1)
#     cmds.refresh()
#     result = "OK"
#     meshDescriptor = ""
#     meshName = ""
#     children = cmds.listRelatives(grpNode, children=True)
#     baseChildren = list()
#
#     for child in children:
#         baseChildren.append(child.rpartition("|")[2])
#
#     if not (divider == "GRP") and len(children) == 1:
#         meshName = "%s_GEO_1" % grpNode.rpartition("|")[2].partition("_GRP")[0]
#     else:
#         while result == "OK" and meshDescriptor == "":
#             result, meshDescriptor, override = getMeshDescriptor(geoNode, grpNode, override, divider)
#
#             if result == "Cancel All":
#                 return result, override
#
#             if result == "OK" and not meshDescriptor == "":
#                 meshDescriptor = "%s%s" % (meshDescriptor[0].lower(), meshDescriptor[1:])
#                 meshName = "%s%s_%s_1" % (grpNode.rpartition("|")[2].partition(divider)[0], meshDescriptor, divider.replace("GRP", "GEO"))
#                 if (meshName in children) and not(meshName == geoNode.rpartition("|")[2]):
#                     cmds.confirmDialog(
#                             title="Warning", messageAlign="center",
#                             message="Enter a unique mesh descriptor.",
#                             button=["Ok"],
#                             defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
#                             )
#                     result = "OK"
#                     meshDescriptor = ""
#                     override = False
#
#     if result == "OK":
#         newMeshName = cmds.rename(geoNode, meshName)
#         shapeNodes = [x for x in (cmds.listRelatives(newMeshName, path=True, shapes=True) or []) if cmds.nodeType(x) == "mesh"]
#         for shapeNode in shapeNodes:
#             if cmds.getAttr("%s.intermediateObject" % shapeNode):
#                 continue
#             cmds.rename(shapeNode, "%sShape" % meshName)
#
#     cmds.select(cl=1)
#
#     return result, override
#
# # end (doRenameGeo)


def getMeshDescriptor(node, grpNode, override=False, divider="GRP"):
    '''Gets mesh descriptor for GEO nodes.
    '''
    currentGrp = grpNode.rpartition("|")[2]
    currentNode = node.rpartition("|")[2]
    assetName, grp, versionAndNumber = currentGrp.partition(divider)
    geoName, geo, instanceNumber = currentNode.partition("GEO")
    meshDescriptor = currentNode.rpartition(":")[2].replace(assetName, "", 1).replace("_GEO%s" % instanceNumber, "", 1).rpartition("|")[2].rpartition("_")[2]
    if "CPS" in divider:
        meshDescriptor = currentNode
    result = "OK"
    
    if not override:
        result = cmds.promptDialog(
                title="Rename Mesh", 
                message='Enter mesh descriptor for "%s": ' % currentNode, text=meshDescriptor, 
                button=["OK", "OK To All", "Cancel", "Cancel All"], 
                defaultButton="OK", cancelButton="Cancel", dismissString="Cancel"
                )
        if result == "OK":
            meshDescriptor = cmds.promptDialog(query=True, text=True)
        elif result == "OK To All":
            meshDescriptor = cmds.promptDialog(query=True, text=True)
            # result = "OK"
            override = True
        
    return result, meshDescriptor, override
    
# end (getMeshDescriptor)


def do(nodes=None, currentAssetCategory="environments"):
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
        nodes = cmds.ls(selection=True, long=True) or []
        
    if not isinstance(nodes, list):
        nodes = [nodes]
        
    if not len(nodes) == 1:
        confirm = cmds.confirmDialog(
                title="Warning", messageAlign="center", 
                message="  Select only one group object.    ", 
                button=["Ok"], 
                defaultButton="Ok", cancelButton="Ok", dismissString="Ok"
                )
        return
        
    # Name the nodes
    if cmds.window("assetNamerWIN", query=True, exists=True):
        cmds.deleteUI("assetNamerWIN")
        
    # Build the window
    window = cmds.window(
            "assetNamerWIN", title="Asset Namer", sizeable=False, 
            resizeToFitChildren=True, widthHeight=(625, 135)
            )
    mainFL = cmds.formLayout("mainFL", numberOfDivisions=100)
    dirPathRL = cmds.rowLayout("dirPathRL", numberOfColumns=3, cw3=[200,200,200], height=25, parent=mainFL)
    
    sDir01TFG = cmds.textFieldGrp("sDir01TFG", editable=False, label="", cw2=[10,190], text="", parent=dirPathRL)
    sDir02TFG = cmds.textFieldGrp("sDir02TFG", editable=False, label="", cw2=[10,190], text="", parent=dirPathRL)
    sDir03TFG = cmds.textFieldGrp("sDir03TFG", editable=False, label="", cw2=[10,190], text="", parent=dirPathRL)
    
    cmds.popupMenu("%s_menu" % sDir01TFG, parent=sDir01TFG)
    cmds.popupMenu("%s_menu" % sDir02TFG, parent=sDir02TFG)
    cmds.popupMenu("%s_menu" % sDir03TFG, parent=sDir03TFG)
    
    descriptorRL = cmds.rowLayout(
            "descriptorRL", numberOfColumns=4, cw4=[240,110,115,125], height=25, parent=mainFL
            )
    descriptorTFG = cmds.textFieldGrp(
            "descriptorTFG", editable=True, label="Descriptor  ", 
            cw2=[65,185], columnAlign2=["left", "left"], text="", parent=descriptorRL
            )
    assetLetterTFG = cmds.textFieldGrp(
            "assetLetterTFG", editable=False, label="Asset Letter  ", 
            cw2=[85,25], columnAlign2=["right", "left"], text="", parent=descriptorRL
            )
    assetVariantTFG = cmds.textFieldGrp(
            "assetVariantTFG", editable=False, label="Asset Variant  ", 
            cw2=[90,25], columnAlign2=["right", "left"], text="", parent=descriptorRL
            )
    versionNumberTFG = cmds.textFieldGrp(
            "versionNumberTFG", editable=True, label="Version Number  ", 
            cw2=[100,25], columnAlign2=["right", "left"], text="1", parent=descriptorRL
            )
    
    if currentAssetCategory == "environments":
        cmds.popupMenu("%s_menu" % assetLetterTFG, parent=assetLetterTFG)
        cmds.popupMenu("%s_menu" % assetVariantTFG, parent=assetVariantTFG)
    elif currentAssetCategory == "characters":
        cmds.textFieldGrp(assetLetterTFG, edit=True, enable=False)
        cmds.textFieldGrp(assetVariantTFG, edit=True, enable=False)
    
    cmds.popupMenu("%s_menu" % versionNumberTFG, parent=versionNumberTFG)        
    
    renameButton = cmds.button("renameBTN", label="Rename", height=30,  parent=mainFL, c=partial(doRenameNodes, nodes[0], currentAssetCategory))
    
    cmds.formLayout(mainFL, edit=True, 
        attachForm=[ (dirPathRL, "top", 15), (dirPathRL, "left", 10), (dirPathRL, "right", 10),
                     (descriptorRL, "left", 15), (descriptorRL, "right", 15),
                     (renameButton, "left", 15), (renameButton, "right", 15),
                     (renameButton, "bottom", 15) ],
        attachControl=[ (descriptorRL, "top", 15, dirPathRL) ] )
        
    window = cmds.window("assetNamerWIN", edit=True, widthHeight=(635, 140))
    
    buildSDir01(currentAssetLibrary)
    buildAssetLetter()
    buildAssetVariant()
    
    if currentAssetCategory == "environments":
        currentNode = nodes[0].rpartition("|")[2]
        assetName, grp, versionAndNumber = currentNode.partition("_GRP_")
        assetPath, underscore, assetDescriptor = assetName.rpartition("_")
        assetParts = assetPath.split("_")
        if assetParts:
            try: 
                menuItems = cmds.popupMenu("sDir01TFG_menu", query=True, itemArray=True)
                if "%sMI"%assetParts[0] in menuItems:
                    updateSDir01(assetParts[0])
            except: pass
            if len(assetParts) > 1:
                try: 
                    menuItems = cmds.popupMenu("sDir02TFG_menu", query=True, itemArray=True)
                    if "%sMI"%assetParts[1] in menuItems:
                        updateSDir02(assetParts[0], assetParts[1])
                        
                except: pass
            if len(assetParts) > 2:
                try:
                    menuItems = cmds.popupMenu("sDir03TFG_menu", query=True, itemArray=True)
                    if "%sMI"%assetParts[2] in menuItems:
                        updateSDir03(assetParts[2])
                except: pass
        if assetDescriptor:
            asset, v, variant = assetDescriptor[-3:].partition("v")
            if asset and variant:
                if v == "v" and (ord(asset) in range(65, 91)) and (ord(variant) in range(65, 91)):
                    cmds.textFieldGrp("descriptorTFG", edit=True, text=assetDescriptor[:-3])
                if not asset:
                    asset = "A"
                if not variant:
                    variant = "A"
                updateAssetLetter(asset)
                updateAssetVariant(variant)
            else:
                cmds.textFieldGrp("descriptorTFG", edit=True, text=assetDescriptor)
        if versionAndNumber:
            version = versionAndNumber.split("_")[0]
            version = version.replace("v00", "").replace("v0", "").replace("v", "")
            cmds.textFieldGrp("versionNumberTFG", edit=True, text=version)
            
    # else:
    #     currentNode = nodes[0].rpartition("|")[2]
    #
    #     chesspieceTypes = ["CPF", "CPO", "CPD", "CPS"]
    #     charType = { "hero": "hero", "bg": "background", "sec": "secondary" }
    #
    #     nodeSplits = currentNode.split("_")
    #     divider = ""
    #     dividerGrp = "_GRP_"
    #     for nodeSplit in nodeSplits:
    #         if nodeSplit in chesspieceTypes:
    #             divider = nodeSplit
    #             dividerGrp = "_%s_GRP_" % divider
    #
    #     assetName, grp, versionAndNumber = currentNode.partition(dividerGrp)
    #     assetParts = assetName.split("_")
    #     if assetParts:
    #         try:
    #             menuItems = cmds.popupMenu("sDir01TFG_menu", query=True, itemArray=True)
    #             if "%sMI" % charType[assetParts[1]] in menuItems:
    #                 updateSDir01(charType[assetParts[1]], currentAssetLibrary)
    #         except: pass
    #         if len(assetParts) > 1:
    #             try:
    #                 menuItems = cmds.popupMenu("sDir02TFG_menu", query=True, itemArray=True)
    #                 if "%sMI" % assetParts[2] in menuItems:
    #                     updateSDir02(charType[assetParts[1]], assetParts[2], currentAssetLibrary)
    #
    #             except: pass
    #         if len(assetParts) > 2:
    #             try:
    #                 menuItems = cmds.popupMenu("sDir03TFG_menu", query=True, itemArray=True)
    #                 for menuItem in menuItems:
    #                     if divider in menuItem:
    #                         chesspieceType = menuItem.replace("MI", "").replace("__", " (").replace("_", ")")
    #                         updateSDir03(chesspieceType, currentAssetLibrary)
    #
    #             except: pass
    #     if len(assetParts) > 3:
    #         cmds.textFieldGrp("descriptorTFG", edit=True, text=assetParts[3])
    #     if versionAndNumber:
    #         version = versionAndNumber.split("_")[0]
    #         version = version.replace("v00", "").replace("v0", "").replace("v", "")
    #         cmds.textFieldGrp("versionNumberTFG", edit=True, text=version)

            
    cmds.showWindow(window)
    
# end do()
