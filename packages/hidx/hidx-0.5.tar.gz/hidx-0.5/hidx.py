#!/usr/bin/env python
# -*- coding:utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        hidx.py
# Project:  HIDX
# Purpose:     High dimensional  data visualizer
#
# Author:      Flávio Codeço Coelho<fccoelho@gmail.com>
#
# Created:     2010-05-10
# Copyright:   (c) 2010 by the Author
# Licence:     GPL
#-----------------------------------------------------------------------------
__docformat__ = "restructuredtext en"


import sys
from PyQt4 import QtGui,  QtCore

#from __version__ import version
def main():
    app = QtGui.QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QtGui.QPixmap(':/splash/images/splash.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    layout = QtGui.QVBoxLayout(splash)
#    vlabel = QtGui.QLabel(version, splash)
#    layout.addWidget(vlabel)
    splash.show()
    app.processEvents()
    splash.showMessage(app.trUtf8("Loading..."))
    import time
    import pylab
    import scipy
    import sqlalchemy
    import dbf
    from GUI.main import MainWindow

    app.processEvents()

    ui = MainWindow()
    ui.show()

    splash.finish(ui)

    sys.exit(app.exec_())
    
if __name__=="__main__":
    main()
