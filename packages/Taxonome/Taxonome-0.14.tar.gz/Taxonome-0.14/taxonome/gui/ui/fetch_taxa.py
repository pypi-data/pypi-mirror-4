# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taxonome/gui/ui/fetch_taxa.ui'
#
# Created: Tue May 29 11:46:18 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FetchOptsDialog(object):
    def setupUi(self, FetchOptsDialog):
        FetchOptsDialog.setObjectName(_fromUtf8("FetchOptsDialog"))
        FetchOptsDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(FetchOptsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(FetchOptsDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.groupname = QtGui.QLineEdit(FetchOptsDialog)
        self.groupname.setObjectName(_fromUtf8("groupname"))
        self.horizontalLayout.addWidget(self.groupname)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(FetchOptsDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.service = QtGui.QComboBox(FetchOptsDialog)
        self.service.setObjectName(_fromUtf8("service"))
        self.horizontalLayout_2.addWidget(self.service)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_3 = QtGui.QLabel(FetchOptsDialog)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.buttonBox = QtGui.QDialogButtonBox(FetchOptsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.groupname)
        self.label_2.setBuddy(self.service)

        self.retranslateUi(FetchOptsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FetchOptsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FetchOptsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FetchOptsDialog)

    def retranslateUi(self, FetchOptsDialog):
        FetchOptsDialog.setWindowTitle(QtGui.QApplication.translate("FetchOptsDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("FetchOptsDialog", "Group name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("FetchOptsDialog", "Source", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("FetchOptsDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This will download basic data for species in  a taxonomic group, e.g. <span style=\" font-style:italic;\">Poaceae</span>. So far, this only works with GRIN, where it can access synonymy data.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

