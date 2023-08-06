# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'long_operation_box.ui'
#
# Created: Tue Jun 21 18:38:17 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LongOperationBox(object):
    def setupUi(self, LongOperationBox):
        LongOperationBox.setObjectName(_fromUtf8("LongOperationBox"))
        LongOperationBox.resize(247, 57)
        self.gridLayout = QtGui.QGridLayout(LongOperationBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(LongOperationBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(LongOperationBox)
        self.progressBar.setProperty(_fromUtf8("value"), 24)
        self.progressBar.setFormat(_fromUtf8(""))
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)

        self.retranslateUi(LongOperationBox)
        QtCore.QMetaObject.connectSlotsByName(LongOperationBox)

    def retranslateUi(self, LongOperationBox):
        LongOperationBox.setWindowTitle(QtGui.QApplication.translate("LongOperationBox", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LongOperationBox", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

