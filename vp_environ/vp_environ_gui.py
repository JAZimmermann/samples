#
# Copyright (c) [2014] John Zimmermann
#
# $URL$
# $Date: 2014-07-28$
# $Revision: 1.0$
# $Author: johnz $
#

import os
import re
import sys

from subprocess import Popen

# make sure package location is available
apath = os.getenv("PYTHONPATH", "b:/tools/common/python")
if apath not in sys.path:
    sys.path.insert(2, apath)

from show import show

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt


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
                        'ARTIST_EMAIL': '',
                        'ARTIST_USERNAME': ''}

        # make sure base environment is setup
        self._check_set_necessary_env_vars()

        # complete gui setup
        self._setupDefaults()
        self._setSignalCallbacks()

    def __setUI(self):
        '''
        set gui to utilize uic file
        '''
        # locate ui file
        ui_file = 'vp_environ_v04.ui'
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

    def _check_existing_key_env_vars(self):
        '''
        check to see if environment variables are already exist
            to possibly auto-populate the fields for user
        '''
        for env_key in self.details.keys():
            if env_key in os.environ and os.getenv(env_key) != "":
                self.details[env_key] = os.getenv(env_key)

    def _check_set_necessary_env_vars(self):
        '''
        check to see if necessary working environment variables exist
        '''
        # for quick access to show root path
        if 'SHOW_ROOT' not in os.environ:
            self.set_env('SHOW_ROOT', 'b:/show')

        if 'TOOLS_ROOT' not in os.environ:
            self.set_env('TOOLS_ROOT', 'b:/tools')

        # for common DD python tools, particularly vir_prod package
        if 'PYTHONPATH' not in os.environ:
            self.set_env('PYTHONPATH', 'b:/tools/common/python')
        elif 'b:/tools/common/python'.replace('/', os.sep) \
                                                not in os.getenv('PYTHONPATH'):
            self.set_env('PYTHONPATH', r'%PYTHONPATH%;b:/tools/common/python')

    def _setupDefaults(self):
        '''
        setup default gui values
        '''
        self._check_existing_key_env_vars()
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

        # display wait cursor while spending time setting env vars
        QtGui.QApplication.setOverrideCursor(
                                    QtGui.QCursor(Qt.WaitCursor))
        self.get_artist_username()

        for key in self.details:
            self.set_env(key, self.details[key])

        # restore regular cursor
        QtGui.QApplication.restoreOverrideCursor()
        self.close()

    def get_artist_username(self):
        '''
        get artist from email
        '''
        self.details['ARTIST_USERNAME'] =\
                            self.details['ARTIST_EMAIL'].split('@')[0] or ''

    def setDefaultTexts(self):
        '''
        set default text values for gui entry fields element
        '''
        self.email_entry.setText(str(self.details['ARTIST_EMAIL']))
        self.name_entry.setText(str(self.details['ARTIST']))

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
        if not re.match('[\w._]+@\w+.\w+', self.details['ARTIST_EMAIL']):
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
        if not self.details['ARTIST']:
            msg = '%s is not a valid .\n' \
                    % self.details['ARTIST'] \
                    + 'Please re-enter artist.'
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

        if self.details['SHOW'] not in ['SHOW', ''] \
                and self.details['SHOW'] in active_shows:
            for i in range(len(active_shows)):
                if self.details['SHOW'] == active_shows[i]:
                    self.show_cmbx.setCurrentIndex(i)
                    break

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
            setting_env = Popen(['SETX', env_var, env_val], shell=True)
            setting_env.wait()
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