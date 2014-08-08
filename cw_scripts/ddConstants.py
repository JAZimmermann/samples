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
    ddConstants.py
    
DESC
    Constants used in other scripts.

'''

import sys

scripts_path = "B:\home\johnz\scripts\cw_scripts"

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# environments
LAYOUT_DIR = r"B:\home\johnz\assets\environments\layoutFiles"
ASSETLIBRARY = r"B:\home\johnz\assets\environments\assetLibrary"
SHADERLIBRARY = r"B:\home\johnz\assets\environments\assetLibrary\tex\shaderLibrary"
IMAGELIBRARY = r"B:\home\johnz\assets\environments\assetLibrary\tex\imageLibrary"
TEXTURELIBRARY = r"B:\home\johnz\assets\environments\assetLibrary\tex\tif"

# characters
CHAR_ASSETLIBRARY = r"B:\home\johnz\assets\characters"
CHAR_SHADERLIBRARY = r"B:\home\johnz\assets\characters\tex\shaderLibrary"
CHAR_TEXTURELIBRARY = r"B:\home\johnz\assets\characters\tex\tif"
CHAR_IMAGELIBRARY = r"B:\home\johnz\assets\characters\tex\imageLibrary"


#ASSETLIBRARY = r"B:\show\TRUCE\assets\environments\assetLibrary"

ASSET_CATEGORIES = ["characters", "environments"]
ASSET_DIRECTORIES = { "characters": CHAR_ASSETLIBRARY, "environments": ASSETLIBRARY }
SHADER_DIRECTORIES = { "characters": CHAR_SHADERLIBRARY, "environments": SHADERLIBRARY }
TEXTURE_DIRECTORIES = { "characters": CHAR_TEXTURELIBRARY, "environments": TEXTURELIBRARY }
IMAGE_DIRECTORIES = { "characters": CHAR_IMAGELIBRARY, "environments": IMAGELIBRARY }

textureTypes = { "color":"DIFF", "specularColor":"SPEC", "normalCamera":"NRML" , "bumpValue":"NRML" }


"""
# environments
LAYOUT_DIR = r"B:\show\TRUCE\assets\environments\layoutFiles"
ASSETLIBRARY = r"B:\show\TRUCE\assets\environments\assetLibrary"
SHADERLIBRARY  = r"B:\show\TRUCE\assets\environments\assetLibrary\tex\shaderLibrary"
IMAGELIBRARY = r"B:\show\TRUCE\assets\environments\assetLibrary\tex\imageLibrary"
TEXTURELIBRARY= r"B:\show\TRUCE\assets\environments\assetLibrary\tex\tif"

# characters
CHAR_ASSETLIBRARY = r"B:\show\TRUCE\assets\characters"
CHAR_SHADERLIBRARY = r"B:\show\TRUCE\assets\characters\tex\shaderLibrary"
CHAR_TEXTURELIBRARY = r"B:\show\TRUCE\assets\characters\tex\tif"
CHAR_IMAGELIBRARY= r"B:\show\TRUCE\assets\characters\tex\imageLibrary"

ASSET_CATEGORIES = ["characters", "environments"]
ASSET_DIRECTORIES = {"characters": CHAR_ASSETLIBRARY, "environments": ASSETLIBRARY}
SHADER_DIRECTORIES = {"characters": CHAR_SHADERLIBRARY, "environments": SHADERLIBRARY}
TEXTURE_DIRECTORIES = {"characters": CHAR_TEXTURELIBRARY, "environments": TEXTURELIBRARY}
IMAGE_DIRECTORIES = { "characters": CHAR_IMAGELIBRARY, "environments": IMAGELIBRARY}

textureTypes = {"color":"DIFF", "specularColor":"SPEC", "normalCamera":"NRML" , "bumpValue":"NRML"}

"""