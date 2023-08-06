# -*- coding: utf-8 -*-
from QSupervisorControl.ui.layout.logview import Ui_dialog
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QThread, pyqtSignal, QPoint
from QSupervisorControl import db
from sqlalchemy.orm.exc import NoResultFound

import codecs

class _ThreadLogView(QThread):

    def __init__(self, logview, *args, **kargs):
        super(_ThreadLogView, self).__init__(*args, **kargs)
        self.logview = logview
        self.live = True

    def run(self):
        with codecs.open(self.logview.log_file, 'r', 'utf-8') as fd:
            fd.seek(0, 2)
            while self.live is True:
                line = fd.readline()
                if line is not None:
                    self.logview.update_log.emit(line)
                self.msleep(10)

class LogViewDialog(QDialog):

    def close_me(self):
        self._thread.quit()
        self.close()

    def _load_data(self):
        session = db.get_session()

        try:
            lc = session.query(db.Launche).filter_by(name=self._program).one()
        except NoResultFound:
            pass
        else:
            self.log_file = lc.log_file
            self._thread = _ThreadLogView(self, parent=self)
            self._thread.start()

    def create_thread(self):
        pass

    update_log = pyqtSignal(str)

    def _update_log(self, line):
        self._ui.txtView.insertPlainText(line);

    def clear_view(self):
        self._ui.txtView.setText('')

    def __init__(self, program, *args, **kargs):
        QDialog.__init__(self, *args, **kargs)
        self._ui = Ui_dialog()
        self._ui.setupUi(self)
        self._program = program
        self._connect()
        self._load_data()

    def _connect(self):
        ui = self._ui

        ui.btnClose.clicked.connect(self.close_me)
        ui.btnClear.clicked.connect(self.clear_view)

        self.update_log.connect(self._update_log)
