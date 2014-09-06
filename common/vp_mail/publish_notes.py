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
# $Date: 2014-09-04$
# $Revision: 1.0$
# $Author: johnz $
#


class PublishNotes(object):
    '''
    main class for gathering publish notes from user by providing
        a prompt dialog based on what application they are in, ie. maya or mobu
    '''
    def __init__(self):
        '''
        initialize instance
        '''
        self._win_title = "Publish Notes"
        self._win_msg = "Enter publish notes / updates."
        self._application = None
        self.notes = None

        # attempt to determine current application
        self._determine_application()

    def _determine_application(self):
        '''
        attempt to determine what is current application before
            proceeding to get notes input from user
        '''
        if not self._check_for_maya() and not self._check_for_mobu():
            raise ImportError("Unable to ascertain / import current "
                              + "application as Maya or MotionBuilder. "
                              + "Make sure application is correct.")

        if self._application.lower() == "maya":
            self._get_maya_notes()

        if self._application.lower() == "mobu":
            self._get_mobu_notes()

    def _check_for_maya(self):
        '''
        try to determine if current application is maya related
        '''
        found = False
        try:
            import maya.cmds as mc
            self._application = mc.about(query=True, application=True)
            found = True
        except:
            pass

        return found

    def _check_for_mobu(self):
        '''
        try to determine if current application is motionbuilder related
        '''
        found = False
        try:
            import re
            from pyfbsdk import FBSystem
            mobu_patt = re.compile("motionbuilder", re.IGNORECASE)
            if mobu_patt.search(FBSystem().ApplicationPath):
                self._application = "mobu"
                found = True
        except:
            pass

        return found

    def _get_maya_notes(self):
        '''
        prompt for and retrieve publish notes from user in maya
        '''
        import maya.cmds as mc
        confirm = mc.promptDialog(
                                    title=self._win_title,
                                    messageAlign="center",
                                    message=self._win_msg,
                                    button=["OK", "Cancel"],
                                    defaultButton="OK",
                                    cancelButton="Cancel",
                                    dismissString="Cancel"
                                    )

        if confirm == "OK":
            self.notes = mc.promptDialog(query=True, text=True)

    def _get_mobu_notes(self):
        '''
        prompt for and retrieve publish notes from user in maya
        '''
        from pyfbsdk import FBMessageBoxGetUserValue, FBPopupInputType

        cancelBtn = 0
        confirm, notes = FBMessageBoxGetUserValue(self._win_title,
                                                  self._win_msg,
                                                  "",
                                                FBPopupInputType.kFBPopupString,
                                                "Ok", "Cancel", None,
                                                1, cancelBtn)
        print confirm, notes

        if confirm == 1:
            self.notes = notes
