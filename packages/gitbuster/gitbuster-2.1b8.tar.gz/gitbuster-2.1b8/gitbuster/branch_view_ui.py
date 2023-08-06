# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'branch_view.ui'
#
# Created: Wed Jun 22 20:35:20 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BranchView(object):
    def setupUi(self, BranchView):
        BranchView.setObjectName(_fromUtf8("BranchView"))
        BranchView.resize(320, 676)
        BranchView.setMinimumSize(QtCore.QSize(320, 0))
        BranchView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.layout = QtGui.QGridLayout(BranchView)
        self.layout.setObjectName(_fromUtf8("layout"))

        self.retranslateUi(BranchView)
        QtCore.QMetaObject.connectSlotsByName(BranchView)

    def retranslateUi(self, BranchView):
        BranchView.setWindowTitle(QtGui.QApplication.translate("BranchView", "Form", None, QtGui.QApplication.UnicodeUTF8))

