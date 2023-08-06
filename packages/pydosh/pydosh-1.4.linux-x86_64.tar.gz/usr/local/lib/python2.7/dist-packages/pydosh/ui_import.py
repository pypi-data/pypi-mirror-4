# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/import.ui'
#
# Created: Sun Apr  7 13:23:07 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Import(object):
    def setupUi(self, Import):
        Import.setObjectName(_fromUtf8("Import"))
        Import.resize(672, 504)
        self.gridLayout = QtGui.QGridLayout(Import)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.view = QtGui.QTableView(Import)
        self.view.setObjectName(_fromUtf8("view"))
        self.gridLayout.addWidget(self.view, 0, 0, 1, 1)
        self.CsvImport = QtGui.QWidget(Import)
        self.CsvImport.setObjectName(_fromUtf8("CsvImport"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.CsvImport)
        self.horizontalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.progressBar = QtGui.QProgressBar(self.CsvImport)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout_2.addWidget(self.progressBar)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.selectAllButton = QtGui.QPushButton(self.CsvImport)
        self.selectAllButton.setObjectName(_fromUtf8("selectAllButton"))
        self.horizontalLayout_2.addWidget(self.selectAllButton)
        self.importCancelButton = QtGui.QPushButton(self.CsvImport)
        self.importCancelButton.setObjectName(_fromUtf8("importCancelButton"))
        self.horizontalLayout_2.addWidget(self.importCancelButton)
        self.closeButton = QtGui.QPushButton(self.CsvImport)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout_2.addWidget(self.closeButton)
        self.gridLayout.addWidget(self.CsvImport, 3, 0, 1, 1)
        self.frame = QtGui.QFrame(Import)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.selectedCounter = QtGui.QLabel(self.frame)
        self.selectedCounter.setObjectName(_fromUtf8("selectedCounter"))
        self.horizontalLayout.addWidget(self.selectedCounter)
        spacerItem1 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.toImportCounter = QtGui.QLabel(self.frame)
        self.toImportCounter.setObjectName(_fromUtf8("toImportCounter"))
        self.horizontalLayout.addWidget(self.toImportCounter)
        spacerItem2 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.importedCounter = QtGui.QLabel(self.frame)
        self.importedCounter.setObjectName(_fromUtf8("importedCounter"))
        self.horizontalLayout.addWidget(self.importedCounter)
        spacerItem3 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.errorsCounter = QtGui.QLabel(self.frame)
        self.errorsCounter.setObjectName(_fromUtf8("errorsCounter"))
        self.horizontalLayout.addWidget(self.errorsCounter)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)

        self.retranslateUi(Import)
        QtCore.QMetaObject.connectSlotsByName(Import)

    def retranslateUi(self, Import):
        Import.setWindowTitle(QtGui.QApplication.translate("Import", "Import CSV", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllButton.setText(QtGui.QApplication.translate("Import", "Select all", None, QtGui.QApplication.UnicodeUTF8))
        self.importCancelButton.setText(QtGui.QApplication.translate("Import", "&Import", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Import", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Import", "selected:", None, QtGui.QApplication.UnicodeUTF8))
        self.selectedCounter.setText(QtGui.QApplication.translate("Import", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Import", "available:", None, QtGui.QApplication.UnicodeUTF8))
        self.toImportCounter.setText(QtGui.QApplication.translate("Import", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Import", "imported:", None, QtGui.QApplication.UnicodeUTF8))
        self.importedCounter.setText(QtGui.QApplication.translate("Import", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Import", "errors:", None, QtGui.QApplication.UnicodeUTF8))
        self.errorsCounter.setText(QtGui.QApplication.translate("Import", "0", None, QtGui.QApplication.UnicodeUTF8))

import pydosh_rc
