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

apath = "B:/home/johnz/scripts/jbtools"
if apath not in sys.path:
    sys.path.insert(2, apath)

# VAD
from cw_scripts import ddConstants
# from mayatools.VAD import ddConstants


class dPublisherBase(object):
    '''
    base publishing library
    '''
    # PUBLISH FILE RELATED
    FOLDER_PUB = 'published'
    FOLDER_WORK = 'working'
    FOLDER_ARCH = 'archive'

    def __init__(self, details, lib_category='environments'):
        '''
        initialize instance variables
        '''
        self._version = details.get('version')
        self._archive_version = None
        self._asset_library = ddConstants.ASSET_DIRECTORIES[lib_category]
        self._lib_category = lib_category
        self._pub_ext = 'ma'
        self._force_save = False

        self.obj = 'tester'

    @property
    def version(self):
        '''
        get expected publish version as string, ie. "v001"
        '''
        return self._version

    @version.setter
    def version(self, str_version):
        '''
        set expected publish version from provided string value

        :type   str_version: C{str}
        :param  str_version: new expected publish version, ie. "v001"
        '''
        self._version = str_version

    @property
    def pub_ext(self):
        '''
        get expected publish file extension
        '''
        return self._pub_ext

    @pub_ext.setter
    def pub_ext(self, new_ext):
        '''
        set expected publish file extension, no "."

        :type   new_ext: C{str}
        :param  new_ext: new file extension
        :return:
        '''
        self._pub_ext = new_ext

    @property
    def force_save(self):
        '''
        get state for forcing saves
        '''
        return self._force_save

    @force_save.setter
    def force_save(self, force_state):
        '''
        set expected force state for saving

        :type   force_state: C{bool}
        :param  force_state: new force state for saving
        '''
        self._force_save = force_state

    @property
    def asset_library(self):
        '''
        get current asset library path for use
        '''
        return self._asset_library

    @asset_library.setter
    def asset_library(self, asset_lib):
        '''
        set current asset library path to new provided path

        :type   asset_lib: C{str}
        :param  asset_lib: new provided library path
        '''
        self._asset_library = asset_lib

    @property
    def archive_version(self):
        '''
        get full path to file version expected to be archived
        '''
        return self._archive_version

    @archive_version.setter
    def archive_version(self, archive_path):
        '''
        set full file path of file version expected to be archived

        :type   archive_path: C{str}
        :param  archive_path: full path to file version
        '''
        self._archive_version = archive_path

    @property
    def actual_pub_archive_path(self):
        return os.path.join(self.actual_pub_path, self.FOLDER_ARCH)

    @property
    def file_name(self):
        '''
        get the expected publish file name prefix
        '''
        return self.obj

    @property
    def version_file_name(self):
        '''
        get the concatenation of the expected publish file name prefix
            and publish version string
        '''
        return "%s_%s" % (self.file_name, self.version)

    @property
    def rel_pub_path(self):
        '''
        get full relative directory path for publish by combining path
            elements together natively for operating system.
            *Note*- Relative path is the section of path between the
            asset library and the actual file
        '''
        return os.path.join(self._lib_category, self.obj, self.FOLDER_PUB)

    @property
    def actual_pub_path(self):
        '''
        get the full publish directory path by combining asset library path
            and the relative publish path together natively for os
        '''
        return os.path.join(self.asset_library, self.rel_pub_path)

    @property
    def actual_file_pub_path(self):
        '''
        get the full publish file path, excluding extension, by combining
            full publish directory path with version file name
            together natively for os
        '''
        return os.path.join(self.actual_pub_path, self.version_file_name)

    @property
    def rel_pub_file_path(self):
        '''
        get full relative file path for publish by combining relative path
            and file name prefix together natively for os.
        '''
        return os.path.join(self.rel_pub_path, self.file_name)

    @staticmethod
    def _version_exists_win(pub_file_name):
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

    def _verify_path_dirs_exist(self):
        '''
        verify that path exists on disk
        '''
        try:
            # collect path elements for verification
            pub_path = self.asset_library
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

    def get_next_version(self):
        '''
        determine next version of file
        '''
        found = False
        version = int(self.version.replace('v', ''))

        # locate next version that does not currently exist
        while not found:
            version += 1
            test_pub_file = '%s_v%03d.%s' % (self.file_name,
                                                version, self.pub_ext)
            if not os.path.isfile(os.path.join(self.actual_pub_path,
                                                                test_pub_file)):
                found = True
                break

        # update latest values
        self.version = 'v%03d' % version

    def archive_old_version(self):
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

    def _get_pub_file_type(self):
        '''
        return file type to save as based on extension
        '''
        ext_file_type = {'ma': 'mayaAscii',
                         'mb': 'mayaBinary',
                         'obj': 'OBJ'
                        }

        return ext_file_type[self.pub_ext]

    def export_maya_file(self):
        '''
        Exports selection to the ".ma" file or specified publish extension
            basic version, may want a separate / better one for FBX's, etc.
        '''
        ascii_path = "%s.%s" % (self.actual_file_pub_path, self.pub_ext)
        print 'Exporting "%s"...' % ascii_path
        try:
            exportedFile = mc.file(ascii_path, type=self._get_pub_file_type(),
                                    exportSelected=True, force=self.force_save)
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

    def _check_for_existing_publish(self):
        '''
        determine if publish version already exists
        '''
        if os.path.isfile('%s.%s' % (self.actual_file_pub_path, self.pub_ext)):
            confirm_action = self._version_exists_win(self.version_file_name)

            print 'File exists: %s.%s. Proceeding with %s' \
                                                % (self.actual_file_pub_path,
                                                   self.pub_ext, confirm_action)

            # determine how to proceed with file
            if confirm_action == 'Version Up':
                self.archive_version = '%s.%s' \
                                   % (self.actual_file_pub_path, self.pub_ext)
                self.get_next_version()
            elif confirm_action == 'Replace':
                self.force_save = True
            else:
                print 'Canceled publish.'
                return False

        else:
            print 'File does not exist, checking if directory structure exists..'
            self._verify_path_dirs_exist()

        return True

    def do_publish(self):
        '''
        publish to versioned file
        '''
        raise Exception("This is the base class. Should be extended to "
                            + "a child class for specific publishing purposes.")