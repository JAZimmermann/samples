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
from VAD.ddPublishBase import dPublisherBase
# from mayatools.VAD import ddConstants


class RigPublisher(dPublisherBase):
    '''
    deals with processing of Maya rig publishing
    '''
    def __init__(self, details):
        '''
        initialize values
        '''
        super(RigPublisher, self).__init__(details, lib_category='characters')
        self._character = details.get('character')
        self._character_type = details.get('character_type')
        self._rig_type = details.get('rig_type')
        self._rig_category = details.get('rig_category', 'maya')

    @property
    def character(self):
        '''
        get character name for publish
        '''
        return self._character

    @property
    def character_type(self):
        '''
        get base character category type
        '''
        return self._character_type

    @property
    def rig_type(self):
        '''
        get specific rig style coded, ie. "BSK" of "BSK (bones, skinned)"
        '''
        return self._rig_type

    @property
    def file_name(self):
        '''
        get the expected publish file name prefix
        '''
        return "%s_rig_%s_%s" % (self.character,
                                 self._rig_category,
                                 self.rig_type)

    @property
    def rel_pub_path(self):
        '''
        get full relative directory path for publish by combining path
            elements together natively for operating system.
            *Note*- Relative path is the section of path between the
            asset library and the actual file
        '''
        return os.path.join(self.character_type, self.character,
                                        'rig', self._rig_category, self.FOLDER_PUB)

    def _validate_attributes(self):
        '''
        validate all required attributes have been passed
        '''
        if not self.character or not self.character_type \
                    or not self.rig_type or not self.version \
                    or not os.path.isdir(self.asset_library):
            return False

        return True

    def do_publish(self, force=False):
        '''
        publish rig to versioned file
        '''
        # valid information provided
        if self._validate_attributes():

            # make sure how to proceed in publish,
            #   does it need input from user, etc.
            do_publish = self._check_for_existing_publish()

            # check if publish was canceled
            if not do_publish:
                return

            # attempt to publish file
            valid_export = self.export_maya_file()

            if valid_export:
                # archive found older publish
                self.archive_old_version()

            print 'Published %s.ma%s complete.' \
                                    % (self.version_file_name,
                                    " not" if not valid_export else '')
