#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# G U I n s t a l l e r
#                                 an user friendly GUI interface for PyInstaller
#                                                            (C) jpl@ozf.fr 2021
#-------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------
# from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFormLayout, QLineEdit, QCheckBox)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import platform
import os
from datetime import date
import pkg_resources

import utils
import const

# -------------------------------------------------------------------------------
# class DlgProperties
# -------------------------------------------------------------------------------
class DlgProperties(QDialog):
    # -------------------------------------------------------------------------------
    # __init__()
    # -------------------------------------------------------------------------------
    def __init__(self, title, dict, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        layout = QFormLayout(self)
        for key, value in dict.items():
            self.lblKey = QLabel(key)
            self.txtValue = QLineEdit(str(value))
            self.txtValue.setEnabled(False)
            layout.addRow(self.lblKey, self.txtValue)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self);
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)

# -------------------------------------------------------------------------------
# class DlgAddData
# -------------------------------------------------------------------------------
class DlgAddData(QDialog):
    BOTH = 64
    # -------------------------------------------------------------------------------
    # __init__()
    # -------------------------------------------------------------------------------
    def __init__(self, parent, caption, fileMode, nameFilter = "All files (*.*)"):
        super().__init__(parent)

        self.fileMode = fileMode
        self.nameFilter = nameFilter

        self.setWindowTitle(caption)
        mainLayout = QVBoxLayout(self)

        formLayout = QFormLayout(self)

        self.hLayout1 = QHBoxLayout(self)
        self.txtDataSource = QLineEdit()
        self.hLayout1.addWidget(self.txtDataSource)
        self.btnBrowse1 = QPushButton()
        icoBrowse1 = QIcon(utils.resource_path("pix/16x16/Folder3.png"))
        self.btnBrowse1.setIcon(icoBrowse1)
        self.btnBrowse1.clicked.connect(self.browseSource)
        self.hLayout1.addWidget(self.btnBrowse1)
        formLayout.addRow("Data source file or folder", self.hLayout1)

        self.hLayout2 = QHBoxLayout(self)
        self.txtDataDest = QLineEdit()
        self.hLayout2.addWidget(self.txtDataDest)
        self.btnBrowse2 = QPushButton()
        icoBrowse2 = QIcon(utils.resource_path("pix/16x16/Folder3.png"))
        self.btnBrowse2.setIcon(icoBrowse2)
        self.btnBrowse2.clicked.connect(self.browseDest)
        self.hLayout2.addWidget(self.btnBrowse2)
        formLayout.addRow("Destination", self.hLayout2)

        boxLayout = QHBoxLayout(self)
        self.btnRun = QPushButton()
        icoRun = QIcon(utils.resource_path("pix/16x16/Ok.png"))
        self.btnRun.setIcon(icoRun)
        self.btnCancel = QPushButton()
        icoCancel = QIcon(utils.resource_path("pix/16x16/Cancel.png"))
        self.btnCancel.setIcon(icoCancel)

        self.btnRun.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.close)

        boxLayout.addStretch(1)
        boxLayout.addWidget(self.btnRun)
        boxLayout.addWidget(self.btnCancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(boxLayout)

    # -------------------------------------------------------------------------------
    # browseSource()
    # -------------------------------------------------------------------------------
    def browseSource(self):
        dlg = QFileDialog(self)
        # dlg.currentChanged.connect(lambda str, dlg = dlg : self.changeSelectionMode(str, dlg))
        if self.fileMode == self.BOTH:
            dlg.currentChanged.connect(lambda str, dlg = dlg : self.changeSelectionMode(str, dlg))
        else:
            dlg.setFileMode(self.fileMode)
        dlg.setNameFilter(self.nameFilter)
        dlg.setOptions(QFileDialog.DontUseNativeDialog)
        if dlg.exec():
            for iFile in dlg.selectedFiles():
                self.txtDataSource.setText(iFile)
                self.txtDataDest.setText(os.path.split(iFile)[1])
                self.btnRun.setFocus()

    # -------------------------------------------------------------------------------
    # changeSelectionMode()
    # -------------------------------------------------------------------------------
    def changeSelectionMode(self, str, dlg):
        info = QFileInfo(str)
        if info.isFile():
            dlg.setFileMode(QFileDialog.ExistingFile)
        elif info.isDir():
            dlg.setFileMode(QFileDialog.Directory)

    # -------------------------------------------------------------------------------
    # browseDest()
    # -------------------------------------------------------------------------------
    def browseDest(self):
        dlg = QFileDialog(self)
        dlg.setFileMode(QFileDialog.Directory)
        # dlg.setNameFilter(self.nameFilter)
        dlg.setOptions(QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
        if dlg.exec():
            for iFile in dlg.selectedFiles():
                self.txtDataDest.setText(iFile)
