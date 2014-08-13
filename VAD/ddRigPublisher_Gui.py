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
# $Date: 2014-08-11$
# $Revision: 1.0$
# $Author: johnz $
#

import maya.cmds as mc


import os
import re
import shutil
import sys
from functools import partial

#sys.path.insert(2, "B:/home/johnz/scripts/jbtools/VAD")


# VAD
from mayatools.VAD import ddConstants


class RigPublisher_GUI(object):
    '''
    Gui to collect user input for publishing character rigs
    '''
    WIN_NAME = 'rigPublishWIN'
    ASSET_LIB = ddConstants.CHAR_ASSETLIBRARY
    IGNORE_LIST = ['.DS_Store', '.mayaSwatches', 'tex']
    RIG_TYPE_LIST = ['BSK (bones, skinned)',
                    'BSG (bones, segmented)',
                    'BCS (bones, controls, skinned)',
                    'BCG (bones, controls, segmented)']

    CHAR_TYPE_LABEL = 'Select character type'
    CHAR_NAME_LABEL = 'Select character'
    RIG_TYPE_LABEL = 'Select rig type'
    DESC_LABEL = 'Sel or type description'

    def __init__(self):
        '''
        initialize instance
        '''
        self._remove_existing()
        self._build_ui()

    @property
    def character_type(self):
        return mc.textFieldGrp(self._tfg_char_type, query=True, text=True)

    @property
    def character(self):
        return mc.textFieldGrp(self._tfg_char, query=True, text=True)

    @property
    def rig_type(self):
        return mc.textFieldGrp(self._tfg_rig_type, query=True, text=True)

    @property
    def version(self):
        return mc.textFieldGrp(self._tfg_version, query=True, text=True)

    def _remove_existing(self):
        '''
        check if an instance of the window already exists, if so delete it
        '''
        if mc.window(self.WIN_NAME, query=True, exists=True):
            mc.deleteUI(self.WIN_NAME)

    def _build_ui(self):
        '''
        build gui window with base controls
        '''
        # build window
        self._window = mc.window(self.WIN_NAME,
                                title='dd Rig Publisher',
                                sizeable=False,
                                resizeToFitChildren=True,
                                widthHeight=(625, 135))

        self._main_flayout = mc.formLayout(numberOfDivisions=100)

        self._tfg_rlayout = mc.rowLayout(numberOfColumns=4,
                                        cw4=[200, 200, 200, 150], height=25,
                                        parent=self._main_flayout)


        self._tfg_char_type = mc.textFieldGrp(editable=False, label='',
                                            cw2=[10, 190], text='',
                                            parent=self._tfg_rlayout)
        self._tfg_char_type_popup = mc.popupMenu(parent=self._tfg_char_type)

        self._tfg_char = mc.textFieldGrp(editable=False, label='',
                                        cw2=[10, 190], text='',
                                        parent=self._tfg_rlayout)
        self._tfg_char_popup = mc.popupMenu(parent=self._tfg_char)

        self._tfg_rig_type = mc.textFieldGrp(editable=False, label='',
                                        cw2=[10, 190], text='',
                                        parent=self._tfg_rlayout)
        self._tfg_rig_type_popup = mc.popupMenu(parent=self._tfg_rig_type)


        self._tfg_version = mc.textFieldGrp(editable=True,
                                        label='Version Number ', cw2=[100,25],
                                        columnAlign2=['right', 'left'], text='1',
                                        parent=self._tfg_rlayout)

        self._publish_btn = mc.button(label='Publish', height=30,
                                        parent=self._main_flayout,
                                        command=self.kick_off_publish)

        mc.formLayout(self._main_flayout, edit=True,
            attachForm=[(self._tfg_rlayout, 'top', 15),
                        (self._tfg_rlayout, 'left', 10),
                        (self._tfg_rlayout, 'right', 10),
                        (self._publish_btn, 'left', 15),
                        (self._publish_btn, 'right', 15),
                        (self._publish_btn, 'bottom', 15)
                        ])

        mc.window(self._window, edit=True, widthHeight=(755, 100))

        self._buildCharTypeTFG()


    def _buildCharTypeTFG(self):
        '''
        build character type text field group menu list
        '''
        # check for and clear out any existing popup menu items
        self._clearOutPopupMenu(self._tfg_char_type)
        self._tfg_char_type_popup = mc.popupMenu(parent=self._tfg_char_type)
        ignore_list = list(set(self.IGNORE_LIST
                                        + ['old characters', 'reference_misc']))

        # collect list of valid character type categories
        data_list = [x for x in (os.listdir(self.ASSET_LIB) or [])
                            if not x in ignore_list and not x.startswith('_')]
        data_list.sort()
        default_label = self.CHAR_TYPE_LABEL

        # setup right click menu items
        mc.menuItem(parent=self._tfg_char_type_popup, label=default_label,
                    command=partial(self._updateCharTypeTFG, default_label))

        for data in data_list:
            mc.menuItem('%sMI' % data, parent=self._tfg_char_type_popup,
                        label=data,
                        command=partial(self._updateCharTypeTFG, data))

        mc.textFieldGrp(self._tfg_char_type, edit=True, text=default_label)

    def _updateCharTypeTFG(self, data, arg=None):
        '''
        update character type text field group menu list
        '''
        print data
        mc.textFieldGrp(self._tfg_char_type, edit=True, text=data)

        # build character list for selected category
        if data != self.CHAR_TYPE_LABEL:
            print data
            self._buildCharTFG(data)

    def _buildCharTFG(self, sel_char_type):
        '''
        build character text field group menu list
        '''
        data_list = None
        ignore_list = self.IGNORE_LIST
        print 'char ignore list:: %s' % str(ignore_list)
        if not sel_char_type == self.CHAR_TYPE_LABEL \
                            or not sel_char_type == '---':
            dir_path = os.path.join(self.ASSET_LIB, sel_char_type)
            data_list = [x for x in (os.listdir(dir_path) or [])
                            if x not in ignore_list]
            data_list.sort()

        # check for and clear out any existing popup menu items
        self._clearOutPopupMenu(self._tfg_char)
        self._tfg_char_popup = mc.popupMenu(parent=self._tfg_char)

        # setup right click menu items
        if data_list:
            # fill with found data items
            default_label = self.CHAR_NAME_LABEL
            mc.menuItem(parent=self._tfg_char_popup, label=default_label,
                        command=partial(self._updateCharTFG,
                                                sel_char_type, default_label))
            print 'setting up data items'
            for data in data_list:
                mc.menuItem('%sMI' % data, parent=self._tfg_char_popup,
                            label=data,
                            command=partial(self._updateCharTFG,
                                                        sel_char_type, data))
            mc.textFieldGrp(self._tfg_char, edit=True, text=default_label)
        else:
            # setup empty menu
            default_label = '---'

            mc.menuItem(parent=self._tfg_char_popup, label=default_label,
                        command=partial(self._updateCharTFG,
                                                sel_char_type, default_label))

            mc.textFieldGrp(self._tfg_char, edit=True, text=default_label)

            # attempt to reupdate field
            self._updateCharTFG(sel_char_type, default_label)

    def _updateCharTFG(self, sel_char_type, data, arg=None):
        '''
        update character text field group menu list
        '''
        mc.textFieldGrp(self._tfg_char, edit=True, text=data)

        # build rig type list for selected category
        if data != self.CHAR_TYPE_LABEL:
            self._buildRigTypeTFG(data)

    def _buildRigTypeTFG(self, sel_char):
        '''
        build rig type text field group menu list
        '''
        data_list = None

        if sel_char != '---':
            data_list = self.RIG_TYPE_LIST

        self._clearOutPopupMenu(self._tfg_rig_type)
        self._tfg_rig_type_popup = mc.popupMenu(parent=self._tfg_rig_type)

        # setup right click menu items
        if data_list:
            # fill with found data items
            default_label = self.RIG_TYPE_LABEL
            mc.menuItem(parent=self._tfg_rig_type_popup, label=default_label,
                        command=partial(self._updateRigTypeTFG,
                                                    sel_char, default_label))
            for data in data_list:
                # get rig type abreviation for use with menu item name
                rtype = data.split(' ')[0]
                mc.menuItem('%sMI' % rtype, parent=self._tfg_rig_type_popup,
                            label=data,
                            command=partial(self._updateRigTypeTFG,
                                                            sel_char, data))
            mc.textFieldGrp(self._tfg_rig_type, edit=True, text=default_label)
        else:
            # setup empty menu
            default_label = '---'
            mc.menuItem(parent=self._tfg_rig_type_popup, label=default_label,
                        command=partial(self._updateRigTypeTFG,
                                                    sel_char, default_label))
            mc.textFieldGrp(self._tfg_rig_type, edit=True, text=default_label)

    def _updateRigTypeTFG(self, sel_char, data, arg=None):
        '''
        update rig type text field group menu list
        '''
        mc.textFieldGrp(self._tfg_rig_type, edit=True, text=data)

    @staticmethod
    def _clearOutPopupMenu(tfg):
        '''
        clear out any existing popup menu items for control
        '''
        kids = mc.textFieldGrp(tfg, query=True, popupMenuArray=True)
        if kids:
            mc.deleteUI(kids)

    def show_win(self):
        '''
        show instance gui
        '''
        mc.showWindow(self._window)

    def validateNamingDetails(self, naming_details):
        '''
        validate correct information was entered
        '''
        print 'Validation Values:: ' + ' - '.join(naming_details.values())

        if self.character_type != self.CHAR_TYPE_LABEL and \
            not self.character in [self.CHAR_NAME_LABEL, '---'] and \
                not self.rig_type in [self.RIG_TYPE_LABEL, '---']:

            if not self.version.isdigit():
                msg = 'Version is not a number.'
                self.validateNamingFailWin(msg)
                return False

            return True
        else:
            self.validateNamingFailWin()
            return False

    @staticmethod
    def validateNamingFailWin(msg=None):
        '''
        display window with validation naming fail to user
        '''
        if not msg:
            msg = "Character and/or rig type fields haven't been entered."

        mc.confirmDialog(
                title='Scene info error',
                message=msg,
                button=['OK'],
                defaultButton='OK')

    def kick_off_publish(self, *args):
        '''
        publish rig to versioned file
        '''
        pass
        # # collect basic details from gui
        # details = collectBasicPubDetails()
        #
        # # valid information provided
        # if details:
        #     # setup path check variables
        #     pub_ver_file = getVersionFile(details)
        #     pub_path = getActualPubPath(details)
        #     pub_rig_path = os.path.join(pub_path, pub_ver_file)
        #     force = False
        #
        #     # determine if publish version already exists
        #     if os.path.isfile('%s.ma' % pub_rig_path):
        #         confirm_action = versionExistsWin(pub_ver_file)
        #
        #         print 'File exists: %s.ma. Proceeding with %s' \
        #                                             % (pub_rig_path, confirm_action)
        #
        #         # determine how to proceed with file
        #         if confirm_action == 'Version Up':
        #             details['archive_version'] = '%s.ma' % pub_rig_path
        #             details = getNextVersion(details)
        #             pub_rig_path = os.path.join(pub_path, getVersionFile(details))
        #         elif confirm_action == 'Replace':
        #             force = True
        #         else:
        #             print 'Canceled publish.'
        #             return
        #
        #     else:
        #         print 'File does not exist, checking if directory structure exists..'
        #         verifyPathDirsExist(details)
        #
        #     # collect user email address for use during publish notifications
        #     user_addy = getUserEmail()
        #     if not user_addy:
        #         return
        #     details['user_address'] = user_addy
        #
        #     for k in details.keys():
        #         print '%s:: %s' % (k, details[k])
        #
        #     details['pub_rig_path'] = '%s.ma' % pub_rig_path
        #     # attempt to publish file
        #     valid_export = exportMayaFiles(pub_rig_path, force)
        #     details['success'] = valid_export
        #
        #     if valid_export:
        #         # archive found older publish
        #         archiveOldVersion(details)
        #
        #     emailUsers(details)
        #     print 'Published %s.ma%s complete.' \
        #                         % (os.path.basename(pub_rig_path),
        #                             " not" if not valid_export else '')

class Callbacks(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        print self.func
        self.args = args
        print self.args
        self.kwargs = kwargs
        print self.kwargs

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)