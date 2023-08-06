# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QSupervisorControl/data/about.ui'
#
# Created: Sat Feb  2 01:07:54 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 415)
        Form.setMinimumSize(QtCore.QSize(400, 415))
        Form.setMaximumSize(QtCore.QSize(400, 415))
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 231))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblQSC = QtGui.QLabel(Form)
        self.lblQSC.setGeometry(QtCore.QRect(10, 250, 381, 51))
        self.lblQSC.setLineWidth(0)
        self.lblQSC.setAlignment(QtCore.Qt.AlignCenter)
        self.lblQSC.setWordWrap(True)
        self.lblQSC.setObjectName(_fromUtf8("lblQSC"))
        self.lblSC = QtGui.QLabel(Form)
        self.lblSC.setGeometry(QtCore.QRect(10, 300, 381, 61))
        self.lblSC.setLineWidth(0)
        self.lblSC.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSC.setWordWrap(True)
        self.lblSC.setObjectName(_fromUtf8("lblSC"))
        self.bntOk = QtGui.QPushButton(Form)
        self.bntOk.setGeometry(QtCore.QRect(300, 370, 94, 41))
        self.bntOk.setObjectName(_fromUtf8("bntOk"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Sobre o QSupervisorControl", None, QtGui.QApplication.UnicodeUTF8))
        self.lblQSC.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p>QSupervisorControl é um software licenciado sobre <br/>Licença da Apache 2.0, mais informações podem ser obtidas no <a href=\"https://bitbucket.org/rodrigopmatias/qsupervisorcontrol\">https://bitbucket.org/rodrigopmatias/qsupervisorcontrol</a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSC.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p>O Supervisor é um software de terceiro e esta licenciado sobre uma licença BSD-derived, mais informações podem ser obtidas em <a href=\"http://supervisord.org\">http://supervisord.org/</a> </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.bntOk.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))

