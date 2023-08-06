# -*- coding: utf-8 -*-
from QSupervisorControl.ui.layout.about import Ui_Form
from PyQt4.QtGui import QDialog, QPixmap

import os

ui_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(ui_dir)
data_dir = os.path.join(app_dir, 'data')

class AboutDialog(QDialog):

    def close_me(self):
        self.close()

    def __init__(self, *args, **kargs):
        QDialog.__init__(self, *args, **kargs)

        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self._ui.lblImage.setPixmap(
            QPixmap(
                os.path.join(
                    data_dir,
                    'olho-animal-tigre.jpg'
                )
            )
        )

        self._connect()

    def _connect(self):
        ui = self._ui

        ui.bntOk.clicked.connect(self.close_me)
