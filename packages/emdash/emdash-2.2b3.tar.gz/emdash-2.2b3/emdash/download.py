# $Id: download.py,v 1.18 2012/07/29 06:33:32 irees Exp $
import Queue
import collections
import datetime
import functools
import getpass
import glob
import operator
import optparse
import os
import re
import sys
import time

# PyQt4 imports
from PyQt4 import QtGui, QtCore, Qt

# emdash imports
import emdash.config
import emdash.emmodels
import emdash.emwizard
import emdash.emthreads
import emdash.upload
import emdash.ui


def main():
    parser = emdash.config.DBRPCOptions()
    usage = """%prog [options] [record name]"""
    parser.set_usage(usage)    

    (options, args) = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    window = BaseDownload()
    window._targets = args
    window.request_login()
    sys.exit(app.exec_())    
    
    

##############################
# Base EMDash Uploader
##############################

class BaseDownload(emdash.upload.BaseTransport):
    ui = emdash.ui.Ui_Download.Ui_Download
    worker = emdash.emthreads.DownloadThread
    headers = ["name", "filename", "record", "_status"]
    headernames = ["Binary", "Filename", "Record", "Status"]
    headerwidths = [200, 200, 100, 100]
    
    def init(self):
        self._targets = []
        self.ui.button_grid.addAction(QtGui.QAction("Browse for destination", self, triggered=self._select_target_wizard))
        self.ui.button_grid.addAction(QtGui.QAction("Manually select destination", self, triggered=self._name_target_wizard))
        self.worker.start()
        

    @QtCore.pyqtSlot()
    def begin_session(self):
        super(BaseDownload, self).begin_session()
        for target in self._targets:
            self.set_target(target)


    @QtCore.pyqtSlot(unicode)
    def set_target(self, name):
        super(BaseDownload, self).set_target(name)
        recs = emdash.config.db().rel.children(self.target, recurse=-1)
        recs = set(recs)
        recs.add(self.target)
        bdos = emdash.config.db().binary.find(record=list(recs))
        for bdo in bdos:
            bdo['_auto'] = True






if __name__ == '__main__':
    main()



__version__ = "$Revision: 1.18 $".split(":")[1][:-1].strip()
