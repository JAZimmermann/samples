import maya.cmds as cmds


def edVtxChanges(transforms,reset,sel,debugOn):
  """---------------------------------------------------------------------------------------------------
  Function to find print and select geometry which contains shape nodes with vertex transforms in
  1. transforms = object transform nodes
  2. reset      = reset positions to zero if non zero
  3. sel        = select geo that is changed
  4. debugOn    = print debug 
  
  - Highlights geo which has any secondary vertex tranforms stored that could potentially
      come from world space transforms or any non legal transform for JB referenced assets
  - Legal assets must have frozen transforms so we can trap the behaviour of non legal transforms 
      in layout
  - If your layout scene finds non legal assets, they should be re-imported
  ---------------------------------------------------------------------------------------------------"""
  shpsChanged=[]
  #print(transforms)
  #cmds.select(transforms)
  #pnts = cmds.getAttr(shape+'.pnts')
  for trans in transforms:
    # check the nodes passed are transforms
    if cmds.objectType(trans, isType='transform'):   
      # get child shape nodes if any
      shapes=cmds.listRelatives(trans,ad=True)
      shape=''
      if shapes != None:
        if len(shapes) > 0:
          shape=shapes[0]

      # if no shape go to next trans
      else:
        shape=None
        continue
        
      # check for shapes only
      if cmds.objectType(shape, isType='mesh'):
        shpChanged=False # switch for if any verts altered
        for x in range(0,cmds.polyEvaluate(shape,v=True)):
          ptx=cmds.getAttr(shape+'.pnts[%d'%x+'].pntx')
          pty=cmds.getAttr(shape+'.pnts[%d'%x+'].pnty')
          ptz=cmds.getAttr(shape+'.pnts[%d'%x+'].pntz')
          
          # if reset is on, reset .pts values to 0
          if reset:
            cmds.setAttr(shape+'.pnts[%d'%x+'].pntx', 0)
            cmds.setAttr(shape+'.pnts[%d'%x+'].pnty', 0)
            cmds.setAttr(shape+'.pnts[%d'%x+'].pntz', 0)
          if debugOn:
            print('PT: %d %d %d'%(ptx,pty,ptz))
            
          # catch non zeros and flag shape if different
          if ptx != 0 or pty != 0 or ptz != 0:
            shpChanged=True
            
        # add to list for return
        if shpChanged:
          shpsChanged.append(shape)
          if debugOn:
            print('INVALID: '+shape)
        elif cmds.objectType(trans, isType='mesh'):
          if debugOn:
            print('VALID: '+shape)
            
      # if not shape then go to next trans
      else:
        continue
  if debugOn:
    print(shpsChanged)
  if(len(shpsChanged) > 0) and sel:
    cmds.select(shpsChanged,r=True)
  return shpsChanged


  
edVtxChanges(cmds.ls(type='transform'),False,True,False)