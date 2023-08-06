# -*- coding: utf-8 -*-
from QSupervisorControl.ui.layout.about import Ui_Form
from PyQt4.QtGui import QDialog


class AboutDialog(QDialog):

    def close_me(self):
        self.close()

    def __init__(self, *args, **kargs):
        QDialog.__init__(self, *args, **kargs)

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._connect()

    def _connect(self):
        ui = self._ui

        ui.bntOk.clicked.connect(self.close_me)
