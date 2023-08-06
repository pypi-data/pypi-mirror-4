# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remote_branch_dialog.ui'
#
# Created: Tue Jun 21 18:38:18 2011
#      by: PyQt4 UI code generator 4.8.3
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
        Form.resize(412, 142)
        Form.setMinimumSize(QtCore.QSize(0, 142))
        Form.setMaximumSize(QtCore.QSize(16777215, 150))
        self.gridLayout_2 = QtGui.QGridLayout(Form)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.remoteLabel = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.remoteLabel.sizePolicy().hasHeightForWidth())
        self.remoteLabel.setSizePolicy(sizePolicy)
        self.remoteLabel.setMinimumSize(QtCore.QSize(90, 22))
        self.remoteLabel.setMaximumSize(QtCore.QSize(90, 22))
        self.remoteLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.remoteLabel.setObjectName(_fromUtf8("remoteLabel"))
        self.gridLayout.addWidget(self.remoteLabel, 0, 0, 1, 1)
        self.remoteComboBox = QtGui.QComboBox(Form)
        self.remoteComboBox.setMinimumSize(QtCore.QSize(0, 22))
        self.remoteComboBox.setObjectName(_fromUtf8("remoteComboBox"))
        self.gridLayout.addWidget(self.remoteComboBox, 0, 1, 1, 2)
        self.locationLabel = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.locationLabel.sizePolicy().hasHeightForWidth())
        self.locationLabel.setSizePolicy(sizePolicy)
        self.locationLabel.setMinimumSize(QtCore.QSize(90, 22))
        self.locationLabel.setMaximumSize(QtCore.QSize(90, 22))
        self.locationLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.locationLabel.setObjectName(_fromUtf8("locationLabel"))
        self.gridLayout.addWidget(self.locationLabel, 1, 0, 1, 1)
        self.locationLineEdit = QtGui.QLineEdit(Form)
        self.locationLineEdit.setMinimumSize(QtCore.QSize(0, 22))
        self.locationLineEdit.setObjectName(_fromUtf8("locationLineEdit"))
        self.gridLayout.addWidget(self.locationLineEdit, 1, 1, 1, 1)
        self.locationDialogButton = QtGui.QToolButton(Form)
        self.locationDialogButton.setObjectName(_fromUtf8("locationDialogButton"))
        self.gridLayout.addWidget(self.locationDialogButton, 1, 2, 1, 1)
        self.branchLabel = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.branchLabel.sizePolicy().hasHeightForWidth())
        self.branchLabel.setSizePolicy(sizePolicy)
        self.branchLabel.setMinimumSize(QtCore.QSize(90, 22))
        self.branchLabel.setMaximumSize(QtCore.QSize(90, 22))
        self.branchLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.branchLabel.setObjectName(_fromUtf8("branchLabel"))
        self.gridLayout.addWidget(self.branchLabel, 2, 0, 1, 1)
        self.branchComboBox = QtGui.QComboBox(Form)
        self.branchComboBox.setMinimumSize(QtCore.QSize(0, 22))
        self.branchComboBox.setObjectName(_fromUtf8("branchComboBox"))
        self.gridLayout.addWidget(self.branchComboBox, 2, 1, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 1, 1, 1)
        self.cancelButton = QtGui.QPushButton(Form)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.gridLayout_2.addWidget(self.cancelButton, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 2, 1, 1, 1)
        self.fetchButton = QtGui.QPushButton(Form)
        self.fetchButton.setObjectName(_fromUtf8("fetchButton"))
        self.gridLayout_2.addWidget(self.fetchButton, 2, 2, 1, 1)
        self.addButton = QtGui.QPushButton(Form)
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.gridLayout_2.addWidget(self.addButton, 2, 3, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "New remote branch", None, QtGui.QApplication.UnicodeUTF8))
        self.remoteLabel.setText(QtGui.QApplication.translate("Form", "Remote:", None, QtGui.QApplication.UnicodeUTF8))
        self.locationLabel.setText(QtGui.QApplication.translate("Form", "Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.locationDialogButton.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.branchLabel.setText(QtGui.QApplication.translate("Form", "Choose branch:", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelButton.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.fetchButton.setText(QtGui.QApplication.translate("Form", "Fetch", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Form", "Add", None, QtGui.QApplication.UnicodeUTF8))

