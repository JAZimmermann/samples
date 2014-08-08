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
    ddRemoveRequires.py

DESC
    Removes unnecessary "requires" statements from ".ma" file.
    
USAGE
    ddRemoveRequires.do()
'''

# MAYA
import maya.cmds as cmds

# PYTHON
import sys
import shutil


def do(path=None):
    '''
    Removes unnecessary "requires" statements from ".ma" file.
    @param path: Path to the mayaAscii file.
    '''
    if not path:
        return
    
    # Create a temporary file.
    outputPath = path.replace(".ma", "_o.ma")
    pluginsInUse = cmds.pluginInfo(query=True, pluginsInUse=True) or []
    actualPluginsInUse = list()
    for i in range(0, len(pluginsInUse), 2):
        actualPluginsInUse.append(pluginsInUse[i])
    print actualPluginsInUse
    # Read the original file, write to the temporary file.
    f = open(path, "r")
    o = open(outputPath, "w")
    scn = False

    # collect lines in maya ascii file
    lines = f.readlines()
    # setup variable to help skip lines within a block
    continue_line = 0

    # Write lines to temporary file, skipping unnecessary "requires" blocks.
    for i in range(0, len(lines)):
        if i > continue_line or i == 0:
            # if lines[i].startswith('requires -nodeType "mentalray'):
            #     requiresMentalRay = True

            if lines[i].startswith("requires"):
                if not "maya" in lines[i]:
                    req_data = {}
                    req_data['block_lines'] = []
                    req_data['start_line'] = i
                    req_data['block_lines'].append(lines[i])
                    # locate all lines for requires block
                    if not lines[i].rstrip().endswith(';'):
                        end_of_command = False
                        while not end_of_command:
                            i += 1
                            req_data['block_lines'].append(lines[i])
                            if lines[i].rstrip().endswith(';'):
                                end_of_command = True
                        if i > req_data['start_line']:
                            continue_line = i

                    req_data['cmd_line'] = ' '.join(req_data['block_lines'])
                    # check if in use plugin is part of the requires command
                    found = False
                    for plugin in actualPluginsInUse:
                        # Keep the line if the plugin is actually used.
                        if plugin in req_data['cmd_line']:
                            found = True
                            break

                    # write out requires block to temp file if needed
                    if req_data['block_lines'] and found:
                        o.writelines(req_data['block_lines'])
                    continue

            # Ignore the lengthy externalContentTable at end of file.
            if "externalContentTable" in lines[i]:
                scn = True
                continue
            # This is part of the externalContentTable.
            if "-scn;" in lines[i]:
                continue
            # Keep everything else.
            o.write(lines[i])

    # Close the files.
    f.close()
    o.close()
    
    # # Move the temporary file onto the original file.
    shutil.move(outputPath, path)
    
# end (do)
