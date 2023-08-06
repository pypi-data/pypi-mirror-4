# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taxonome/gui/ui/find_taxon.ui'
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

class Ui_FindSpDialog(object):
    def setupUi(self, FindSpDialog):
        FindSpDialog.setObjectName(_fromUtf8("FindSpDialog"))
        FindSpDialog.resize(380, 354)
        self.verticalLayout = QtGui.QVBoxLayout(FindSpDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label = QtGui.QLabel(FindSpDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(FindSpDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_2)
        self.service = QtGui.QComboBox(FindSpDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.service.sizePolicy().hasHeightForWidth())
        self.service.setSizePolicy(sizePolicy)
        self.service.setObjectName(_fromUtf8("service"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.service)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.taxname = QtGui.QLineEdit(FindSpDialog)
        self.taxname.setObjectName(_fromUtf8("taxname"))
        self.horizontalLayout_2.addWidget(self.taxname)
        self.search = QtGui.QPushButton(FindSpDialog)
        self.search.setObjectName(_fromUtf8("search"))
        self.horizontalLayout_2.addWidget(self.search)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.result_block = QtGui.QWidget(FindSpDialog)
        self.result_block.setEnabled(False)
        self.result_block.setObjectName(_fromUtf8("result_block"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.result_block)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.result_view = QtWebKit.QWebView(self.result_block)
        self.result_view.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.result_view.setObjectName(_fromUtf8("result_view"))
        self.verticalLayout_2.addWidget(self.result_view)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(self.result_block)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.destination_ds = QtGui.QComboBox(self.result_block)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.destination_ds.sizePolicy().hasHeightForWidth())
        self.destination_ds.setSizePolicy(sizePolicy)
        self.destination_ds.setObjectName(_fromUtf8("destination_ds"))
        self.horizontalLayout_3.addWidget(self.destination_ds)
        self.ds_add = QtGui.QPushButton(self.result_block)
        self.ds_add.setObjectName(_fromUtf8("ds_add"))
        self.horizontalLayout_3.addWidget(self.ds_add)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.result_block)
        self.buttonBox = QtGui.QDialogButtonBox(FindSpDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(FindSpDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FindSpDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FindSpDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FindSpDialog)

    def retranslateUi(self, FindSpDialog):
        FindSpDialog.setWindowTitle(QtGui.QApplication.translate("FindSpDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("FindSpDialog", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("FindSpDialog", "Service", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setText(QtGui.QApplication.translate("FindSpDialog", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("FindSpDialog", "Add to dataset:", None, QtGui.QApplication.UnicodeUTF8))
        self.ds_add.setText(QtGui.QApplication.translate("FindSpDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
