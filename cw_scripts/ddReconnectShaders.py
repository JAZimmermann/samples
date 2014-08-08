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
# $Date: 2014-07-11$
# $Revision: 1.0$
# $Author: cwong $
#


'''
NAME
    ddReconnectShaders.py

DESC
    Reconnects to published shaders using surface shader node. 

USAGE
    ddReconnectShaders.do()
    
FUNCTIONS
    getConnectedShadingEngine()
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
import ddRemoveNamespaces; reload(ddRemoveNamespaces)


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

   
def do():
    shaderList = list()
    shadingEngines = cmds.ls(type="shadingEngine")
    for shadingEngine in shadingEngines:
        cnx = [x for x in (cmds.listConnections("%s.surfaceShader" % shadingEngine) or []) if x.endswith("_SHD")]
        if cnx:
            shaderList.append(cnx[0])
    shaderList = list(set(shaderList))
    
    foundShaders = list()
    
    for assetCategory in ['environments', 'characters']:
        currentShaderLibrary = ddConstants.SHADER_DIRECTORIES[assetCategory]
        categories = [ x for x in (os.listdir(currentShaderLibrary) or []) if os.path.isdir(os.path.join(currentShaderLibrary, x)) and not x.startswith(".") and not x in ["Keyboard", "Materials", "_Materials"] ]
        
        # Loop through the shader categories.
        for category in categories:
            directory = os.path.join(currentShaderLibrary, category)
            # Get the list of swatch files on disk for the category.
            swatchFiles = [x.replace(".png", "") for x in os.listdir(directory) if x.endswith(".png")]
            
            for shader in shaderList:
                # For each category, loop through the shaders, looking for a match.
                meshList = list()
                swatch = shader.replace("_SHD", "")
                
                if swatch in swatchFiles:
                    # If a match is found, import and connect it.
                    tempGrp = "tempImportedGrp"
                    if cmds.objExists(tempGrp):
                        cmds.delete(tempGrp)
                    
                    foundShaders.append(shader)
                    connectedShadingEngines = cmds.listConnections("%s.outColor" % shader) or []
                    for connectedShadingEngine in connectedShadingEngines:
                        meshSubList = [x for x in (cmds.listHistory(connectedShadingEngine) or []) if cmds.nodeType(x) == "mesh"]
                        if meshSubList:
                            meshList.extend(meshSubList)
                        cmds.delete(connectedShadingEngine)
                        
                    cmds.delete(shader)
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
                                            
                    sys.stdout.write("Shader reconnected: %s\n" % shader)
                                    
                    if cmds.objExists(tempGrp):
                        cmds.delete(tempGrp)
                        
    strayNodes = cmds.ls("tempImportedGrp*")
    if strayNodes:
        try:
            cmds.delete(strayNodes)
        except:
            pass
    
    # Figure out if any shaders were not reconnected.
    shaderNotFoundStr = ""
    for shaderName in shaderList:
        if not shaderName in foundShaders:
            shaderNotFoundStr += "%s, " % shaderName
            
    if shaderNotFoundStr:
        sys.stdout.write("Shaders not found for %s\n" % shaderNotFoundStr[:-1])
    else:
        sys.stdout.write("All shaders have been reconnected.\n")
        
# end (do)