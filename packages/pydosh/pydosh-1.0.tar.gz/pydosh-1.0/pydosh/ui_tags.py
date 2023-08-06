# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/tags.ui'
#
# Created: Sat Mar  2 16:27:20 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Tags(object):
    def setupUi(self, Tags):
        Tags.setObjectName(_fromUtf8("Tags"))
        Tags.resize(223, 267)
        self.gridLayout_2 = QtGui.QGridLayout(Tags)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.widget = QtGui.QWidget(Tags)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.addTagButton = QtGui.QToolButton(self.widget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addTagButton.setIcon(icon)
        self.addTagButton.setObjectName(_fromUtf8("addTagButton"))
        self.gridLayout.addWidget(self.addTagButton, 0, 1, 1, 1)
        self.deleteTagButton = QtGui.QToolButton(self.widget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/delete.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteTagButton.setIcon(icon1)
        self.deleteTagButton.setObjectName(_fromUtf8("deleteTagButton"))
        self.gridLayout.addWidget(self.deleteTagButton, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 173, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.tagView = QtGui.QListView(self.widget)
        self.tagView.setObjectName(_fromUtf8("tagView"))
        self.gridLayout.addWidget(self.tagView, 0, 0, 3, 1)
        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Tags)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi(Tags)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Tags.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Tags.reject)
        QtCore.QMetaObject.connectSlotsByName(Tags)

    def retranslateUi(self, Tags):
        Tags.setWindowTitle(QtGui.QApplication.translate("Tags", "Tag Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.addTagButton.setText(QtGui.QApplication.translate("Tags", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteTagButton.setText(QtGui.QApplication.translate("Tags", "...", None, QtGui.QApplication.UnicodeUTF8))

import pydosh_rc
