# -*- coding: utf-8 -*-

"""
Module implementing WebForm.
"""

from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSignature

from Ui_webview import Ui_WebForm

class WebForm(QWidget, Ui_WebForm):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QWidget.__init__(self, parent)
        self.setupUi(self)
    
    @pyqtSignature("")
    def on_webView_loadStarted(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

