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
# $Date: 2014-08-05$
# $Revision: 1.0$
# $Author: johnz $
#


import maya.cmds as mc

import os
import sys
sys.path.insert(2, "B:/home/johnz/scripts/jbtools/VAD")
import ddScreenBoardGrab

# from mayatools.VAD import ddScreenBoardGrab


class LayoutScreenBoardGrab_GUI(object):
    '''
    Gui to collect user input for creating layout screen boards
    '''
    WIN_NAME = 'layoutScreenGrabWin'
    def __init__(self):
        '''
        initialize instance variables
        '''
        self._remove_existing()
        self._build_ui()

    def _build_ui(self):
        self._window = mc.window(
                                self.WIN_NAME,
                                title='dd Layout Screen Board Grab',
                                sizeable=False,
                                resizeToFitChildren=True,
                                widthHeight=(625, 135))

        self._main_flayout = mc.formLayout(numberOfDivisions=100)

        self._path_field = mc.textFieldButtonGrp(editable=True,
                                    label='Save Path (*OPTIONAL*)',
                                    columnAlign3=['left', 'left', 'right'],
                                    columnWidth3=[125, 450, 15],
                                    parent=self._main_flayout,
                                    buttonLabel='...',
                                    buttonCommand=self._browser,
                                    annotation="Specify a specific path to "
                                        + "save image boards to. **NOTE** "
                                        + "This is optional as the script "
                                        + "will normally save to the publish "
                                        + "folder of the scene if not "
                                        + "overriden by another path.")

        self._rlayout = mc.rowLayout(numberOfColumns=2,
                                cw2=[300, 300], height=25,
                                parent=self._main_flayout)

        self._ex_prefix_field = mc.textFieldGrp(editable=True,
                                        label="Exclude Prefixes: ",
                                        cw2=[100, 190], text='',
                                        parent=self._rlayout,
                                        annotation="Provided a comma separated "
                                           + "list of words / phrases to be "
                                           + "used as prefixes to exclude "
                                           + "certain bookmarks from creating "
                                           + "image boards.  Underscores ('_') "
                                           + "do not need to be provided, "
                                           + "unless starts or is apart of "
                                           + "the phrase.")
        self._ex_postfix_field = mc.textFieldGrp(editable=True,
                                        label="Exclude Postfixes: ",
                                        cw2=[100, 190], text='',
                                        parent=self._rlayout,
                                        annotation="Provided a comma separated "
                                           + "list of words / phrases to be "
                                           + "used as postfixes to exclude "
                                           + "certain bookmarks from creating "
                                           + "image boards.  Underscores ('_') "
                                           + "do not need to be provided, "
                                           + "unless ends or is apart of "
                                           + "the phrase.")

        self._use_panel_chbx = mc.checkBox(label="Use Current Panel for Size",
                                           value=True,
                                           parent=self._main_flayout,
                                           annotation="Left checked, the image "
                                              + "boards will use the current "
                                              + "panel size for the resolution."
                                              + " Unchecked, will use the "
                                              + "default HD size coded into "
                                              + "the tool.")

        self._ok_button = mc.button(label='OK', height=30,
                                    parent=self._main_flayout,
                                    command=self.kick_off,
                                    annotation="Make sure that a camera "
                                               + "with bookmarks is selected.")

        mc.formLayout(self._main_flayout, edit=True,
                attachForm=[
                            (self._path_field, 'top', 10),
                            (self._path_field, 'left', 10),
                            (self._path_field, 'right', 10),
                            (self._rlayout, 'left', 10),
                            (self._rlayout, 'right', 5),
                            (self._use_panel_chbx, 'right', 10),
                            (self._ok_button, 'left', 10),
                            (self._ok_button, 'bottom', 10),
                            (self._ok_button, 'right', 10)
                    ],
                attachControl=[
                            (self._path_field, "bottom", 5, self._rlayout),
                            (self._rlayout, "bottom", 5, self._use_panel_chbx),
                            (self._use_panel_chbx, "bottom", 5, self._ok_button)
                    ]
                )

    @property
    def user_path(self):
        '''
        get the user supplied path
        '''
        return mc.textFieldButtonGrp(self._path_field, query=True, text=True)

    @property
    def exclude_prefixes(self):
        '''
        get list of user supplied prefixes to exclude
        '''
        ex_prefixes = mc.textFieldGrp(self._ex_prefix_field,
                                            query=True, text=True)
        return [epref.strip() for epref in ex_prefixes.split(',') \
                                                        if ex_prefixes] or []

    @property
    def exclude_postfixes(self):
        '''
        get list of user supplied postfixes to exclude
        '''
        ex_postfixes = mc.textFieldGrp(self._ex_postfix_field,
                                            query=True, text=True)
        return [epost.strip() for epost in ex_postfixes.split(',') \
                                                        if ex_postfixes] or []

    @property
    def use_panel(self):
        '''
        get state to determine if the current camera panel for size
        '''
        return mc.checkBox(self._use_panel_chbx, query=True, value=True)

    def show_win(self):
        '''
        show instance gui
        '''
        mc.showWindow(self._window)

    def kick_off(self, *args):
        '''
        kick off the processing of layout boards with the specified settings
        :param args:
        '''
        if not self._check_prereqs():
            return

        print 'Utilising the current values..'
        print '\tUser Path:: %s' % self.user_path
        print '\tExclude Prefixes:: %s' % str(self.exclude_prefixes)
        print '\tExclude Postfixes:: %s' % str(self.exclude_postfixes)
        print '\tUse Current Panel:: %s' % str(self.use_panel)

        ddScreenBoardGrab.do_layout_boards(
                                    use_path=self.user_path,
                                    exclude_prefixes=self.exclude_prefixes,
                                    exclude_postfixes=self.exclude_postfixes,
                                    use_panel=self.use_panel)

        confirm = mc.confirmDialog(
                                    title="Complete", messageAlign="center",
                                    message='Boards have been created.',
                                    button=["OK", "Cancel"],
                                    defaultButton="OK",
                                    cancelButton="Cancel",
                                    dismissString="Cancel"
                                    )

        if confirm == "OK":
            self._remove_existing()

    def _check_prereqs(self):
        '''
        check for correct selections to proceed
        '''
        cur_sel = mc.ls(sl=True)
        msg = None
        if len(cur_sel) < 1:
            msg = "Incorrect selection. Need to select at " \
                + "least one camera. Preferably a camera and " \
                + "layout set group node, ie. env_0080_PCR...GRP, " \
                + "as added help for proper naming / saving."

        else:
            cam_shape = mc.listRelatives(cur_sel[0], type='camera')[0] or ''
            if not cam_shape:
                msg = "%s is not a camera" % cur_sel[0]

        if msg:
            mc.confirmDialog(title="Error", messageAlign="center",
                             message=msg, button=["OK"], defaultButton="OK")
            raise Exception(msg)

        return True

    def _browser(self, *args):
        '''
        open a file browser, collect directory path provided by user and enter
            it into the text field
        :param args:
        :return:
        '''
        folder = mc.fileDialog2(fileMode=3,
                                caption="Choose Directory to save boards to..",
                                startingDirectory=os.getenv('SHOW_ROOT'))\
                                or None
        if folder:
            mc.textFieldButtonGrp(self._path_field, edit=True, text=folder[0])

    def _remove_existing(self):
        '''
        check if an instance of the window already exists, if so delete it
        '''
        if mc.window(self.WIN_NAME, query=True, exists=True):
            mc.deleteUI(self.WIN_NAME)