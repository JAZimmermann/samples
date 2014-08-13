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
# $Date: 2014-07$
# $Revision: 1.0$
# $Author: johnz $
#


import maya.cmds as mc

import os
import re
import shutil
import sys
from functools import partial

# VAD
import ddConstants; reload(ddConstants)
from ddmail import sendMail

# CUR_ASSET_LIB = ddConstants.CHAR_ASSETLIBRARY
CUR_ASSET_LIB = "B:/home/johnz/assets/characters"

# GUI RELATED
# RIGPUB_WIN_NAME = 'rigPublishWIN'
# IGNORE_LIST = ['.DS_Store', '.mayaSwatches', 'tex']
# RIG_TYPE_LIST = ['BSK (bones, skinned)',
#                 'BSG (bones, segmented)',
#                 'BCS (bones, controls, skinned)',
#                 'BCG (bones, controls, segmented)']
# CHAR_TYPE_LABEL = 'Select character type'
# CHAR_NAME_LABEL = 'Select character'
# RIG_TYPE_LABEL = 'Select rig type'
# DESC_LABEL = 'Sel or type description'

# PUBLISH FILE RELATED
# FOLDER_PUB = 'published'
# FOLDER_WORK = 'working'
# FOLDER_ARCH = 'archive'




class RigPublisher(object):
    '''
    '''
    ASSET_LIB = ddConstants.CHAR_ASSETLIBRARY

    # PUBLISH FILE RELATED
    FOLDER_PUB = 'published'
    FOLDER_WORK = 'working'
    FOLDER_ARCH = 'archive'

    def __init__(self):
        '''
        initialize values
        '''
        self._character = None
        self._character_type = None
        self._rig_type = None
        self._version = None
        self._archive_version = None


    @property
    def character(self):
        return self._character

    @property
    def character_type(self):
        return self._character_type

    @property
    def rig_type(self):
        return self._rig_type

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, str_version):
        self._version = str_version

    @property
    def archive_version(self):
        return self._archive_version

    @archive_version.setter
    def archive_version(self, archive_path):
        self._archive_version = archive_path

    @property
    def actual_pub_archive_path(self):
        return os.path.join(self.actual_pub_path, self.FOLDER_ARCH)

    @property
    def file_name(self):
        return "%s_rig_maya_%s" % (self.character, self.rig_type)

    @property
    def version_file_name(self):
        return "%s_%s" % (self.file_name, self.version)

    @property
    def rel_pub_path(self):
        return os.path.join(self.character_type, self.character,
                                        'rig', 'maya', self.FOLDER_PUB)

    @property
    def actual_pub_path(self):
        return os.path.join(self.ASSET_LIB, self.rel_pub_path)

    @property
    def actual_file_pub_path(self):
        return os.path.join(self.actual_pub_path, self.version_file_name)

    @property
    def rel_pub_file_path(self):
        return os.path.join(self.rel_pub_path, self.file_name)

    @staticmethod
    def versionExistsWin(pub_file_name):
        '''
        display window if publish file already exists, how to proceed
        '''
        confirm = mc.confirmDialog(
            title="Warning", messageAlign="center",
            message='File "%s" already exists.' % pub_file_name,
            button=["Version Up", "Replace", "Cancel"],
            defaultButton="Version Up",
            cancelButton="Cancel",
            dismissString="Cancel"
            )

        return confirm

    def verifyPathDirsExist(self):
        '''
        verify that path exists on disk
        '''
        try:
            # collect path elements for verification
            pub_path = self.ASSET_LIB
            pub_dirs = self.rel_pub_path.split(os.sep)
            # also make sure archive directory exists for archiving old versions
            pub_dirs.append(self.FOLDER_ARCH)

            # verify if publish directories exist, if not create
            for pdir in pub_dirs:
                pub_path = os.path.join(pub_path, pdir)
                if not os.path.exists(pub_path):
                    print 'directory %s, does not exist. Creating...' % pub_path
                    os.mkdir(pub_path)
        except Exception, e:
            mc.confirmDialog(
                    title='Path Error',
                    message='Issue creating/validating publish path. %s' % e,
                    button=['OK'],
                    defaultButton='OK')
            raise e

    def getNextVersion(self):
        '''
        determine next version of file
        '''
        found = False
        test_ext = 'ma'
        version = int(self.version.replace('v', ''))

        # locate next version that does not currently exist
        while not found:
            version += 1
            test_pub_file = '%s_v%03d.%s' % (self.file_name, version, test_ext)
            if not os.path.isfile(os.path.join(self.actual_pub_path,
                                                                test_pub_file)):
                found = True
                break

        # update latest values
        self.version = 'v%03d' % version

    def archiveOldVersion(self):
        '''
        move old version from directory to archive directory
        '''
        if self.archive_version:
            try:
                print 'Attempting to archive %s to %s' \
                                    % (self.archive_version,
                                       self.actual_pub_archive_path)
                shutil.move(self.archive_version, self.actual_pub_archive_path)
            except Exception, e:
                mc.confirmDialog(
                        title='Archive Error',
                        message='Issue archiving old publish version. %s' % e,
                        button=['OK'],
                        defaultButton='OK')
                raise e

    def exportMayaFiles(self, force=False):
        '''
        Exports selection to the ".ma" file
        '''
        ascii_path = "%s.ma" % self.actual_file_pub_path
        print 'Exporting "%s"...' % ascii_path
        try:
            exportedFile = mc.file(ascii_path, type="mayaAscii",
                                        exportSelected=True, force=force)
        except Exception, e:
            mc.confirmDialog(
                    title='Publish Error',
                    message='Issue exporting publish rig %s due to %s' \
                                                            % (ascii_path, e),
                    button=['OK'],
                    defaultButton='OK')
            print 'Export cancelled due to %s' % e
            return False

        return True

    def doPublish(self, query):
        '''
        publish rig to versioned file
        '''
        # valid information provided
        if details:
            # setup path check variables
            force = False

            # determine if publish version already exists
            if os.path.isfile('%s.ma' % self.actual_file_pub_path):
                confirm_action = self.versionExistsWin(self.version_file_name)

                print 'File exists: %s.ma. Proceeding with %s' \
                                % (self.actual_file_pub_path, confirm_action)

                # determine how to proceed with file
                if confirm_action == 'Version Up':
                    self.archive_version = '%s.ma' % self.actual_file_pub_path
                    self.getNextVersion()
                elif confirm_action == 'Replace':
                    force = True
                else:
                    print 'Canceled publish.'
                    return

            else:
                print 'File does not exist, checking if directory structure exists..'
                self.verifyPathDirsExist()

            # # collect user email address for use during publish notifications
            # user_addy = getUserEmail()
            # if not user_addy:
            #     return
            # details['user_address'] = user_addy
            #
            # for k in details.keys():
            #     print '%s:: %s' % (k, details[k])
            #
            # details['pub_rig_path'] = '%s.ma' % pub_rig_path
            # attempt to publish file
            valid_export = self.exportMayaFiles(force)
            # details['success'] = valid_export

            if valid_export:
                # archive found older publish
                self.archiveOldVersion()

            # emailUsers(details)
            print 'Published %s.ma%s complete.' \
                                    % (self.version_file_name,
                                    " not" if not valid_export else '')






# class RigPublisher_GUI(object):
#     '''
#     Gui to collect user input for publishing character rigs
#     '''
#     WIN_NAME = 'rigPublishWIN'
#     RIG_TYPE_LIST = ['BSK (bones, skinned)',
#                     'BSG (bones, segmented)',
#                     'BCS (bones, controls, skinned)',
#                     'BCG (bones, controls, segmented)']
#
#     CHAR_TYPE_LABEL = 'Select character type'
#     CHAR_NAME_LABEL = 'Select character'
#     RIG_TYPE_LABEL = 'Select rig type'
#     DESC_LABEL = 'Sel or type description'
#
#     def __init__(self):
#         '''
#         initialize instance
#         '''
#         pass
#
#
#     def _build_ui(self):
#         '''
#         build gui window with base controls
#         '''
#         # build window
#         self._window = mc.window(self.WIN_NAME,
#                                 title='dd Rig Publisher',
#                                 sizeable=False,
#                                 resizeToFitChildren=True,
#                                 widthHeight=(625, 135))
#
#         self._main_flayout = mc.formLayout(numberOfDivisions=100)
#
#         self._tfg_rlayout = mc.rowLayout(numberOfColumns=4,
#                                         cw4=[200, 200, 200, 150], height=25,
#                                         parent=self._main_flayout)
#
#
#         self._tfg_char_type = mc.textFieldGrp(editable=False, label='',
#                                             cw2=[10, 190], text='',
#                                             parent=tfg_rlayout)
#         self._tfg_char = mc.textFieldGrp(editable=False, label='',
#                                         cw2=[10, 190], text='',
#                                         parent=tfg_rlayout)
#         self._tfg_rig_type = mc.textFieldGrp(editable=False, label='',
#                                         cw2=[10, 190], text='',
#                                         parent=tfg_rlayout)
#
#
#         self._tfg_version = mc.textFieldGrp(editable=True,
#                                         label='Version Number ', cw2=[100,25],
#                                         columnAlign2=['right', 'left'], text='1',
#                                         parent=tfg_rlayout)
#
#         self._publish_btn = mc.button(label='Publish', height=30,
#                                         parent=self._main_flayout,
#                                         command=self.kick_off_publish)
#
#         # build popup menus
#         buildMultiPopups([tfg_char_type, tfg_char, tfg_rig_type])
#
#         mc.formLayout(self._main_flayout, edit=True,
#             attachForm=[(tfg_rlayout, 'top', 15),
#                         (tfg_rlayout, 'left', 10),
#                         (tfg_rlayout, 'right', 10),
#                         (publish_btn, 'left', 15),
#                         (publish_btn, 'right', 15),
#                         (publish_btn, 'bottom', 15)
#                         ])
#
#         mc.window(self._window, edit=True, widthHeight=(755, 100))
#
#         buildCharTypeTFG()
#
#     @staticmethod
#     def clearOutPopupMenu(tfg):
#         '''
#         clear out any existing popup menu items for control
#         '''
#         kids = mc.textFieldGrp(tfg, query=True, popupMenuArray=True)
#         if kids:
#             mc.deleteUI(kids)
#
#
#     def buildMultiPopups(ctl_list):
#         '''
#         build popup menus for text field group controls
#         '''
#         for ctl in ctl_list:
#             mc.popupMenu('%s_menu' % ctl, parent=ctl)
#
#     def show_win(self):
#         '''
#         show instance gui
#         '''
#         mc.showWindow(self._window)
#
#     def kick_off_publish(self, *args):
#         '''
#         publish rig to versioned file
#         '''
#         # collect basic details from gui
#         details = collectBasicPubDetails()
#
#         # valid information provided
#         if details:
#             # setup path check variables
#             pub_ver_file = getVersionFile(details)
#             pub_path = getActualPubPath(details)
#             pub_rig_path = os.path.join(pub_path, pub_ver_file)
#             force = False
#
#             # determine if publish version already exists
#             if os.path.isfile('%s.ma' % pub_rig_path):
#                 confirm_action = versionExistsWin(pub_ver_file)
#
#                 print 'File exists: %s.ma. Proceeding with %s' \
#                                                     % (pub_rig_path, confirm_action)
#
#                 # determine how to proceed with file
#                 if confirm_action == 'Version Up':
#                     details['archive_version'] = '%s.ma' % pub_rig_path
#                     details = getNextVersion(details)
#                     pub_rig_path = os.path.join(pub_path, getVersionFile(details))
#                 elif confirm_action == 'Replace':
#                     force = True
#                 else:
#                     print 'Canceled publish.'
#                     return
#
#             else:
#                 print 'File does not exist, checking if directory structure exists..'
#                 verifyPathDirsExist(details)
#
#             # collect user email address for use during publish notifications
#             user_addy = getUserEmail()
#             if not user_addy:
#                 return
#             details['user_address'] = user_addy
#
#             for k in details.keys():
#                 print '%s:: %s' % (k, details[k])
#
#             details['pub_rig_path'] = '%s.ma' % pub_rig_path
#             # attempt to publish file
#             valid_export = exportMayaFiles(pub_rig_path, force)
#             details['success'] = valid_export
#
#             if valid_export:
#                 # archive found older publish
#                 archiveOldVersion(details)
#
#             emailUsers(details)
#             print 'Published %s.ma%s complete.' \
#                                 % (os.path.basename(pub_rig_path),
#                                     " not" if not valid_export else '')
#
#
# def getNamingDetails():
#     '''
#     collect details from gui
#     '''
#     char_type = mc.textFieldGrp('tfg_char_type', q=True, tx=True)
#     character = mc.textFieldGrp('tfg_char', q=True, tx=True)
#     rig_type = mc.textFieldGrp('tfg_rig_type', q=True, tx=True)
#     rig_version = mc.textFieldGrp('tfg_version', q=True, tx=True)
#
#     if re.search('\(', rig_type):
#         rig_type = rig_type.split(' ')[0]
#
#     naming_data = {
#                 'char_type': char_type,
#                 'character': character,
#                 'rig_type': rig_type,
#                 'version': rig_version
#                 }
#
#     return naming_data
#
#
# def collectBasicPubDetails():
#     '''
#     collect basic publish details
#     '''
#     details = getNamingDetails()
#
#     if validateNamingDetails(details):
#         # reformat version number
#         details['version'] = 'v%03d' % int(details['version'])
#         # add relative pub directory details
#         details['rel_pub_dir'] = getRelPubPath(details)
#         details['file_name'] = getFileName(details)
#         details['full_file_name'] = getVersionFile(details)
#
#         return details
#
#     return False
#
#
#
# def getRelPubPath(details):
#     '''
#     combine data elements for relative path
#     '''
#     return os.path.join(details['char_type'], details['character'],
#                             'rig', 'maya', FOLDER_PUB)
#
#
# def getActualPubPath(details):
#     '''
#     combine relative path with asset library path
#     '''
#     return os.path.join(CUR_ASSET_LIB, getRelPubPath(details))
#
#
# def getRelPubFilePath(details):
#     '''
#     combine relative path with file name prefix
#     '''
#     return os.path.join(details['rel_pub_path'], details['file_name'])
#
#
# def getFileName(details):
#     '''
#     combine data elements for file name prefix, no version number
#     '''
#     return '%s_rig_maya_%s' % (details['character'], details['rig_type'])
#
# def getVersionFile(details):
#     '''
#     combine file name with version value
#     '''
#     return '%s_%s' % (details['file_name'], details['version'])
#
#
# def getUserEmail(not_email=False):
#     '''
#     prompt user for email address for later use in publish notifications
#     '''
#     print "Attempting to collect user's email alias for publish notification.."
#     user_addy = ''
#     msg = 'Enter Email Address:'
#
#     if not_email:
#         msg = 'Please Re-enter an Email Address:'
#
#     result = mc.promptDialog(
#                     title='Get User',
#                     message=msg,
#                     button=['OK', 'Cancel'],
#                     defaultButton='OK',
#                     cancelButton='Cancel',
#                     dismissString='Cancel')
#
#     if result == 'OK':
#         user_addy = mc.promptDialog(query=True, text=True)
#         if not re.match('\w+@\w+.\w+', user_addy):
#             user_addy = getUserEmail(True)
#
#     return user_addy
#
#
# def versionExistsWin(pub_file_name):
#     '''
#     display window if publish file already exists, how to proceed
#     '''
#     confirm = mc.confirmDialog(
#         title="Warning", messageAlign="center",
#         message='File "%s" already exists.' % pub_file_name,
#         button=["Version Up", "Replace", "Cancel"],
#         defaultButton="Version Up",
#         cancelButton="Cancel",
#         dismissString="Cancel"
#         )
#
#     return confirm
#
#
# def verifyPathDirsExist(details):
#     '''
#     verify that path exists on disk
#     '''
#     try:
#         # collect path elements for verification
#         pub_path = CUR_ASSET_LIB
#         pub_dirs = details['rel_pub_dir'].split(os.sep)
#         # also make sure archive directory exists for archiving old versions
#         pub_dirs.append(FOLDER_ARCH)
#
#         # verify if publish directories exist, if not create
#         for pdir in pub_dirs:
#             pub_path = os.path.join(pub_path, pdir)
#             if not os.path.exists(pub_path):
#                 print 'directory %s, does not exist. Creating...' % pub_path
#                 os.mkdir(pub_path)
#     except Exception, e:
#         mc.confirmDialog(
#                 title='Path Error',
#                 message='Issue creating/validating publish path. %s' % e,
#                 button=['OK'],
#                 defaultButton='OK')
#         raise e
#
# def getNextVersion(details):
#     '''
#     determine next version of file
#     '''
#     found = False
#     test_ext = 'ma'
#     version = int(details['version'].replace('v', ''))
#     test_pub_path = getActualPubPath(details)
#
#     # locate next version that does not currently exist
#     while not found:
#         version += 1
#         test_pub_file = '%s_%s.%s' % (details['file_name'], version, test_ext)
#         if not os.path.isfile(os.path.join(test_pub_path, test_pub_file)):
#             found = True
#             break
#
#     # update latest values
#     details['version'] = 'v%03d' % version
#     details['full_file_name'] = getVersionFile(details)
#
#     return details
#
# def emailUsers(details):
#     '''
#     send out email notification of publish results
#     '''
#     print 'Building publish notification email...'
#     success_text = 'Not Published' if not details['success'] else 'Publish'
#     subject = '[TRUCE] VAD RIG %s: %s.ma' \
#                                 % (success_text, getVersionFile(details))
#     send_to = []
#     text = ''
#     user_name = details['user_address'].split('@')[0]
#
#     send_to.append(details['user_address'])
#
#     text_header = []
#     text_header.append('Hi everyone,\n')
#     text_header.append('%s has published out a new version of %s rig.  ' \
#                         % (user_name, details['character']) \
#                         + 'It is available here:\n')
#     text_header.append('%s\n' % details['pub_rig_path'])
#     text_header.append('Please let me know if you have any questions!\n')
#     text_header.append('Thanks,')
#     text_header.append('Sam x183')
#
#     text = '\n'.join(text_header) + text
#
#     print 'Sending email:::'
#     log_text = []
#     log_text.append('From: %s' % 'johnz@d2.com')
#     log_text.append('To: %s' % ', '.join(send_to))
#     log_text.append('Subject: %s' % subject)
#     log_text.append('%s' % text)
#     print '\n'.join(log_text)
#
#     sendMail(send_from = 'johnz@d2.com',
#              send_to = send_to,
#              subject = subject,
#              text    = text)
#
#
# def archiveOldVersion(details):
#     '''
#     move old version from directory to archive directory
#     '''
#     if 'archive_version' in details:
#         arch_dir = os.path.join(getActualPubPath(details), FOLDER_ARCH)
#         try:
#             print 'Attempting to archive %s to %s' \
#                                 % (details['archive_version'], arch_dir)
#             shutil.move(details['archive_version'], arch_dir)
#         except Exception, e:
#             mc.confirmDialog(
#                     title='Archive Error',
#                     message='Issue archiving old publish version. %s' % e,
#                     button=['OK'],
#                     defaultButton='OK')
#             raise e
#
#
# def exportMayaFiles(pub_rig_path, force=False):
#     '''
#     Exports selection to the ".ma" file
#     '''
#     ascii_path = "%s.ma" % pub_rig_path
#     print 'Exporting "%s"...' % ascii_path
#     try:
#         exportedFile = mc.file(ascii_path, type="mayaAscii",
#                                     exportSelected=True, force=force)
#     except Exception, e:
#         mc.confirmDialog(
#                 title='Publish Error',
#                 message='Issue exporting publish rig %s due to %s' \
#                                                         % (ascii_path, e),
#                 button=['OK'],
#                 defaultButton='OK')
#         print 'Export cancelled due to %s' % e
#         return False
#
#     return True
#
#
# def doPublish(self, query):
#     '''
#     publish rig to versioned file
#     '''
#     # collect basic details from gui
#     details = collectBasicPubDetails()
#
#     # valid information provided
#     if details:
#         # setup path check variables
#         pub_ver_file = getVersionFile(details)
#         pub_path = getActualPubPath(details)
#         pub_rig_path = os.path.join(pub_path, pub_ver_file)
#         force = False
#
#         # determine if publish version already exists
#         if os.path.isfile('%s.ma' % pub_rig_path):
#             confirm_action = versionExistsWin(pub_ver_file)
#
#             print 'File exists: %s.ma. Proceeding with %s' \
#                                                 % (pub_rig_path, confirm_action)
#
#             # determine how to proceed with file
#             if confirm_action == 'Version Up':
#                 details['archive_version'] = '%s.ma' % pub_rig_path
#                 details = getNextVersion(details)
#                 pub_rig_path = os.path.join(pub_path, getVersionFile(details))
#             elif confirm_action == 'Replace':
#                 force = True
#             else:
#                 print 'Canceled publish.'
#                 return
#
#         else:
#             print 'File does not exist, checking if directory structure exists..'
#             verifyPathDirsExist(details)
#
#         # collect user email address for use during publish notifications
#         user_addy = getUserEmail()
#         if not user_addy:
#             return
#         details['user_address'] = user_addy
#
#         for k in details.keys():
#             print '%s:: %s' % (k, details[k])
#
#         details['pub_rig_path'] = '%s.ma' % pub_rig_path
#         # attempt to publish file
#         valid_export = exportMayaFiles(pub_rig_path, force)
#         details['success'] = valid_export
#
#         if valid_export:
#             # archive found older publish
#             archiveOldVersion(details)
#
#         emailUsers(details)
#         print 'Published %s.ma%s complete.' \
#                             % (os.path.basename(pub_rig_path),
#                                 " not" if not valid_export else '')
#
#
# def buildCharTypeTFG():
#     '''
#     build character type text field group menu list
#     '''
#     tfg = 'tfg_char_type'
#     # check for and clear out any existing popup menu items
#     clearOutPopupMenu(tfg)
#     menu = mc.popupMenu('%s_menu' % tfg, parent=tfg)
#     ignore_list = list(set(IGNORE_LIST + ['old characters', 'reference_misc']))
#
#     # collect list of valid character type categories
#     data_list = [x for x in (os.listdir(CUR_ASSET_LIB) or [])
#                         if not x in ignore_list and not x.startswith('_')]
#     data_list.sort()
#     default_label = CHAR_TYPE_LABEL
#
#     # setup right click menu items
#     mc.menuItem(parent=menu, label=default_label,
#                 command=partial(updateCharTypeTFG, default_label))
#
#     for data in data_list:
#         mc.menuItem('%sMI' % data, parent=menu, label=data,
#                     command=partial(updateCharTypeTFG, data))
#
#     mc.textFieldGrp(tfg, edit=True, text=default_label)
#
#
# def updateCharTypeTFG(data, arg=None):
#     '''
#     update character type text field group menu list
#     '''
#     default_label = CHAR_TYPE_LABEL
#     mc.textFieldGrp('tfg_char_type', edit=True, text=data)
#
#     # build character list for selected category
#     if data != default_label:
#         buildCharTFG(data)
#
#
# def buildCharTFG(sel_char_type):
#     '''
#     build character text field group menu list
#     '''
#     tfg = 'tfg_char'
#     data_list = None
#     ignore_list = IGNORE_LIST
#     print 'char ignore list:: %s' % str(ignore_list)
#     if not sel_char_type == CHAR_TYPE_LABEL or not sel_char_type == '---':
#         dir_path = os.path.join(CUR_ASSET_LIB, sel_char_type)
#         data_list = [x for x in (os.listdir(dir_path) or [])
#                         if x not in ignore_list]
#         data_list.sort()
#
#     # check for and clear out any existing popup menu items
#     clearOutPopupMenu(tfg)
#     menu = mc.popupMenu('%s_menu' % tfg, parent=tfg)
#
#     # setup right click menu items
#     if data_list:
#         # fill with found data items
#         default_label = CHAR_NAME_LABEL
#         mc.menuItem(parent=menu, label=default_label,
#                     command=partial(updateCharTFG, sel_char_type, default_label))
#         print 'setting up data items'
#         for data in data_list:
#             mc.menuItem('%sMI' % data, parent=menu, label=data,
#                         command=partial(updateCharTFG, sel_char_type, data))
#         mc.textFieldGrp(tfg, edit=True, text=default_label)
#     else:
#         # setup empty menu
#         default_label = '---'
#
#         mc.menuItem(parent=menu, label=default_label,
#                     command=partial(updateCharTFG, sel_char_type, default_label))
#
#         mc.textFieldGrp(tfg, edit=True, text=default_label)
#
#         # attempt to reupdate field
#         updateCharTFG(sel_char_type, default_label)
#
#
# def updateCharTFG(sel_char_type, data, arg=None):
#     '''
#     update character text field group menu list
#     '''
#     mc.textFieldGrp('tfg_char', edit=True, text=data)
#
#     # build rig type list for selected category
#     if data != CHAR_TYPE_LABEL:
#         buildRigTypeTFG(data)
#
#
# def buildRigTypeTFG(sel_char):
#     '''
#     build rig type text field group menu list
#     '''
#     tfg = 'tfg_rig_type'
#     data_list = None
#
#     if sel_char != '---':
#         data_list = RIG_TYPE_LIST
#
#     clearOutPopupMenu(tfg)
#     menu = mc.popupMenu('%s_menu' % tfg, parent=tfg)
#
#     # setup right click menu items
#     if data_list:
#         # fill with found data items
#         default_label = RIG_TYPE_LABEL
#         mc.menuItem(parent=menu, label=default_label,
#                     command=partial(updateRigTypeTFG, sel_char, default_label))
#         for data in data_list:
#             # get rig type abreviation for use with menu item name
#             rtype = data.split(' ')[0]
#             mc.menuItem('%sMI' % rtype, parent=menu, label=data,
#                         command=partial(updateRigTypeTFG, sel_char, data))
#         mc.textFieldGrp(tfg, edit=True, text=default_label)
#     else:
#         # setup empty menu
#         default_label = '---'
#         mc.menuItem(parent=menu, label=default_label,
#                     command=partial(updateRigTypeTFG, sel_char, default_label))
#         mc.textFieldGrp(tfg, edit=True, text=default_label)
#
#
# def updateRigTypeTFG(sel_char, data, arg=None):
#     '''
#     update rig type text field group menu list
#     '''
#     mc.textFieldGrp('tfg_rig_type', edit=True, text=data)
#
#
# def clearOutPopupMenu(tfg):
#     '''
#     clear out any existing popup menu items for control
#     '''
#     kids = mc.textFieldGrp(tfg, query=True, popupMenuArray=True)
#     if kids:
#         mc.deleteUI(kids)
#
#
# def buildMultiPopups(ctl_list):
#     '''
#     build popup menus for text field group controls
#     '''
#     for ctl in ctl_list:
#         mc.popupMenu('%s_menu' % ctl, parent=ctl)
#
#
# def winExistsDelete():
#     '''
#     check if window already exists, if so delete
#     '''
#     if mc.window(RIGPUB_WIN_NAME, query=True, exists=True):
#         mc.deleteUI(RIGPUB_WIN_NAME)
#
#
# def buildGui():
#     '''
#     build gui window with base controls
#     '''
#     rig_window_name = RIGPUB_WIN_NAME
#
#     # build window
#     window = mc.window(rig_window_name,
#                         title='Rig Publisher',
#                         sizeable=False,
#                         resizeToFitChildren=True,
#                         widthHeight=(625, 135))
#
#     main_flayout = mc.formLayout('main_flayout', numberOfDivisions=100)
#     # tfg_rlayout = mc.rowLayout('tfg_rlayout', numberOfColumns=3,
#     #                             cw3=[200, 200, 200], height=25,
#     #                             parent=main_flayout)
#     tfg_rlayout = mc.rowLayout('tfg_rlayout', numberOfColumns=4,
#                                 cw4=[200, 200, 200, 150], height=25,
#                                 parent=main_flayout)
#
#
#     tfg_char_type = mc.textFieldGrp('tfg_char_type', editable=False, label='',
#                                         cw2=[10, 190], text='',
#                                         parent=tfg_rlayout)
#     tfg_char = mc.textFieldGrp('tfg_char', editable=False, label='',
#                                     cw2=[10, 190], text='',
#                                     parent=tfg_rlayout)
#     tfg_rig_type = mc.textFieldGrp('tfg_rig_type', editable=False, label='',
#                                     cw2=[10, 190], text='',
#                                     parent=tfg_rlayout)
#
#     # desc_rlayout = mc.rowLayout('desc_rlayout', numberOfColumns=4,
#     #                             cw4=[240,110,115,125], height=25,
#     #                             parent=main_flayout)
#     # tfg_desc = mc.textFieldGrp('tfg_desc', editable=True, label='Descriptor ',
#     #                             cw2=[65,185], columnAlign2=['left', 'left'],
#     #                             text='', parent=desc_rlayout)
#
#     # tfg_version = mc.textFieldGrp('tfg_version', editable=True,
#     #                                 label='Version Number ', cw2=[100,25],
#     #                                 columnAlign2=['right', 'left'], text='1',
#     #                                 parent=desc_rlayout)
#     tfg_version = mc.textFieldGrp('tfg_version', editable=True,
#                                     label='Version Number ', cw2=[100,25],
#                                     columnAlign2=['right', 'left'], text='1',
#                                     parent=tfg_rlayout)
#
#     publish_btn = mc.button('publish_btn', label='Publish', height=30,
#                             parent=main_flayout, c=partial(doPublish, False))
#
#     # build popup menus
#     # buildMultiPopups([tfg_char_type, tfg_char, tfg_rig_type, tfg_desc])
#     buildMultiPopups([tfg_char_type, tfg_char, tfg_rig_type])
#
#     # mc.formLayout(main_flayout, edit=True,
#     #     attachForm=[(tfg_rlayout, 'top', 15), (tfg_rlayout, 'left', 10),
#     #                 (tfg_rlayout, 'right', 10), (desc_rlayout, 'left', 15),
#     #                 (desc_rlayout, 'right', 15), (publish_btn, 'left', 15),
#     #                 (publish_btn, 'right', 15), (publish_btn, 'bottom', 15)
#     #                 ],
#     #     attachControl=[(desc_rlayout, 'top', 15, tfg_rlayout)])
#     mc.formLayout(main_flayout, edit=True,
#         attachForm=[(tfg_rlayout, 'top', 15), (tfg_rlayout, 'left', 10),
#                     (tfg_rlayout, 'right', 10), (publish_btn, 'left', 15),
#                     (publish_btn, 'right', 15), (publish_btn, 'bottom', 15)
#                     ])
#
#     # mc.window(window, edit=True, widthHeight=(635, 140))
#     mc.window(window, edit=True, widthHeight=(755, 100))
#
#     buildCharTypeTFG()
#
#     return window
#
#
# def do():
#     '''
#     main run function for rig publish window
#     '''
#     # check window
#     winExistsDelete()
#
#     # build and show
#     mc.showWindow(buildGui())
