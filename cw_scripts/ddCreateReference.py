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
    ddCreateReference.py

DESC
    Creates reference of asset.
    
USAGE
    ddCreateReference.do()
    
'''


# MAYA
import maya.cmds as cmds

# VAD
import ddConstants; reload(ddConstants)


def do(currentAssetLibrary=ddConstants.ASSETLIBRARY):
    '''Creates reference.
    '''
    cmds.namespace(setNamespace=":")
    
    # Select file from file browser dialog.
    filename = cmds.fileDialog2(
            fileMode=1, caption="Reference Asset", 
            startingDirectory=currentAssetLibrary, okCaption="Reference")
    if not filename: 
        return
    
    filename = filename[0]
    # Create namespace.
    namespace = filename.rpartition("/")[2].rpartition(".")[0]
    # Reference asset under namespace.
    cmds.file(filename, reference=True, namespace=namespace)
    
# end (do)
