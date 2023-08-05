# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/fccoelho/Documentos/Projects_software/HIDX/GUI/dbserver.ui'
#
# Created: Tue Nov 22 11:50:38 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(300, 200)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(300, 200))
        Dialog.setMaximumSize(QtCore.QSize(300, 200))
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setText(QtGui.QApplication.translate("Dialog", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label)
        self.hostname = QtGui.QLineEdit(Dialog)
        self.hostname.setText(QtGui.QApplication.translate("Dialog", "localhost", None, QtGui.QApplication.UnicodeUTF8))
        self.hostname.setObjectName(_fromUtf8("hostname"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.hostname)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Db Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "User:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Database:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_5)
        self.DatabaseComboBox = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DatabaseComboBox.sizePolicy().hasHeightForWidth())
        self.DatabaseComboBox.setSizePolicy(sizePolicy)
        self.DatabaseComboBox.setDuplicatesEnabled(False)
        self.DatabaseComboBox.setObjectName(_fromUtf8("DatabaseComboBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.DatabaseComboBox)
        self.username = QtGui.QLineEdit(Dialog)
        self.username.setObjectName(_fromUtf8("username"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.username)
        self.DbComboBox = QtGui.QComboBox(Dialog)
        self.DbComboBox.setObjectName(_fromUtf8("DbComboBox"))
        self.DbComboBox.addItem(_fromUtf8(""))
        self.DbComboBox.setItemText(0, QtGui.QApplication.translate("Dialog", "MySQL", None, QtGui.QApplication.UnicodeUTF8))
        self.DbComboBox.addItem(_fromUtf8(""))
        self.DbComboBox.setItemText(1, QtGui.QApplication.translate("Dialog", "PostgreSQL", None, QtGui.QApplication.UnicodeUTF8))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.DbComboBox)
        self.passwd = QtGui.QLineEdit(Dialog)
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.passwd.setObjectName(_fromUtf8("passwd"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.passwd)
        self.connectButton = QtGui.QPushButton(Dialog)
        self.connectButton.setText(QtGui.QApplication.translate("Dialog", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.connectButton.setObjectName(_fromUtf8("connectButton"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.connectButton)
        self.connCheck = QtGui.QCheckBox(Dialog)
        self.connCheck.setEnabled(True)
        self.connCheck.setToolTip(QtGui.QApplication.translate("Dialog", "Check connection parameters are valid", None, QtGui.QApplication.UnicodeUTF8))
        self.connCheck.setWhatsThis(QtGui.QApplication.translate("Dialog", "If checked, it means that a connection with current parameters is possible.", None, QtGui.QApplication.UnicodeUTF8))
        self.connCheck.setText(QtGui.QApplication.translate("Dialog", "Check", None, QtGui.QApplication.UnicodeUTF8))
        self.connCheck.setCheckable(False)
        self.connCheck.setTristate(True)
        self.connCheck.setObjectName(_fromUtf8("connCheck"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.connCheck)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_6)
        self.portBox = QtGui.QSpinBox(Dialog)
        self.portBox.setMaximum(10000)
        self.portBox.setProperty("value", 3306)
        self.portBox.setObjectName(_fromUtf8("portBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.portBox)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

