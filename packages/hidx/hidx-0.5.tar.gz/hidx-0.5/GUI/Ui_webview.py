# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/fccoelho/Documentos/Projects_software/HIDX/GUI/webview.ui'
#
# Created: Wed Nov 23 11:23:00 2011
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_WebForm(object):
    def setupUi(self, WebForm):
        WebForm.setObjectName(_fromUtf8("WebForm"))
        WebForm.resize(631, 504)
        WebForm.setWindowTitle(QtGui.QApplication.translate("WebForm", "Web View", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(WebForm)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.webView = QtWebKit.QWebView(WebForm)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)

        self.retranslateUi(WebForm)
        QtCore.QMetaObject.connectSlotsByName(WebForm)

    def retranslateUi(self, WebForm):
        pass

from PyQt4 import QtWebKit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    WebForm = QtGui.QWidget()
    ui = Ui_WebForm()
    ui.setupUi(WebForm)
    WebForm.show()
    sys.exit(app.exec_())

