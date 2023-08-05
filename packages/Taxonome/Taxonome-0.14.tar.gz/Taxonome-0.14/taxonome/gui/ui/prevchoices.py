# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taxonome/gui/ui/prevchoices.ui'
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

class Ui_PrevChoicesDialog(object):
    def setupUi(self, PrevChoicesDialog):
        PrevChoicesDialog.setObjectName(_fromUtf8("PrevChoicesDialog"))
        PrevChoicesDialog.resize(568, 475)
        self.verticalLayout_3 = QtGui.QVBoxLayout(PrevChoicesDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(PrevChoicesDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ambignames = QtGui.QListView(self.layoutWidget)
        self.ambignames.setObjectName(_fromUtf8("ambignames"))
        self.verticalLayout.addWidget(self.ambignames)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.forget = QtGui.QPushButton(self.layoutWidget)
        self.forget.setObjectName(_fromUtf8("forget"))
        self.horizontalLayout.addWidget(self.forget)
        self.forget_all = QtGui.QPushButton(self.layoutWidget)
        self.forget_all.setObjectName(_fromUtf8("forget_all"))
        self.horizontalLayout.addWidget(self.forget_all)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.layoutWidget1 = QtGui.QWidget(self.splitter)
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.layoutWidget1)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.chosenmatch = QtGui.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.chosenmatch.setFont(font)
        self.chosenmatch.setText(_fromUtf8(""))
        self.chosenmatch.setScaledContents(False)
        self.chosenmatch.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.chosenmatch.setObjectName(_fromUtf8("chosenmatch"))
        self.verticalLayout_2.addWidget(self.chosenmatch)
        self.label_2 = QtGui.QLabel(self.layoutWidget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.altmatches = QtGui.QListView(self.layoutWidget1)
        self.altmatches.setObjectName(_fromUtf8("altmatches"))
        self.verticalLayout_2.addWidget(self.altmatches)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.update_choice = QtGui.QPushButton(self.layoutWidget1)
        self.update_choice.setObjectName(_fromUtf8("update_choice"))
        self.horizontalLayout_2.addWidget(self.update_choice)
        self.reject_all = QtGui.QPushButton(self.layoutWidget1)
        self.reject_all.setObjectName(_fromUtf8("reject_all"))
        self.horizontalLayout_2.addWidget(self.reject_all)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3.addWidget(self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(PrevChoicesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.label_2.setBuddy(self.altmatches)

        self.retranslateUi(PrevChoicesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PrevChoicesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PrevChoicesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PrevChoicesDialog)

    def retranslateUi(self, PrevChoicesDialog):
        PrevChoicesDialog.setWindowTitle(QtGui.QApplication.translate("PrevChoicesDialog", "Stored name choices", None, QtGui.QApplication.UnicodeUTF8))
        self.forget.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Forget", None, QtGui.QApplication.UnicodeUTF8))
        self.forget_all.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Forget all", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Preferred match:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Alternatives:", None, QtGui.QApplication.UnicodeUTF8))
        self.update_choice.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Update choice", None, QtGui.QApplication.UnicodeUTF8))
        self.reject_all.setText(QtGui.QApplication.translate("PrevChoicesDialog", "Reject all", None, QtGui.QApplication.UnicodeUTF8))

