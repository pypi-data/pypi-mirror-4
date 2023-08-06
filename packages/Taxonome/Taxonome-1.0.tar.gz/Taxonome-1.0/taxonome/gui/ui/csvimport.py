# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taxonome/gui/ui/csvimport.ui'
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

class Ui_CsvImportDialog(object):
    def setupUi(self, CsvImportDialog):
        CsvImportDialog.setObjectName(_fromUtf8("CsvImportDialog"))
        CsvImportDialog.resize(435, 528)
        self.verticalLayout = QtGui.QVBoxLayout(CsvImportDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(CsvImportDialog)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.ds_name = QtGui.QLineEdit(CsvImportDialog)
        self.ds_name.setObjectName(_fromUtf8("ds_name"))
        self.horizontalLayout.addWidget(self.ds_name)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_4 = QtGui.QLabel(CsvImportDialog)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(CsvImportDialog)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.namefield = QtGui.QComboBox(CsvImportDialog)
        self.namefield.setObjectName(_fromUtf8("namefield"))
        self.horizontalLayout_2.addWidget(self.namefield)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.groupBox = QtGui.QGroupBox(CsvImportDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.noauth = QtGui.QRadioButton(self.groupBox)
        self.noauth.setObjectName(_fromUtf8("noauth"))
        self.verticalLayout_2.addWidget(self.noauth)
        self.auth_with_name = QtGui.QRadioButton(self.groupBox)
        self.auth_with_name.setObjectName(_fromUtf8("auth_with_name"))
        self.verticalLayout_2.addWidget(self.auth_with_name)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.auth_separate = QtGui.QRadioButton(self.groupBox)
        self.auth_separate.setChecked(True)
        self.auth_separate.setObjectName(_fromUtf8("auth_separate"))
        self.horizontalLayout_3.addWidget(self.auth_separate)
        self.authfield = QtGui.QComboBox(self.groupBox)
        self.authfield.setEnabled(True)
        self.authfield.setObjectName(_fromUtf8("authfield"))
        self.horizontalLayout_3.addWidget(self.authfield)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.groupBox)
        self.label_2 = QtGui.QLabel(CsvImportDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.preview = QtGui.QTableWidget(CsvImportDialog)
        self.preview.setObjectName(_fromUtf8("preview"))
        self.preview.setColumnCount(0)
        self.preview.setRowCount(0)
        self.verticalLayout.addWidget(self.preview)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_5 = QtGui.QLabel(CsvImportDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_4.addWidget(self.label_5)
        self.csv_encoding = QtGui.QComboBox(CsvImportDialog)
        self.csv_encoding.setObjectName(_fromUtf8("csv_encoding"))
        self.horizontalLayout_4.addWidget(self.csv_encoding)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.buttonBox = QtGui.QDialogButtonBox(CsvImportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_3.setBuddy(self.ds_name)
        self.label.setBuddy(self.namefield)
        self.label_2.setBuddy(self.preview)

        self.retranslateUi(CsvImportDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CsvImportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CsvImportDialog.reject)
        QtCore.QObject.connect(self.auth_separate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.authfield.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CsvImportDialog)

    def retranslateUi(self, CsvImportDialog):
        CsvImportDialog.setWindowTitle(QtGui.QApplication.translate("CsvImportDialog", "Import CSV", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("CsvImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:8pt;\">Dataset name:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("CsvImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Please select which columns contain the name (e.g. </span><span style=\" font-size:8pt; font-style:italic;\">Vigna radiata</span><span style=\" font-size:8pt;\">) and the name authorities (e.g. \'(L.) R. Wilczek\').</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("CsvImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:8pt;\">Name column:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("CsvImportDialog", "Authorities:", None, QtGui.QApplication.UnicodeUTF8))
        self.noauth.setText(QtGui.QApplication.translate("CsvImportDialog", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.auth_with_name.setText(QtGui.QApplication.translate("CsvImportDialog", "In column with species", None, QtGui.QApplication.UnicodeUTF8))
        self.auth_separate.setText(QtGui.QApplication.translate("CsvImportDialog", "In separate column:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("CsvImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Preview</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("CsvImportDialog", "Character encoding", None, QtGui.QApplication.UnicodeUTF8))

