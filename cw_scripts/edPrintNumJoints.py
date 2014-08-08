def edPrintJoints():
  """Select the root joint and run to print
  """
  import maya.mel as mel
  mel.eval('SelectHierarchy')
  print('Joints: %d'%(len(cmds.ls(sl=True))))

edPrintJoints()