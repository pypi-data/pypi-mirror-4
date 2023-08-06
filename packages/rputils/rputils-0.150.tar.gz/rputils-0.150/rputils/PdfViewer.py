#!/usr/bin/env python
# Written by: DGC

# python imports
from PyQt4 import QtGui, QtWebKit

# local imports
import Resources.finder

#==============================================================================
class ViewerDock(QtGui.QDockWidget):

    def __init__(self):
        super(ViewerDock, self).__init__("PDF Viewer")
        self.setWindowIcon(
            QtGui.QIcon(Resources.finder.find_image_file("Pdf.png"))
            )
        self.pdf_view = QtWebKit.QWebView()
        self.pdf_view.settings().setAttribute(
            QtWebKit.QWebSettings.PluginsEnabled, 
            True
            )
        self.setWidget(self.pdf_view)

    def set_url(self, url):
        self.pdf_view.load(url)
