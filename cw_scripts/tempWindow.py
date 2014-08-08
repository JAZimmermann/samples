if cmds.window("layoutPublishHelpWIN", query=True, exists=True):
    cmds.deleteUI("layoutPublishHelpWIN")

# Window.
helpWindow = cmds.window(
        "layoutPublishHelpWIN", title="Layout Publish Help", sizeable=True, 
        resizeToFitChildren=True, widthHeight=(900, 450)
        )
        
# Main form layout.
helpFL = cmds.formLayout("layoutPublishHelpFL", numberOfDivisions=100, parent=helpWindow)
helpSF = cmds.scrollField("layoutPublishHelpSF", editable=False, wordWrap=True, text='INSTRUCTIONS\n\n(1) First, do one of the following:\n\n    (A) Run the "Clean Scene" button.\n\n            - OR -\n\n    (B) Step through the following buttons:\n\n            - Show Unpublished Assets (Make sure all assets have been published)\n            - Show Referenced Edits / Fix Reference Edits\n            - Import All From Reference\n            - Show Invalid Names / Fix Invalid Names\n            - Show Invalid Textures\n            - Show Invalid Pivots / Fix Invalid Pivots\n            - Show Vertex Edits / Fix Vertex Edits\n            - Show Duplicate Node Names / Fix Duplicate Node Names\n            - Fix Instance Numbers\n            - Optimize and Clean\n            - Add GRP to Node Names\n            - Add Metadata to GRP Nodes\n            - Create Null Hierarchy\n\n(2) Next, take a look at the scene to make sure nothing has changed.\n\n(3) Clean out any unnecessary layers and sets.\n\n(4) Check that everything has been correctly parented under the master nodes.\n\n(5) Finally, click "Publish Scene".\n\n\n . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .\n\n\n' )

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='BUTTONS\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Clean Scene\nSteps through the buttons in (B) above. Ideally all assets should be referenced before running this tool as proof of asset publish. An attempt is made to remove reference edits before all objects are imported from reference. Duplicate node names are removed by incrementing instance numbers. Pivot offsets are checked, metadata is added to the top group nodes and construction history is deleted. The scene is then optimized which may take a few minutes. Any remaining render layers and duplicate script nodes are removed.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Publish Scene\nSaves out a mayaAscii file and parses the file to remove extraneous data. The file name should match the name on the env_master null but without "env_" at the beginning and "_GRP" at the end. For example: 0230_UFJ_riverbank_v001. Also exports an FBX file.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Clear Display\nClears the display window of any data.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Refresh\nUpdates the data in the display window.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Unpublished Assets\nDisplays list of assets not found in the Asset Library.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Published Assets\nDisplays list of assets found in the Asset Library.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Reference Edits\nDisplays list of top group nodes which have reference edits including manual shader adjustments.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Reference Edits\nAttempts to remove reference edits from nodes listed in display window. If removal fails, will try to replace with a clean reference.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Referenced Nodes\nDisplays list of all referenced GRP nodes in scene file.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Non-Referenced Nodes\nDisplays list of all non-referenced GRP nodes in scene file.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Replace All With References\nReplaces all assets with clean references from the Asset Library.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Import All From Reference\nImports all assets from reference.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Names\nRuns the Check Names script on the entire scene file.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Invalid Names\nAttempts to fix names listed in the display window by removing namespaces, checking geo instance numbers and fixing duplicate node names. Upon occasion it may be necessary to hit this button twice.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Textures\nChecks if textures have been published in the Shader Library.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Invalid Pivots\nRuns the Check Pivot Offsets script on the entire scene file.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Invalid Pivots\nRuns the Reset Geo Metadata script on the items listed in the display window.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Vertex Edits\nDisplays nodes which have vertex edits.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Vertex Edits\nRemoves vertex edits from nodes listed in display window.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Show Duplicate Node Names\nChecks scene file for duplicate node names.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Duplicate Node Names\nFixes duplicate node names by incrementing instances.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Instance Numbers\nRuns Check Geo Instance Number script on all top groups.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Optimize and Clean\nRuns optimize scene, deletes unused nodes, deletes duplicate shading networks, cleans up shading network node names, deletes history and removes other stray nodes.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Add GRP to Node Names\nAdds "GRP" to names of all trackable nodes.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Add Metadata to GRP Nodes\nAdds metadata to all nodes ending with "_GRP".\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Create Null Hierarchy\nCreates the scene hierarchy nulls.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=0, insertText='- Fix Wait Cursor\nIf a script errors, the wait cursor may get stuck in the spinning mode. Click this button to fix it. Avoid clicking this button if the script has not errored. It will not affect execution but the script has not finished.\n\n\n')

cmds.scrollField(helpSF, edit=True, insertionPosition=1, insertText='\n')

cmds.formLayout(helpFL, edit=True, 
    attachForm=[ (helpSF, "top", 15), 
                 (helpSF, "left", 15), 
                 (helpSF, "right", 15),
                 (helpSF, "bottom", 15)])


cmds.showWindow(helpWindow)