# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog, QFileDialog
from QSupervisorControl.ui.layout.configuration import Ui_Form
from QSupervisorControl import db
from sqlalchemy.orm.exc import NoResultFound
import os


class ConfigurationDialog(QDialog):

    def select_directory(self, line_edit):
        line_edit.setText(
            QFileDialog.getExistingDirectory(
                self,
                directory=line_edit.text()
            )
        )

    def select_file(self, line_edit):
        line_edit.setText(
            QFileDialog.getOpenFileName(
                self,
                directory=line_edit.text()
            )
        )

    def load_data(self):
        session = db.get_session()

        try:
            launche = session.query(db.Launche).filter_by(name=self._program).one()
        except NoResultFound:
            launche = Launche()
        finally:
            self._ui.txtMonitorPattern.setText(launche.monitor_pattern or '')
            self._ui.txtTouchFile.setText(launche.touch_file or '')
            self._ui.txtLogFile.setText(launche.log_file or '')
            self._ui.txtPath.setText(launche.path or '')

    def store(self):
        session = db.get_session()

        try:
            launche = session.query(db.Launche).filter_by(name=self._program).one()
        except NoResultFound:
            launche = Launche()
        finally:
            launche.name = self._program
            launche.monitor_pattern = unicode(self._ui.txtMonitorPattern.text())
            launche.touch_file = unicode(self._ui.txtTouchFile.text())
            launche.log_file = unicode(self._ui.txtLogFile.text())
            launche.path = unicode(self._ui.txtPath.text())
            session.add(launche)

        session.commit()

    def cancel(self):
        self.close()

    def __init__(self, program, *args, **kargs):
        QDialog.__init__(self, *args, **kargs)

        self._program = program
        self._ui = Ui_Form()
        self._ui.setupUi(self)

        self.setWindowTitle(self.windowTitle() + ' [%s]' % program)
        self._connect()

    def fn(self, method, *args, **kargs):
        def wrap():
            return method(*args, **kargs)
        return wrap

    def project_changed(self, value):
        if self._ui.txtTouchFile.text() == '':
            self._ui.txtTouchFile.setText(
                os.path.join(unicode(value), 'reload.txt')
            )
        if self._ui.txtLogFile.text() == '':
            self._ui.txtLogFile.setText(
                os.path.join(unicode(value), 'log.txt')
            )

    def _connect(self):
        ui = self._ui

        ui.bntCancel.clicked.connect(self.cancel)
        ui.bntStore.clicked.connect(self.store)

        ui.bntSearchProject.clicked.connect(
            self.fn(
                self.select_directory,
                ui.txtPath
            )
        )

        ui.bntSearchReloadFile.clicked.connect(
            self.fn(
                self.select_file,
                ui.txtTouchFile
            )
        )

        ui.bntSearchLogFile.clicked.connect(
            self.fn(
                self.select_file,
                ui.txtLogFile
            )
        )

        ui.txtPath.textChanged.connect(self.project_changed)
