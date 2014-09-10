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
# $Date: 2014-07-28$
# $Revision: 1.0$
# $Author: johnz $
#

import os
import re

from subprocess import Popen
from show import show

from PyQt4 import QtGui, QtCore, uic


class VP_Environ_Gui(QtGui.QMainWindow):
    '''
    VP Environment setup tool's gui control setup and actions
    '''
    def __init__(self):
        '''
        initializing VP Environment to inherit from QtGui.MainWindow and
        establish variables and signal connections
        '''
        super(VP_Environ_Gui, self).__init__()
        self.__setUI()

        # initialize base details
        self.details = {'SHOW': 'SHOW',
                        'ARTIST': '',
                        'ARTIST_EMAIL': ''}

        # complete gui setup
        self._setupDefaults()
        self._setSignalCallbacks()

    def __setUI(self):
        '''
        set gui to utilize uic file
        '''
        # locate ui file
        ui_file = 'vp_environ_v03.ui'
        ico_file = 'vp_environ.ico'
        cwd = os.path.dirname(os.path.abspath(__file__))
        ui = os.path.join(cwd, 'ui', ui_file)
        ico = os.path.join(cwd, 'images', ico_file)

        uic.loadUi(ui, baseinstance=self)
        self.setWindowIcon(QtGui.QIcon(ico))

    def _setSignalCallbacks(self):
        '''
        setup signal connection callbacks for gui elements
        '''
        self.show_cmbx.currentIndexChanged.connect(
                                            self.show_cmbx_currentIndexChanged)
        self.email_entry.editingFinished.connect(
                                            self.email_entry_editingFinished)
        self.name_entry.editingFinished.connect(
                                            self.name_entry_editingFinished)
        self.ok_pbutton.clicked.connect(self.ok_pbutton_clicked)

    def _setupDefaults(self):
        '''
        setup default gui values
        '''
        self.addShows()
        self.setDefaultTexts()

    @QtCore.pyqtSlot(int)
    def show_cmbx_currentIndexChanged(self):
        '''
        show combo box slot updates vpshow variable with selected show
        '''
        if str(self.show_cmbx.currentText()) != '':
            self.details['SHOW'] = str(self.show_cmbx.currentText())
        else:
            self.details['SHOW'] = 'SHOW'

    @QtCore.pyqtSlot()
    def email_entry_editingFinished(self):
        '''
        email entry field updates artist email variable after verifying if
        valid
        '''
        if len(str(self.email_entry.text()).strip()):
            self.details['ARTIST_EMAIL'] = str(self.email_entry.text()).strip()
        else:
            self.details['ARTIST_EMAIL'] = ''

    @QtCore.pyqtSlot()
    def name_entry_editingFinished(self):
        '''
        name entry field updates artist variable after verifying if
        valid
        '''
        if len(str(self.email_entry.text()).strip()):
            self.details['ARTIST'] = str(self.name_entry.text()).strip()
        else:
            self.details['ARTIST'] = ''

    @QtCore.pyqtSlot(bool)
    def ok_pbutton_clicked(self):
        '''
        ok button slot kicks off environment setup
        '''
        if not self.validateShow() \
                or not self.validateEmail() \
                        or not self.validateName():
            return

        # self.get_artist()

        for key in self.details:
            self.set_env(key, self.details[key])

        self.close()

    # def get_artist(self):
    #     '''
    #     get artist from email
    #     '''
    #     self.details['ARTIST'] =\
    #                         self.details['ARTIST_EMAIL'].split('@')[0] or ''

    def setDefaultTexts(self):
        '''
        set default text values for gui entry fields element
        '''
        self.email_entry.setText(str(self.details['ARTIST_EMAIL']))

    def validateShow(self):
        '''
        validate that user has provided a show
        :return C(bool)
        '''
        if self.details['SHOW'] == 'SHOW':
            msg = 'No active show selected.\nPlease select show from list.'

            nonwin_dialog = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                                            'Issue', msg)
            nonwin_dialog.exec_()
            return False

        return True

    def validateEmail(self):
        '''
        validate that user provided a 'valid' email address
            'valid' is questionable as nothing currently available
                to check against. checking for at least an email address format
        :return C(bool)
        '''
        if not re.match('\w+@\w+.\w+', self.details['ARTIST_EMAIL']):
            msg = '%s is not a valid email address.\n' \
                    % self.details['ARTIST_EMAIL'] \
                    + 'Please re-enter email address.'
            nonwin_dialog = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                                            'Issue', msg)
            nonwin_dialog.exec_()

            return False

        return True

    def validateName(self):
        '''
        validate that user provided a 'valid' artist name
            'valid' is questionable as nothing currently available
                to check against. checking for at least text
        :return C(bool)
        '''
        if not re.match('\w+@\w+.\w+', self.details['ARTIST_EMAIL']):
            msg = '%s is not a valid email address.\n' \
                    % self.details['ARTIST_EMAIL'] \
                    + 'Please re-enter email address.'
            nonwin_dialog = QtGui.QMessageBox(QtGui.QMessageBox.Warning,
                                                            'Issue', msg)
            nonwin_dialog.exec_()

            return False

        return True

    def addShows(self):
        '''
        add active shows to gui
        '''
        self.show_cmbx.clear()
        active_shows = show.GetActive()
        active_shows.sort()
        active_shows.insert(0, '')
        self.addToComboBox(self.show_cmbx, active_shows)

    @staticmethod
    def set_env(env_var, env_val):
        '''
        attempt to connect value to environment variable

        :type   env_var: C{string}
        :param  env_var: environment variable
        :type   env_val: C{string}
        :param  env_val: value to set to environment variable
        '''
        try:
            Popen(['SETX', env_var, env_val], shell=True)
            return
        except Exception, e:
            raise e

    @staticmethod
    def addToComboBox(cbox, items):
        '''
        iterate over items and add to gui combo box

        :type   cbox: C(QComboBox)
        :param  cbox: pyqt gui combo box element
        :type   items: C(list)
        :param  items: list of text items to add to combo box
        '''
        for item in items:
            cbox.addItem(item)


def main(argv=None):
    '''
    creates and launches instance of VP Environment Gui
    :param argv:
    '''
    app = None

    # prepping app
    if not QtGui.QApplication.instance():
        app = QtGui.QApplication(argv)
        app.setStyle('plastique')

    # create the main window
    vp_environ = VP_Environ_Gui()
    vp_environ.show()

    # run the application if necessary
    if app:
        return app.exec_()

    # no errors since we're not running our own event loop
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))