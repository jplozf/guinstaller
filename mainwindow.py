#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# G U I n s t a l l e r
#                                 an user friendly GUI interface for PyInstaller
#                                                            (C) jpl@ozf.fr 2021
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import platform
import sys
import datetime
import pickle

# These imports are project specific
import settings
import const
import pyinstall
import dialog
import utils
import QCodeEditor
import syntax

#-------------------------------------------------------------------------------
# Class MainWindow
#-------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    appDir = ""
    CurrentOS = platform.system()
    CurrentDrive = os.path.splitdrive(os.path.realpath(__file__))[0]
    CurrentDir = os.path.splitdrive(os.path.dirname(os.path.realpath(__file__)))[1]
    source_path = ""
    filename = None
    dirtyFlag = False

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent = None, mainFile = None):
        QMainWindow.__init__( self, parent )
        uic.loadUi(utils.resource_path('ui/guinstaller.ui'), self)

        self.appDir = os.path.join(os.path.expanduser("~"), const.db["APP_FOLDER"])
        if not os.path.exists(self.appDir):
            os.makedirs(self.appDir)
        pyinstall.initFormEXE(self)
        self.btnBuildEXE.clicked.connect(self.doBuildEXE)
        self.btnBuildEXE.setToolTip("Launch the build process")
        self.btnBuildEXE.setEnabled(False)
        self.btnGenSpec.clicked.connect(self.doGenSpec)
        self.btnGenSpec.setToolTip("Generate the spec file only")
        self.btnGenSpec.setEnabled(False)
        self.lblRCBuild.setFont(QFont('Courier', 10))
        self.lblTimeBuild.setFont(QFont('Courier', 10))
        self.btnBrowseMainFile.clicked.connect(lambda: pyinstall.browseMainFile(self))
        self.btnBrowseMainFile.setToolTip("Browse to get the main script file of project")
        self.lblRunEXE.setText(const.db['PROGRAM_NONE'])
        self.lblRunEXE.setToolTip("Generated program file name")
        self.btnRunEXE.clicked.connect(lambda: pyinstall.runEXE(self))
        self.btnRunEXE.setToolTip("Run the generated executable file")
        self.txtParamsEXE.returnPressed.connect(lambda: pyinstall.runEXE(self))
        self.txtParamsEXE.setToolTip("Parameters for running the generated program")
        self.lblTimeBuild.setToolTip("Running time for the previous operation")
        self.lblLEDBuild.setToolTip("Running status")
        self.lblRCBuild.setToolTip("Return code for the previous operation")

        self.btnClearOutput.clicked.connect(self.doClearOutput)
        self.btnClearOutput.setToolTip("Clear the output")
        self.btnCopyOutput.clicked.connect(self.doCopyOutput)
        self.btnCopyOutput.setToolTip("Copy the output to clipboard")
        self.btnShowDoc.clicked.connect(self.doShowDoc)
        self.btnShowDoc.setToolTip("Open the PyInstaller documentation")
        self.btnOpenFolder.clicked.connect(self.doOpenFolder)
        self.btnOpenFolder.setToolTip("Open the target folder")
        self.btnOpenFolder.setEnabled(False)
        self.btnRunEXE.setEnabled(False)
        self.btnBreakEXE.setEnabled(False)
        self.btnBreakEXE.setToolTip("Try to stop and kill the running generated executable file")

        self.lstAddData.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstAddData.customContextMenuRequested.connect(lambda position, w = self.lstAddData : self.onListContext(position, w))

        self.lstAddBinary.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstAddBinary.customContextMenuRequested.connect(lambda position, w = self.lstAddBinary : self.onListContext(position, w))

        self.lstPaths.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstPaths.customContextMenuRequested.connect(lambda position, w = self.lstPaths : self.onListContext(position, w))

        self.lstHiddenImport.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstHiddenImport.customContextMenuRequested.connect(lambda position, w = self.lstHiddenImport : self.onListContext(position, w))

        self.lstAdditionalHooksDir.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstAdditionalHooksDir.customContextMenuRequested.connect(lambda position, w = self.lstAdditionalHooksDir : self.onListContext(position, w))

        self.lstRuntimeHook.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstRuntimeHook.customContextMenuRequested.connect(lambda position, w = self.lstRuntimeHook : self.onListContext(position, w))

        self.lstExcludeModule.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lstExcludeModule.customContextMenuRequested.connect(lambda position, w = self.lstExcludeModule : self.onListContext(position, w))

        css = 'font: %dpt "%s"; color: %s; background-color: %s;' % (settings.db['OUTPUT_STYLE_FONT_SIZE'],settings.db['OUTPUT_STYLE_FONT_NAME'],settings.db['OUTPUT_STYLE_COLOR'],settings.db['OUTPUT_STYLE_COLOR_BACKGROUND'])
        self.txtBuildOutput.setStyleSheet(css)
        self.txtBuildOutput.setReadOnly(True)

        self.txtSpecFile = QCodeEditor.QCodeEditor(self)
        self.lytEditor.addWidget(self.txtSpecFile)
        css = 'font: %dpt "%s"; background-color: %s;' % (settings.db['EDITOR_FONT_SIZE'],settings.db['EDITOR_FONT'],settings.db['EDITOR_COLOR_BACKGROUND'])
        self.txtSpecFile.setStyleSheet(css)
        self.txtSpecFile.textChanged.connect(self.changedText)
        self.txtSpecFile.selectionChanged.connect(self.handleSelectionChanged)
        self.txtSpecFile.cursorPositionChanged.connect(self.cursorPosition)
        self.txtSpecFile.highlight = syntax.PythonHighlighter(self.txtSpecFile.document())
        self.btnSaveSpecFile.clicked.connect(self.saveFile)

        self.tabSettings = settings.TabSettings(self)
        self.tbwBuild.addTab(self.tabSettings, QIcon(QPixmap(utils.resource_path("pix/16x16/Gear.png"))), "")

        self.restoreSettings()

        self.setEnabledGUI(False)
        self.showMessage("Welcome to %s version %s" % (const.db['APPLICATION_NAME'], const.db['VERSION']))
        if mainFile is not None:
            pyinstall.setMainFile(self, mainFile)

#-------------------------------------------------------------------------------
# cursorPosition()
#-------------------------------------------------------------------------------
    def cursorPosition(self):
        line = self.txtSpecFile.textCursor().blockNumber() + 1
        col = self.txtSpecFile.textCursor().columnNumber() + 1
        self.lblRowCol.setText("Line %d, Column %d" % (line, col))

#-------------------------------------------------------------------------------
# handleSelectionChanged()
#-------------------------------------------------------------------------------
    def handleSelectionChanged(self):
        myCursor = self.txtSpecFile.textCursor()
        text = myCursor.selectedText()
        # myCursor.clearSelection()
        # self.txtEditor.setTextCursor(myCursor)
        # self.txtGotoSearch.setText(text)

#-------------------------------------------------------------------------------
# changedText()
#-------------------------------------------------------------------------------
    def changedText(self):
        self.dirtyFlag = True
        self.lblModified.setText("*modified*")
        self.displaySize()

#-------------------------------------------------------------------------------
# displaySize()
#-------------------------------------------------------------------------------
    def displaySize(self):
        # self.lblSize.setText(str(sys.getsizeof(self.txtEditor.toPlainText())))
        self.lblSize.setText("%d (%s)" % (len(self.txtSpecFile.toPlainText()), utils.getHumanSize(len(self.txtSpecFile.toPlainText()))))

#-------------------------------------------------------------------------------
# saveFile()
#-------------------------------------------------------------------------------
    def saveFile(self):
        # Convert tabs to spaces before saving file
        s = self.txtSpecFile.toPlainText()
        s = s.replace("\t", settings.db['EDITOR_TAB_SPACES'] * ' ')
        self.txtSpecFile.setPlainText(s)

        if self.filename is not None:
            with open(self.filename, "w") as pyFile:
                pyFile.write(self.txtSpecFile.toPlainText())
                self.dirtyFlag = False
                self.lblModified.setText("")
            self.showMessage("Saving %s file" % (self.filename))
        else:
            filename = QFileDialog.getSaveFileName(self, 'Save file', './', "Spec file (*.spec);;All files (*.*)")[0]
            if filename != "":
                self.filename = filename
                shortname = os.path.basename(self.filename)
                with open(self.filename, "w") as pyFile:
                    pyFile.write(self.txtSpecFile.toPlainText())
                    self.dirtyFlag = False
                    self.lblModified.setText("")
                self.txtMainFile.setText(self.filename)
                self.showMessage("Saving %s file" % (self.filename))
            else:
                self.showMessage("Spec file has no name")

#-------------------------------------------------------------------------------
# onListContext()
#-------------------------------------------------------------------------------
    def onListContext(self, position, widget):
        menu = QMenu("Menu", self)
        deleteRowAction = menu.addAction("Delete one row")
        deleteAllAction = menu.addAction("Delete all rows")
        action = menu.exec_(widget.mapToGlobal(position))
        if action == deleteRowAction:
            if widget.count() > 0:
                self.showMessage("Delete row in list")
                widget.takeItem(widget.currentRow())
            else:
                self.showMessage("Nothing to delete in this list")
        elif action == deleteAllAction:
            if widget.count() > 0:
                self.showMessage("List cleared")
                widget.clear()
            else:
                self.showMessage("List is already empty")

#-------------------------------------------------------------------------------
# doBuildEXE()
#-------------------------------------------------------------------------------
    def doBuildEXE(self):
        pyinstall.buildEXE(self)

#-------------------------------------------------------------------------------
# doGenSpec()
#-------------------------------------------------------------------------------
    def doGenSpec(self):
        pyinstall.genSpec(self)

#-------------------------------------------------------------------------------
# __del__()
#-------------------------------------------------------------------------------
    def __del__(self):
        settings.db.close()
        self.ui = None

#-------------------------------------------------------------------------------
# restoreSettings()
#-------------------------------------------------------------------------------
    def restoreSettings(self):
        #
        regSettings = QSettings()
        size = regSettings.value('MainWindow/Size', QSize(600,500))
        try:
            self.resize(size)
        except:
            self.resize(size.toSize())
        position = regSettings.value('MainWindow/Position', QPoint(0,0))
        try:
            self.move(position)
        except:
            self.move(position.toPoint())
        try:
            self.restoreGeometry(regSettings.value("MainWindow/WindowGeometry", b"", type='QByteArray'))
        except:
            pass
        try:
            self.restoreState(regSettings.value("MainWindow/WindowState", b"", type='QByteArray'))
        except:
            pass
        try:
            # mainSplitter
            mainSplitterSettings = regSettings.value("MainWindow/mainSplitterSettings")
            if mainSplitterSettings:
                try:
                    self.mainSplitter.restoreState(mainSplitterSettings)
                except:
                    try:
                        self.mainSplitter.restoreState(mainSplitterSettings.toPyObject())
                    except:
                        pass
            # consoleSplitter
            consoleSplitterSettings = regSettings.value("MainWindow/consoleSplitterSettings")
            if consoleSplitterSettings:
                try:
                    self.tabConsole.consoleSplitter.restoreState(consoleSplitterSettings)
                except:
                    try:
                        self.tabConsole.consoleSplitter.restoreState(consoleSplitterSettings.toPyObject())
                    except:
                        pass
        except:
            pass


#-------------------------------------------------------------------------------
# backupSettings()
#-------------------------------------------------------------------------------
    def backupSettings(self):
        #
        regSettings = QSettings()
        regSettings.setValue("MainWindow/Size", self.size())
        regSettings.setValue("MainWindow/Position", self.pos())
        regSettings.setValue("MainWindow/WindowState", self.saveState())
        regSettings.setValue("MainWindow/WindowGeometry", self.saveGeometry())
        # mainSplitter
        mainSplitterSettings = self.mainSplitter.saveState()
        if mainSplitterSettings:
            regSettings.setValue("MainWindow/mainSplitterSettings", self.mainSplitter.saveState())
        # consoleSplitter
        try:
            consoleSplitterSettings = self.tabConsole.consoleSplitter.saveState()
            if consoleSplitterSettings:
                regSettings.setValue("MainWindow/consoleSplitterSettings", self.tabConsole.consoleSplitter.saveState())
        except:
            pass

        settings.db.sync()
        self.showMessage("Settings saved")

#-------------------------------------------------------------------------------
# showMessage()
#-------------------------------------------------------------------------------
    def showMessage(self, msg):
        self.statusBar.showMessage(msg, settings.db['APP_TIMER_STATUS'])
        self.outputMessage(msg)

#-------------------------------------------------------------------------------
# outputMessage()
#-------------------------------------------------------------------------------
    def outputMessage(self, msg):
        now = datetime.datetime.now()
        self.txtBuildOutput.appendPlainText(now.strftime(settings.db['OUTPUT_TIMESTAMP']) + msg)
        self.txtBuildOutput.moveCursor(QTextCursor.End)

#-------------------------------------------------------------------------------
# closeEvent()
#-------------------------------------------------------------------------------
    def closeEvent(self, event):
        if settings.db['APP_EXIT_CONFIRM'] == True:
            result1 = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to quit ?", QMessageBox.Yes | QMessageBox.No)
            if result1 == QMessageBox.Yes:
                # self.doClose()
                if self.dirtyFlag == True:
                    result2 = QMessageBox.question(self, "File has been modified", "The spec file has been modified.\n Would you like to save it ?", QMessageBox.Yes | QMessageBox.No)
                    if result2 == QMessageBox.Yes:
                        self.saveFile()
                self.doClose()
                event.accept()
            else:
                self.showMessage("Welcome back")
                event.ignore()
        else:
            self.doClose()
            event.accept()

#-------------------------------------------------------------------------------
# doClose()
#-------------------------------------------------------------------------------
    def doClose(self):
        self.backupSettings()

#-------------------------------------------------------------------------------
# doClearOutput()
#-------------------------------------------------------------------------------
    def doClearOutput(self):
        self.txtBuildOutput.setPlainText("")

#-------------------------------------------------------------------------------
# doCopyOutput()
#-------------------------------------------------------------------------------
    def doCopyOutput(self):
        qc = QApplication.clipboard()
        qc.setText(self.txtBuildOutput.toPlainText(), mode=qc.Clipboard)
        self.showMessage("Output copied to clipboard")

#-------------------------------------------------------------------------------
# doShowDoc()
#-------------------------------------------------------------------------------
    def doShowDoc(self):
        self.showMessage("Opening PyInstaller Documentation")
        utils.openFileWithDefaultViewer(utils.resource_path("dox/pyinstaller.pdf"))

#-------------------------------------------------------------------------------
# doOpenFolder()
#-------------------------------------------------------------------------------
    def doOpenFolder(self):
        self.showMessage("Opening target folder")
        utils.openFileWithDefaultViewer(os.path.dirname(self.lblRunEXE.text()))

#-------------------------------------------------------------------------------
# setEnabledGUI()
#-------------------------------------------------------------------------------
    def setEnabledGUI(self, flag):
        self.lblDistPath.setEnabled(flag)
        self.txtDistPath.setEnabled(flag)
        self.lblWorkPath.setEnabled(flag)
        self.txtWorkPath.setEnabled(flag)
        self.lblUPXDir.setEnabled(flag)
        self.txtUPXDir.setEnabled(flag)
        self.lblAscii.setEnabled(flag)
        self.chkAscii.setEnabled(flag)
        self.lblClean.setEnabled(flag)
        self.chkClean.setEnabled(flag)
        self.lblNoConfirm.setEnabled(flag)
        self.chkNoConfirm.setEnabled(flag)
        self.lblLogLevel.setEnabled(flag)
        self.cbxLogLevel.setEnabled(flag)
        self.lblOneDir.setEnabled(flag)
        self.chkOneDir.setEnabled(flag)
        self.lblOneFile.setEnabled(flag)
        self.chkOneFile.setEnabled(flag)
        self.lblSpecPath.setEnabled(flag)
        self.txtSpecPath.setEnabled(flag)
        self.lblName.setEnabled(flag)
        self.txtName.setEnabled(flag)
        self.lblAddData.setEnabled(flag)
        self.lstAddData.setEnabled(flag)
        self.lblAddBinary.setEnabled(flag)
        self.lstAddBinary.setEnabled(flag)
        self.lblPaths.setEnabled(flag)
        self.lstPaths.setEnabled(flag)
        self.lblHiddenImport.setEnabled(flag)
        self.lstHiddenImport.setEnabled(flag)
        self.lblCollectSubmodules.setEnabled(flag)
        self.lstCollectSubmodules.setEnabled(flag)
        self.lblCollectData.setEnabled(flag)
        self.lstCollectData.setEnabled(flag)
        self.lblCollectBinaries.setEnabled(flag)
        self.lstCollectBinaries.setEnabled(flag)
        self.lblCollectAll.setEnabled(flag)
        self.lstCollectAll.setEnabled(flag)
        self.lblCopyMetadata.setEnabled(flag)
        self.lstCopyMetadata.setEnabled(flag)
        self.lblRecursiveCopyMetadata.setEnabled(flag)
        self.lstRecursiveCopyMetadata.setEnabled(flag)
        self.lblAdditionalHooksDir.setEnabled(flag)
        self.lstAdditionalHooksDir.setEnabled(flag)
        self.lblRuntimeHook.setEnabled(flag)
        self.lstRuntimeHook.setEnabled(flag)
        self.lblExcludeModule.setEnabled(flag)
        self.lstExcludeModule.setEnabled(flag)
        self.lblKey.setEnabled(flag)
        self.txtKey.setEnabled(flag)
        self.lblDebug.setEnabled(flag)
        self.cbxDebug.setEnabled(flag)
        self.lblStrip.setEnabled(flag)
        self.chkStrip.setEnabled(flag)
        self.lblNoUPX.setEnabled(flag)
        self.chkNoUPX.setEnabled(flag)
        self.lblRuntimeTmpDir.setEnabled(flag)
        self.txtRuntimeTmpDir.setEnabled(flag)
        self.lblBootloaderIgnoreSignals.setEnabled(flag)
        self.chkBootloaderIgnoreSignals.setEnabled(flag)
        self.txtExtraOptions.setEnabled(flag)

        self.lblConsole.setEnabled(flag)
        self.chkConsole.setEnabled(flag)
        self.lblWindowed.setEnabled(flag)
        self.chkWindowed.setEnabled(flag)
        self.lblIcon.setEnabled(flag)
        self.txtIcon.setEnabled(flag)
        self.lblDisableWindowedTraceback.setEnabled(flag)
        self.chkDisableWindowedTraceback.setEnabled(flag)

        self.lblVersionFile.setEnabled(flag)
        self.txtVersionFile.setEnabled(flag)
        self.lblManifest.setEnabled(flag)
        self.txtManifest.setEnabled(flag)
        self.lblResource.setEnabled(flag)
        self.lstResource.setEnabled(flag)
        self.lblUACAdmin.setEnabled(flag)
        self.chkUACAdmin.setEnabled(flag)
        self.lblUACUIAccess.setEnabled(flag)
        self.chkUACUIAccess.setEnabled(flag)
        self.lblWinPrivateAssemblies.setEnabled(flag)
        self.chkWinPrivateAssemblies.setEnabled(flag)
        self.lblWinNoPreferRedirects.setEnabled(flag)
        self.chkWinNoPreferRedirects.setEnabled(flag)

        self.lblOSXBundleIdentifier.setEnabled(flag)
        self.txtOSXBundleIdentifier.setEnabled(flag)
        self.lblTargetArchitecture.setEnabled(flag)
        self.cbxTargetArchitecture.setEnabled(flag)
        self.lblCodesignIdentity.setEnabled(flag)
        self.txtCodesignIdentity.setEnabled(flag)
        self.lblOSXEntitlementsFile.setEnabled(flag)
        self.txtOSXEntitlementsFile.setEnabled(flag)
