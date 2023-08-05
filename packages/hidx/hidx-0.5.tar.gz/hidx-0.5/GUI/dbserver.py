# -*- coding: utf-8 -*-
"""
Module implementing class OpenDb.

This class is the Dialog for opening connections with relational with databases


"""

from PyQt4.QtGui import QDialog,  QMessageBox
from PyQt4.QtCore import pyqtSignature

from Ui_dbserver import Ui_Dialog

from sqlalchemy.ext.sqlsoup import SqlSoup


class OpenDb(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.dbs = []
        self.setupUi(self)
        if self.DbComboBox.currentIndex() == 0:
            self.portBox.setValue(3306)
        elif self.DbComboBox.currentIndex() == 1:
            self.portBox.setValue(5432)
        self.fill_gui_from_config()
    
    def fill_gui_from_config(self):
        self.username.setText(self.parent.config.get('Connections', 'username'))
        self.passwd.setText(self.parent.config.get('Connections', 'passwd'))
        self.hostname.setText(self.parent.config.get('Connections', 'host'))
        self.portBox.setValue(int(self.parent.config.get('Connections', 'port')))
        if self.parent.config.get('Connections', 'server') == 'mysql':
            self.DbComboBox.setCurrentIndex(0)
        else:
            self.DbComboBox.setCurrentIndex(1)
            
    def test_connection(self):
        """
        Test if a connection is possible with current parameters
        """
        try:
            if self.DbComboBox.currentIndex() == 0:
                server = 'mysql'
                db = SqlSoup('mysql://%s:%s@%s:%s'%(self.username.text(), self.passwd.text(), self.hostname.text(),self.portBox.value()))
                dbs = db.bind.execute("show databases;").fetchall()
            elif self.DbComboBox.currentIndex() == 1:
                server = 'postgresql'
                db = SqlSoup('postgresql://%s:%s@%s:%s'%(self.username.text(), self.passwd.text(), self.hostname.text(),self.portBox.value()))
                dbs = db.bind.execute("show databases;").fetchall()
            while self.DatabaseComboBox.count() != 0:
                self.DatabaseComboBox.removeItem(0)
            self.dbs = [i[0] for i in dbs]
            self.DatabaseComboBox.addItems(self.dbs)
        except:
            print "Erro de conexao"
            return 1
        self.parent.save_prefs([('Connections','server', server), 
                                ('Connections','username', str(self.username.text())), 
                                ('Connections','passwd', str(self.passwd.text())), 
                                ('Connections','host', str(self.hostname.text())), 
                                ('Connections','port', str(self.portBox.value()))
                                ])


    @pyqtSignature("")
    def on_hostname_editingFinished(self):
        """
        Slot documentation goes here.
        """
        if self.test_connection():
            self.connCheck.setCheckState(2)
        else:
            self.connCheck.setCheckState(0)
    
    @pyqtSignature("")
    def on_username_editingFinished(self):
        """
        Slot documentation goes here.
        """
        if self.test_connection():
            self.connCheck.setCheckState(2)
        else:
            self.connCheck.setCheckState(0)
    
    @pyqtSignature("")
    def on_passwd_editingFinished(self):
        """
        Slot documentation goes here.
        """
        if self.test_connection():
            self.connCheck.setCheckState(2)
        else:
            self.connCheck.setCheckState(0)
    
    @pyqtSignature("")
    def on_connectButton_released(self):
        """
        Slot documentation goes here.
        """
        if not self.test_connection:
            return
        if self.DbComboBox.currentIndex() == 0:
            try:
                self.parent.open_mysql(str(self.username.text()), self.passwd.text(), self.hostname.text(),str(self.DatabaseComboBox.currentText()),self.portBox.value())
            except:
                QMessageBox.information(None,
                    self.trUtf8("Connection Failed"),
                    self.trUtf8("""Connection to database Failed.
Please check connection parameters."""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Ok))

        self.close()
    
    @pyqtSignature("QString")
    def on_DatabaseComboBox_textChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if self.test_connection():
            self.connCheck.setCheckState(2)
        else:
            self.connCheck.setCheckState(0)
    
    @pyqtSignature("QString")
    def on_DbComboBox_textChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if self.test_connection():
            self.connCheck.setCheckState(2)
        else:
            self.connCheck.setCheckState(0)
