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
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import shutil
import os
import time
import datetime
from subprocess import Popen, PIPE
from importlib import util
import tempfile
from os.path import splitext

import const
import utils
import dialog
import shrealding
import settings

MODE_RUN = 0
MODE_BUILD = 1
GEN_EXE = 0
GEN_SPEC = 1

#-------------------------------------------------------------------------------
# Globals Vars
#-------------------------------------------------------------------------------
name_base = None
name_EXE = None
dist_path = None
source_path = None
mode = None
gen = None
time1 = None
tCmd = None

#-------------------------------------------------------------------------------
# initFormEXE()
#-------------------------------------------------------------------------------
def initFormEXE(mw):
    # General options
    mw.lblNoConfirm.setToolTip("Replace output directory (default: SPECPATH/dist/SPECNAME) without asking for confirmation")
    mw.lblAscii.setToolTip("Do not include unicode encoding support (default: included if available)")
    mw.lblClean.setToolTip("Clean PyInstaller cache and remove temporary files before building")
    mw.lblName.setToolTip("Name to assign to the bundled app and spec file (default: first script’s basename)")
    mw.lblDebug.setToolTip("Provide assistance with debugging a frozen application. This argument may be provided multiple times to select several of the following options. - all: All three of the following options. - imports: specify the -v option to the underlying Python interpreter, causing it to print a message each time a module is initialized, showing the place(filename or built-in module) from which it is loaded. See https://docs.python.org/3/using/cmdline.html#id4. -bootloader: tell the bootloader to issue progress messages while initializing and starting the bundled app. Used to diagnose problems with missing imports. - noarchive: instead of storing all frozen Python source files as an archive inside the resulting executable, store them as files in the resulting output directory.")
    mw.lblKey.setToolTip("The key used to encrypt Python bytecode")
    mw.lblStrip.setToolTip("Apply a symbol-table strip to the executable and shared libs (not recommended for Windows)")
    mw.lblNoUPX.setToolTip("Do not use UPX even if it is available (works differently between Windows and *nix)")
    mw.lblBootloaderIgnoreSignals.setToolTip("Tell the bootloader to ignore signals rather than forwarding them to the child process. Useful in situations where e.g. a supervisor process signals both the bootloader and child (e.g. via a process group) to avoid signalling the child twice")

    mw.lblLogLevel.setToolTip("Amount of detail in build-time console messages. LEVEL may be one of TRACE, DEBUG, INFO, WARN,ERROR, CRITICAL (default: INFO)")
    mw.cbxLogLevel.addItem("TRACE")
    mw.cbxLogLevel.addItem("DEBUG")
    mw.cbxLogLevel.addItem("INFO")
    mw.cbxLogLevel.addItem("WARN")
    mw.cbxLogLevel.addItem("ERROR")
    mw.cbxLogLevel.addItem("CRITICAL")
    mw.cbxLogLevel.setCurrentIndex(2)       # INFO default

    mw.lblOneDir.setToolTip("Create a one-folder bundle containing an executable (default)")
    mw.lblOneFile.setToolTip("Create a one-file bundled executable")
    mw.chkOneDir.setChecked(True)

    mw.cbxDebug.addItem("none")
    mw.cbxDebug.addItem("all")
    mw.cbxDebug.addItem("imports")
    mw.cbxDebug.addItem("bootloader")
    mw.cbxDebug.addItem("noarchive")
    mw.cbxDebug.addItem("imports, bootloader")
    mw.cbxDebug.addItem("imports, noarchive")
    mw.cbxDebug.addItem("bootloader, noarchive")
    mw.cbxDebug.setCurrentIndex(0)          # NONE default

    mw.lblDistPath.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblDistPath.mousePressEvent = lambda event, widget=mw.txtDistPath : doClickForPath(event, widget)
    mw.lblDistPath.setToolTip("Where to put the bundled app (default: ./dist)")

    mw.lblWorkPath.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblWorkPath.mousePressEvent = lambda event, widget=mw.txtWorkPath : doClickForPath(event, widget)
    mw.lblWorkPath.setToolTip("Where to put all the temporary work files, .log, .pyz and etc. (default: ./build)")

    mw.lblUPXDir.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblUPXDir.mousePressEvent = lambda event, widget=mw.txtUPXDir : doClickForPath(event, widget)
    mw.lblUPXDir.setToolTip("Path to UPX utility (default: search the execution path)")

    mw.lblSpecPath.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblSpecPath.mousePressEvent = lambda event, widget=mw.txtSpecPath : doClickForPath(event, widget)
    mw.lblSpecPath.setToolTip("Folder to store the generated spec file (default: current directory)")

    mw.lblAddData.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblAddData.mousePressEvent = lambda event, mw=mw : doClickForAddSRCDST(event, mw)
    mw.lblAddData.setToolTip("Additional non-binary files or folders to be added to the executable. The path separator is platform specific, os.pathsep (which is ; on Windows and : on most unix systems) is used. This option can be used multiple times")

    mw.lblAddBinary.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblAddBinary.mousePressEvent = lambda event, mw=mw : doClickForAddBinary(event, mw)
    mw.lblAddBinary.setToolTip("Additional binary files to be added to the executable. See the --add-data option for more details. This option can be used multiple times")

    mw.lblPaths.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblPaths.mousePressEvent = lambda event, widget=mw.lstPaths : doClickForPath(event, widget)
    mw.lblPaths.setToolTip("A path to search for imports (like using PYTHONPATH). Multiple paths are allowed, separated by ‘:’, or use this option multiple times")

    mw.lblHiddenImport.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblHiddenImport.mousePressEvent = lambda event, widget=mw.lstHiddenImport : doClickForModule(event, widget)
    mw.lblHiddenImport.setToolTip("Name an import not visible in the code of the script(s). This option can be used multiple times")

    mw.lblCollectSubmodules.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblCollectSubmodules.mousePressEvent = lambda event, widget=mw.lstCollectSubmodules : doClickForModule(event, widget)
    mw.lblCollectSubmodules.setToolTip("Collect all submodules from the specified package or module. This option can be used multiple times")

    mw.lblCollectData.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblCollectData.mousePressEvent = lambda event, widget=mw.lstCollectData : doClickForModule(event, widget)
    mw.lblCollectData.setToolTip("Collect all data from the specified package or module. This option can be used multiple times")

    mw.lblCollectBinaries.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblCollectBinaries.mousePressEvent = lambda event, widget=mw.lstCollectBinaries : doClickForModule(event, widget)
    mw.lblCollectBinaries.setToolTip("Collect all binaries from the specified package or module. This option can be used multiple times")

    mw.lblCollectAll.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblCollectAll.mousePressEvent = lambda event, widget=mw.lstCollectAll : doClickForModule(event, widget)
    mw.lblCollectAll.setToolTip("Collect all submodules, data files, and binaries from the specified package or module. This option can be usedmultiple times")

    mw.lblCopyMetadata.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblCopyMetadata.mousePressEvent = lambda event, widget=mw.lstCopyMetadata : doClickForModule(event, widget)
    mw.lblCopyMetadata.setToolTip("Copy metadata for the specified package. This option can be used multiple times")

    mw.lblRecursiveCopyMetadata.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblRecursiveCopyMetadata.mousePressEvent = lambda event, widget=mw.lstRecursiveCopyMetadata : doClickForModule(event, widget)
    mw.lblRecursiveCopyMetadata.setToolTip("Copy metadata for the specified package and all its dependencies. This option can be used multiple times")

    mw.lblAdditionalHooksDir.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblAdditionalHooksDir.mousePressEvent = lambda event, widget=mw.lstAdditionalHooksDir : doClickForPath(event, widget)
    mw.lblAdditionalHooksDir.setToolTip("An additional path to search for hooks. This option can be used multiple times")

    mw.lblRuntimeHook.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblRuntimeHook.mousePressEvent = lambda event, widget=mw.lstRuntimeHook : doClickForModule(event, widget)
    mw.lblRuntimeHook.setToolTip("Path to a custom runtime hook file. A runtime hook is code that is bundled with the executable and is executed before any other code or module to set up special features of the runtime environment. This option can be used multiple times")

    mw.lblExcludeModule.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblExcludeModule.mousePressEvent = lambda event, widget=mw.lstExcludeModule : doClickForModule(event, widget)
    mw.lblExcludeModule.setToolTip("Optional module or package (the Python name, not the path name) that will be ignored (as though it was not found). This option can be used multiple times")

    mw.lblRuntimeTmpDir.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblRuntimeTmpDir.mousePressEvent = lambda event, widget=mw.txtRuntimeTmpDir : doClickForPath(event, widget)
    mw.lblRuntimeTmpDir.setToolTip("Where to extract libraries and support files in onefile-mode. If this option is given, the bootloader will ignore any temp-folder location defined by the run-time OS. The _MEIxxxxxx-folder will be created here. Please use this option only if you know what you are doing")


    # Windows and Mac OS X options
    mw.lblConsole.setToolTip("Open a console window for standard i/o (default). On Windows this option will have no effect if the first script is a ‘.pyw’ file")
    mw.lblWindowed.setToolTip("Windows and Mac OS X: do not provide a console window for standard i/o. On Mac OS X this also triggers building an OS X .app bundle. On Windows this option will be set if the first script is a ‘.pyw’ file. This option is ignored in *NIX systems")

    mw.lblIcon.setFrameStyle(QFrame.Panel | QFrame.Raised)
    # mw.txtIcon.setText("NONE")
    mw.lblIcon.mousePressEvent = lambda event, filter="Icon files (*.ico *.icns *.exe);;All files (*.*)", widget=mw.txtIcon : doClickForFile(event, filter, widget)
    mw.lblIcon.setToolTip("FILE.ico: apply that icon to a Windows executable. FILE.exe,ID, extract the icon with ID from an exe. FILE.icns:apply the icon to the .app bundle on Mac OS X. Use “NONE” to not apply any icon, thereby making the OS to show some default (default: apply PyInstaller’s icon)")
    mw.lblDisableWindowedTraceback.setToolTip("Disable traceback dump of unhandled exception in windowed (noconsole) mode (Windows and macOS only), and instead display a message that this feature is disabled")

    # Windows specific options
    mw.lblVersionFile.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblVersionFile.mousePressEvent = lambda event, filter="All files (*.*)", widget=mw.txtVersionFile : doClickForFile(event, filter, widget)
    mw.lblVersionFile.setToolTip("add a version resource from FILE to the exe")

    mw.lblManifest.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblManifest.mousePressEvent = lambda event, filter="XML files (*.xml);;All files (*.*)", widget=mw.txtManifest : doClickForFile(event, filter, widget)
    mw.lblManifest.setToolTip("add manifest FILE or XML to the exe")

    mw.lblResource.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblResource.mousePressEvent = lambda event, filter="EXE files (*.exe *.dll);;All files (*.*)", widget=mw.lstResource : doClickForFile(event, filter, widget)
    mw.lblResource.setToolTip("Add or update a resource to a Windows executable. The RESOURCE is one to four items,FILE[,TYPE[,NAME[,LANGUAGE]]]. FILE can be a data file or an exe/dll. For data files, at least TYPE and NAME must be specified. LANGUAGE defaults to 0 or may be specified as wildcard * to update all resources of the given TYPE and NAME. For exe/dll files, all resources from FILE will be added/updated to the final executable if TYPE, NAME and LANGUAGE are omitted or specified as wildcard *. This option can be used multiple times")

    mw.lblUACAdmin.setToolTip("Using this option creates a Manifest which will request elevation upon application restart")
    mw.lblUACUIAccess.setToolTip("Using this option allows an elevated application to work with Remote Desktop")
    mw.lblWinPrivateAssemblies.setToolTip("Any Shared Assemblies bundled into the application will be changed into Private Assemblies. This means the exact versions of these assemblies will always be used, and any newer versions installed on user machines at the system level will be ignored")
    mw.lblWinNoPreferRedirects.setToolTip("While searching for Shared or Private Assemblies to bundle into the application, PyInstaller will prefer not to follow policies that redirect to newer versions, and will try to bundle the exact versions of the assembly")

    # Mac OS X specific options
    mw.lblOSXBundleIdentifier.setToolTip("Mac OS X .app bundle identifier is used as the default unique program name for code signing purposes. The usual form is a hierarchical name in reverse DNS notation. For example: com.mycompany.department.appname (default: first script’s basename)")

    mw.lblTargetArchitecture.setToolTip("Target architecture (macOS only; valid values: x86_64, arm64, universal2). Enables switching between universal2 and single-arch version of frozen application (provided python installation supports the target architecture).If not target architecture is not specified, the current running architecture is targeted")
    mw.cbxTargetArchitecture.addItem("current")
    mw.cbxTargetArchitecture.addItem("x86_64")
    mw.cbxTargetArchitecture.addItem("arm64")
    mw.cbxTargetArchitecture.addItem("universal2")
    mw.cbxTargetArchitecture.setCurrentIndex(0)          # current default

    mw.lblCodesignIdentity.setToolTip("Code signing identity (macOS only). Use the provided identity to sign collected binaries and generated executable. If signing identity is not provided, ad-hoc signing is performed instead")

    mw.lblOSXEntitlementsFile.setFrameStyle(QFrame.Panel | QFrame.Raised)
    mw.lblOSXEntitlementsFile.mousePressEvent = lambda event, filter="All files (*.*)", widget=mw.txtOSXEntitlementsFile : doClickForFile(event, filter, widget)
    mw.lblOSXEntitlementsFile.setToolTip("Entitlements file to use when code-signing the collected binaries (macOS only)")

#-------------------------------------------------------------------------------
# doClickForPath()
#-------------------------------------------------------------------------------
def doClickForPath(event, widget):
    path = QFileDialog.getExistingDirectory(widget, "Open a folder", ".", options = QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
    if path:
        if isinstance(widget, QListWidget):
            widget.addItem(path)
        else:
            widget.setText(path)

#-------------------------------------------------------------------------------
# doClickForModule()
#-------------------------------------------------------------------------------
def doClickForModule(event, widget):
    module = QFileDialog.getOpenFileName(widget, "Open a module", ".", "Python sources (*.py *.pyw);;All files (*.*)", options = QFileDialog.DontUseNativeDialog)
    if module:
        if isinstance(widget, QListWidget):
            widget.addItem(module[0])
        else:
            widget.setText(module[0])

#-------------------------------------------------------------------------------
# doClickForModule()
#-------------------------------------------------------------------------------
def doClickForFile(event, filter, widget):
    module = QFileDialog.getOpenFileName(widget, "Open a file", ".", filter, options = QFileDialog.DontUseNativeDialog)
    if module:
        if isinstance(widget, QListWidget):
            widget.addItem(module[0])
        else:
            widget.setText(module[0])

#-------------------------------------------------------------------------------
# doClickForAddSRCDST()
# Additional non-binary files or folders to be added to the executable.
# The path separator is platform specific, os.pathsep(which is ; on Windows and : on most unix systems) is used.
# This option can be used multipletimes.
#-------------------------------------------------------------------------------
def doClickForAddSRCDST(event, mw):
    dlg = dialog.DlgAddData(mw, "Add data", dialog.DlgAddData.BOTH)
    result = dlg.exec()
    if result == QDialog.Accepted:
        src = dlg.txtDataSource.text()
        dst = dlg.txtDataDest.text()
        mw.lstAddData.addItem("%s%s%s" % (src, os.pathsep, dst))

#-------------------------------------------------------------------------------
# doClickForAddBinary()
# Additional binary files to be added to the executable.
# See the --add-data option for more details.
# This option can be used multiple times.
#-------------------------------------------------------------------------------
def doClickForAddBinary(event, mw):
    dlg = dialog.DlgAddData(mw, "Add binary", QFileDialog.ExistingFile)
    result = dlg.exec()
    if result == QDialog.Accepted:
        src = dlg.txtDataSource.text()
        dst = dlg.txtDataDest.text()
        mw.lstAddBinary.addItem("%s%s%s" % (src, os.pathsep, dst))

#-------------------------------------------------------------------------------
# getAddOptionsFromList()
#-------------------------------------------------------------------------------
def getAddOptionsFromList(lstWidget, prefix):
    rc = ""
    for i in range(lstWidget.count()):
        rc = rc + '%s="%s" ' % (prefix, str(lstWidget.item(i).text()))
    return rc

#-------------------------------------------------------------------------------
# genSpec()
#-------------------------------------------------------------------------------
def genSpec(mw):
    global gen
    gen = GEN_SPEC
    mw.showMessage("Generating the spec file")
    mw.btnRunEXE.setEnabled(False)
    mw.btnOpenFolder.setEnabled(False)
    source_file = mw.txtMainFile.text()
    if source_file == "":
        mw.showMessage("Nothing to build")
        return

    if not os.path.isabs(source_file):
        source_file = os.path.join(os.path.abspath('.'), source_file)
    mw.source_path = os.path.split(source_file)[0]
    # print("SF=%s\nSP=%s"%(source_file, mw.source_path))
    global name_base
    name_base = mw.txtName.text() if mw.txtName.text() else os.path.splitext(os.path.basename(source_file))[0]

    global dist_path
    dist_path = mw.txtDistPath.text() if mw.txtDistPath.text() else os.path.join(mw.source_path, "dist")
    work_path = mw.txtWorkPath.text() if mw.txtWorkPath.text() else os.path.join(mw.source_path, "build")

    if not os.path.isabs(dist_path):
        dist_path = os.path.join(mw.source_path, dist_path)
        # source_file = os.path.join(source_file, dist_path)

    if not os.path.isabs(work_path):
        work_path = os.path.join(mw.source_path, work_path)

    if mw.chkOneDir.isChecked():
        dist_path = os.path.join(dist_path, name_base)

    global name_EXE
    name_EXE = os.path.join(dist_path, name_base)

    if mw.CurrentOS == "Windows":
        name_EXE = name_EXE + ".exe" if name_EXE[-3:].lower() != ".exe" else name_EXE

    if mw.chkCleanBeforeBuild.isChecked():
        cleanUp(mw)

    command_line = buildCommand(mw, GEN_SPEC)
    mw.showMessage("Generating spec file with %s" % command_line)
    runCommand(command_line, mw.source_path, mw, MODE_BUILD)
    # postProcess(mw)

#-------------------------------------------------------------------------------
# buildEXE()
#-------------------------------------------------------------------------------
def buildEXE(mw):
    global gen
    gen = GEN_EXE
    mw.btnRunEXE.setEnabled(False)
    mw.btnOpenFolder.setEnabled(False)
    source_file = mw.txtMainFile.text()
    if source_file == "":
        mw.showMessage("Nothing to build")
        return

    if not os.path.isabs(source_file):
        source_file = os.path.join(os.path.abspath('.'), source_file)
    mw.source_path = os.path.split(source_file)[0]
    # print("SF=%s\nSP=%s"%(source_file, mw.source_path))
    global name_base
    name_base = mw.txtName.text() if mw.txtName.text() else os.path.splitext(os.path.basename(source_file))[0]

    global dist_path
    dist_path = mw.txtDistPath.text() if mw.txtDistPath.text() else os.path.join(mw.source_path, "dist")
    work_path = mw.txtWorkPath.text() if mw.txtWorkPath.text() else os.path.join(mw.source_path, "build")

    if not os.path.isabs(dist_path):
        dist_path = os.path.join(mw.source_path, dist_path)
        # source_file = os.path.join(source_file, dist_path)

    if not os.path.isabs(work_path):
        work_path = os.path.join(mw.source_path, work_path)

    if mw.chkOneDir.isChecked():
        dist_path = os.path.join(dist_path, name_base)

    global name_EXE
    name_EXE = os.path.join(dist_path, name_base)

    if mw.CurrentOS == "Windows":
        name_EXE = name_EXE + ".exe" if name_EXE[-3:].lower() != ".exe" else name_EXE

    if mw.chkCleanBeforeBuild.isChecked():
        cleanUp(mw)

    command_line = buildCommand(mw, GEN_EXE)
    mw.showMessage("Building with %s" % command_line)
    mw.tbwBuild.setCurrentIndex(0)
    runCommand(command_line, mw.source_path, mw, MODE_BUILD)
    # postProcess(mw)

#-------------------------------------------------------------------------------
# cleanUp()
#-------------------------------------------------------------------------------
def cleanUp(mw):
    dist_path = mw.txtDistPath.text() if mw.txtDistPath.text() else os.path.join(mw.source_path, "dist")
    if os.path.normpath(dist_path) == os.path.normpath(mw.source_path):
        dist_path = os.path.join(source_path, "dist")
    work_path = mw.txtWorkPath.text() if mw.txtWorkPath.text() else os.path.join(mw.source_path, "build")
    if os.path.normpath(work_path) == os.path.normpath(mw.source_path):
        work_path = os.path.join(mw.source_path, "build")
    utils.deleteFolder(dist_path)
    utils.deleteFolder(work_path)

#-------------------------------------------------------------------------------
# isEXE()
#-------------------------------------------------------------------------------
def isEXE(fpath):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

#-------------------------------------------------------------------------------
# getEXE()
#-------------------------------------------------------------------------------
def getEXE(fpath):
    aEXE = []
    for r, d, f in os.walk(fpath):
        for file in f:
            if isEXE(os.path.join(r, file)):
                aEXE.append(os.path.join(r, file))
    print(aEXE)
    return aEXE

#-------------------------------------------------------------------------------
# buildCommand()
#-------------------------------------------------------------------------------
def buildCommand(mw, gen_mode):
    if mw.txtMainFile.text() == "":
        mw.showMessage("Nothing to build")
        return

    #---------------------------------------------------------------------------
    # Build the command line
    #---------------------------------------------------------------------------
    source_file = '"{}"'.format(mw.txtMainFile.text())
    _, extension = splitext(source_file)
    if extension == ".spec":
        workPath_option = '--workpath "{}" '.format(mw.txtWorkPath.text()) if mw.txtWorkPath.text() else ''
        distPath_option = '--distpath "{}" '.format(mw.txtDistPath.text()) if mw.txtDistPath.text() else ''
        UPXDir_option = '--upx-dir "{}" '.format(mw.txtUPXDir.text()) if mw.txtUPXDir.text() else ''
        ascii_option = '--ascii ' if mw.chkAscii.isChecked() else ''
        clean_option = '--clean ' if mw.chkClean.isChecked() else ''
        noConfirm_option = '--noconfirm ' if mw.chkNoConfirm.isChecked() else ''

        command_line = 'pyinstaller {} {}{}{}{}{}{}'.format(\
        source_file,\
        workPath_option,\
        distPath_option,\
        UPXDir_option,\
        ascii_option,\
        clean_option,\
        noConfirm_option)
    else:
    #---------------------------------------------------------------------------
    # Set the general options according to the GUI
    #---------------------------------------------------------------------------
        gen_option = '-D ' if mw.chkOneDir.isChecked() else '-F '
        workPath_option = '--workpath "{}" '.format(mw.txtWorkPath.text()) if mw.txtWorkPath.text() else ''
        distPath_option = '--distpath "{}" '.format(mw.txtDistPath.text()) if mw.txtDistPath.text() else ''
        specPath_option = '--specpath "{}" '.format(mw.txtSpecPath.text()) if mw.txtSpecPath.text() else ''
        UPXDir_option = '--upx-dir "{}" '.format(mw.txtUPXDir.text()) if mw.txtUPXDir.text() else ''
        ascii_option = '--ascii ' if mw.chkAscii.isChecked() else ''
        clean_option = '--clean ' if mw.chkClean.isChecked() else ''
        logLevel_option = '--log-level "{}" '.format(mw.cbxLogLevel.currentText()) if mw.cbxLogLevel.currentText() else ''
        noConfirm_option = '--noconfirm ' if mw.chkNoConfirm.isChecked() else ''
        name_option = '--name "{}" '.format(mw.txtName.text()) if mw.txtName.text() else ''
        key_option = '--key {} '.format(mw.txtKey.text()) if mw.txtKey.text() else ''
        debug_option = '--debug "{}" '.format(mw.cbxDebug.currentText()) if mw.cbxDebug.currentText() != "none" else ''
        strip_option = '--strip ' if mw.chkStrip.isChecked() else ''
        noUPX_option = '--noupx ' if mw.chkNoUPX.isChecked() else ''
        paths_option = getAddOptionsFromList(mw.lstPaths, "--paths")
        addData_option = getAddOptionsFromList(mw.lstAddData, "--add-data")
        addBinary_option = getAddOptionsFromList(mw.lstAddBinary, "--add-binary")
        hiddenImport_option = getAddOptionsFromList(mw.lstHiddenImport, "--hidden-import")
        collectSubmodules_option = getAddOptionsFromList(mw.lstPaths, "--collect-submodules")
        collectData_option = getAddOptionsFromList(mw.lstPaths, "--collect-data")
        collectBinaries_option = getAddOptionsFromList(mw.lstPaths, "--collect-binaries")
        collectAll_option = getAddOptionsFromList(mw.lstPaths, "--collect-all")
        copyMetadata_option = getAddOptionsFromList(mw.lstPaths, "--copy-metadata")
        recursiveCopyMetadata_option = getAddOptionsFromList(mw.lstPaths, "--recursive-copy-metadata")
        additionalHooksDir_option = getAddOptionsFromList(mw.lstAdditionalHooksDir, "--additional-hooks-dir")
        runtimeHook_option = getAddOptionsFromList(mw.lstRuntimeHook, "--runtime-hook")
        excludeModule_option = getAddOptionsFromList(mw.lstExcludeModule, "--exclude-module")
        runtimeTmpDir_option = '--runtime-tmpdir "{}" '.format(mw.txtRuntimeTmpDir.text()) if mw.txtRuntimeTmpDir.text() else ''
        bootloaderIgnoreSignals_option = '--bootloader-ignore-signals ' if mw.chkBootloaderIgnoreSignals.isChecked() else ''
        extraOptions_option = "{}".format(mw.txtExtraOptions.text()) if mw.txtExtraOptions.text() else ''

        #---------------------------------------------------------------------------
        # Set the Windows and Mac OS X specific options according to the GUI
        #---------------------------------------------------------------------------
        console_option = '--console ' if mw.chkConsole.isChecked() else ''
        windowed_option = '--windowed ' if mw.chkWindowed.isChecked() else ''
        icon_option = '--icon "{}" '.format(mw.txtIcon.text()) if mw.txtIcon.text() else ''
        disableWindowedTraceback_option = '--disable-windowed-traceback ' if mw.chkDisableWindowedTraceback.isChecked() else ''

        #---------------------------------------------------------------------------
        # Set the Windows specific options according to the GUI
        #---------------------------------------------------------------------------
        versionFile_option = '--version-file "{}" '.format(mw.txtVersionFile.text()) if mw.txtVersionFile.text() else ''
        manifest_option = '--manifest "{}" '.format(mw.txtManifest.text()) if mw.txtManifest.text() else ''
        resource_option = getAddOptionsFromList(mw.lstResource, "--resource")
        UACAdmin_option = '--uac-admin ' if mw.chkUACAdmin.isChecked() else ''
        UACUIAccess_option = '--uac-uiaccess ' if mw.chkUACUIAccess.isChecked() else ''
        winPrivateAssemblies_option = '--win-private-assemblies ' if mw.chkWinPrivateAssemblies.isChecked() else ''
        winNoPreferRedirects_option = '--win-no-prefer-redirects ' if mw.chkWinNoPreferRedirects.isChecked() else ''

        #---------------------------------------------------------------------------
        # Set the Mac OS X specific options according to the GUI
        #---------------------------------------------------------------------------
        OSXBundleIdentifier_option = '--osx-bundle-identifier "{}" '.format(mw.txtOSXBundleIdentifier.text()) if mw.txtOSXBundleIdentifier.text() else ''
        targetArchitecture_option = '--target-architecture "{}" '.format(mw.cbxTargetArchitecture.currentText()) if mw.cbxTargetArchitecture.currentText() != "current" else ''
        codesignIdentity_option = '--codesign-identity "{}" '.format(mw.txtCodesignIdentity.text()) if mw.txtCodesignIdentity.text() else ''
        OSXEntitlementsFile_option = '--osx-entitlements-file "{}" '.format(mw.txtOSXEntitlementsFile.text()) if mw.txtOSXEntitlementsFile.text() else ''

        if gen_mode == GEN_EXE:
            program = 'pyinstaller'
        else:
            program = 'pyi-makespec'
            # The following options are not recognized when generating a spec file
            # So, we clear them just in case of...
            ascii_option = ""
            clean_option = ""
            noConfirm_option = ""

        command_line = '{} {}{} {}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(\
        program,\
        gen_option,\
        source_file,\
        workPath_option,\
        distPath_option,\
        specPath_option,\
        addData_option,\
        addBinary_option,\
        paths_option,\
        name_option,\
        UPXDir_option,\
        ascii_option,\
        clean_option,\
        logLevel_option,\
        noConfirm_option,\
        key_option,\
        debug_option,\
        strip_option,\
        noUPX_option,\
        hiddenImport_option,\
        collectSubmodules_option,\
        collectData_option,\
        collectBinaries_option,\
        collectAll_option,\
        copyMetadata_option,\
        recursiveCopyMetadata_option,\
        additionalHooksDir_option,\
        runtimeHook_option,\
        excludeModule_option,\
        runtimeTmpDir_option,\
        bootloaderIgnoreSignals_option,\
        extraOptions_option,\
        console_option,\
        windowed_option,\
        icon_option,\
        disableWindowedTraceback_option,\
        versionFile_option,\
        manifest_option,\
        resource_option,\
        UACAdmin_option,\
        UACUIAccess_option,\
        winPrivateAssemblies_option,\
        winNoPreferRedirects_option,\
        OSXBundleIdentifier_option,\
        targetArchitecture_option,\
        codesignIdentity_option,\
        OSXEntitlementsFile_option,\
        extraOptions_option\
        )
    print(command_line)
    return command_line

#-------------------------------------------------------------------------------
# browseMainFile()
#-------------------------------------------------------------------------------
def browseMainFile(mw):
    filename = QFileDialog.getOpenFileName(mw, 'Open main file', '', 'Python sources (*.py *.pyw);;Specification files (*.spec);;All files (*.*)', options = QFileDialog.DontUseNativeDialog)[0]
    if filename:
        setMainFile(mw, filename)
    else:
        mw.setEnabledGUI(False)

#-------------------------------------------------------------------------------
# setMainFile()
#-------------------------------------------------------------------------------
def setMainFile(mw, filename):
    if os.path.exists(filename):
        mw.txtMainFile.setText(filename)
        _, extension = splitext(filename)
        if extension == ".spec":
            # readSpecFile(filename)
            spec = open(filename, 'r').read()
            mw.filename = filename
            mw.txtSpecFile.setPlainText(spec)
            mw.tbwBuild.setCurrentIndex(2)
            mw.showMessage("Opening %s file" % (filename))
            mw.txtSpecFile.textChanged.connect(mw.changedText)
            mw.lblModified.setText("")
            mw.dirtyFlag = False
            mw.setEnabledGUI(False)
            # Only these options are available when building from spec file
            mw.lblDistPath.setEnabled(True)
            mw.txtDistPath.setEnabled(True)
            mw.lblWorkPath.setEnabled(True)
            mw.txtWorkPath.setEnabled(True)
            mw.lblUPXDir.setEnabled(True)
            mw.txtUPXDir.setEnabled(True)
            mw.lblAscii.setEnabled(True)
            mw.chkAscii.setEnabled(True)
            mw.lblClean.setEnabled(True)
            mw.chkClean.setEnabled(True)
            mw.lblNoConfirm.setEnabled(True)
            mw.chkNoConfirm.setEnabled(True)
            # Enable the build button
            mw.btnBuildEXE.setEnabled(True)
            mw.btnGenSpec.setEnabled(False)
        else:
            mw.tbwBuild.setCurrentIndex(0)
            mw.showMessage("Main file set as %s" % (filename))
            mw.txtSpecFile.setPlainText("")
            mw.lblModified.setText("")
            mw.dirtyFlag = False
            mw.setEnabledGUI(True)
            # Enable the build and gen spec buttons
            mw.btnBuildEXE.setEnabled(True)
            mw.btnGenSpec.setEnabled(True)
    else:
        mw.showMessage("Unknown file %s" % (filename))
        mw.setEnabledGUI(False)

#-------------------------------------------------------------------------------
# runEXE()
#-------------------------------------------------------------------------------
def runEXE(mw):
    if mw.lblRunEXE.text() != const.db['PROGRAM_NONE']:
        try:
            source_path = os.path.split(mw.lblRunEXE.text())[0]
            mw.tbwBuild.setCurrentIndex(0)
            rc = runCommand(r'"{}" {}'.format(mw.lblRunEXE.text(), mw.txtParamsEXE.text()), source_path, mw, MODE_RUN)
        except:
            mw.btnBuildEXE.setEnabled(True)
            mw.lblLEDBuild.setPixmap(QPixmap("pix/led_green.png"))
            mw.showMessage("Can't run this")
    else:
        mw.showMessage("Nothing to run")

#-------------------------------------------------------------------------------
# runCommand()
#-------------------------------------------------------------------------------
def runCommand(command, cwd, mw, typeRun):
    global mode
    mode = typeRun

    mw.setCursor(Qt.WaitCursor)
    mw.btnBuildEXE.setEnabled(False)
    mw.lblLEDBuild.setPixmap(QPixmap("pix/led_red.png"))
    mw.repaint()
    mw.txtBuildOutput.appendPlainText("%s%s %s" % (nowPrompt(),settings.db['SHELL_PROMPT'], command))
    global time1
    time1 = time.time()
    mw.btnBreakEXE.setEnabled(True)
    mw.tbwBuild.setCurrentIndex(0)
    QGuiApplication.processEvents()
    global tCmd
    tCmd = shrealding.Shreald(mw, command, cwd, shell=True)
    tCmd.linePrinted.connect(lambda line, mw=mw: handleLine(line, mw))
    mw.lblTimeBuild.setText("---")

#-------------------------------------------------------------------------------
# handleLine()
#-------------------------------------------------------------------------------
def handleLine(line, mw):
    global mode
    if line !=  "":
        if line[0] == '1':
            if mode == MODE_BUILD:
                mw.txtBuildOutput.appendPlainText("%s%s" % (nowPrompt(), line[1:].rstrip()))
            else:
                mw.txtBuildOutput.appendPlainText("%s[OUT] %s" % (nowPrompt(), line[1:].rstrip()))
        elif line[0] == '2':
            if mode == MODE_BUILD:
                mw.txtBuildOutput.appendPlainText("%s%s" % (nowPrompt(), line[1:].rstrip()))
            else:
                mw.txtBuildOutput.appendPlainText("%s[ERR] %s" % (nowPrompt(), line[1:].rstrip()))
        elif line[0] == 'x':
            killProcess(mw)

#-------------------------------------------------------------------------------
# killProcess()
#-------------------------------------------------------------------------------
def killProcess(mw):
    global tCmd
    try:
        tCmd.kill()
    except:
        pass
    finalizeCommand(mw)

#-------------------------------------------------------------------------------
# finalizeCommand()
#-------------------------------------------------------------------------------
def finalizeCommand(mw):
    global tCmd
    global time1
    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
    mw.txtBuildOutput.appendPlainText("%sEnd of shreald with PID %s" % (nowPrompt(), str(tCmd.process.pid)))
    mw.txtBuildOutput.appendPlainText("%sReturn code is %d" % (nowPrompt(), tCmd.returncode))
    time2 = time.time()
    elapsed = time2 - time1
    mw.lblTimeBuild.setText(utils.getHumanTime(elapsed))

    mw.lblLEDBuild.setPixmap(QPixmap("pix/led_green.png"))
    mw.lblRCBuild.setText("RC=%d" % tCmd.returncode)
    mw.btnBreakEXE.setEnabled(False)
    mw.btnBuildEXE.setEnabled(True)

    # FIXME : name_EXE seems to be incorrect when building from spec file ?!?
    global name_EXE
    global mode
    global gen

    if gen == GEN_SPEC:
        if tCmd.returncode == 0:
            # Grab the generated spec filename from the shreald's log
            # and open this spec file into the editor
            for line in tCmd.log:
                if line.startswith("1wrote"):
                    specFileName = line.split(' ', maxsplit=1)[1].strip()
                    spec = open(specFileName, 'r').read()
                    mw.filename = specFileName
                    mw.txtSpecFile.setPlainText(spec)
                    mw.txtMainFile.setText(specFileName)
                    mw.txtMainFile.deselect()
                    mw.tbwBuild.setCurrentIndex(2)
                    mw.txtSpecFile.textChanged.connect(mw.changedText)
                    mw.lblModified.setText("")
                    mw.dirtyFlag = False
                    mw.setEnabledGUI(False)
                    # Only these options are available when building from spec file
                    mw.lblDistPath.setEnabled(True)
                    mw.txtDistPath.setEnabled(True)
                    mw.lblWorkPath.setEnabled(True)
                    mw.txtWorkPath.setEnabled(True)
                    mw.lblUPXDir.setEnabled(True)
                    mw.txtUPXDir.setEnabled(True)
                    mw.lblAscii.setEnabled(True)
                    mw.chkAscii.setEnabled(True)
                    mw.lblClean.setEnabled(True)
                    mw.chkClean.setEnabled(True)
                    mw.lblNoConfirm.setEnabled(True)
                    mw.chkNoConfirm.setEnabled(True)
                    # Enable the build button
                    mw.btnBuildEXE.setEnabled(True)
                    mw.btnGenSpec.setEnabled(False)
                    break
            mw.showMessage("Spec file successfully generated")
        else:
            mw.showMessage("Error when generating spec file")
    else:
        if mode == MODE_BUILD:
            if tCmd.returncode == 0:
                postProcess(mw)
                mw.btnRunEXE.setEnabled(True)
                mw.btnOpenFolder.setEnabled(True)
                # aEXE = getEXE(os.path.join(source_path,"dist"))
                if os.path.exists(name_EXE):
                    fInfo = utils.getFileInfo(name_EXE)
                    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
                    mw.txtBuildOutput.appendPlainText("%sExecutable file info" % nowPrompt())
                    mw.txtBuildOutput.appendPlainText("%s====================" % nowPrompt())
                    for key, value in fInfo.items():
                        mw.txtBuildOutput.appendPlainText("{}{}\t{}".format(nowPrompt(), key, value))
                    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
                    mw.lblRunEXE.setText(name_EXE)
                    mw.showMessage("Build completed successfully")
                else:
                    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
                    mw.txtBuildOutput.appendPlainText("%s!!! BUILD FAILED !!!" % nowPrompt())
                    mw.txtBuildOutput.appendPlainText("%sCan't find the generated file %s." % (nowPrompt(), name_EXE))
                    mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
            else:
                mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
                mw.txtBuildOutput.appendPlainText("%s!!! BUILD FAILED !!!" % nowPrompt())
                mw.txtBuildOutput.appendPlainText("%sRetry with checking first the upper right \"Clean\" option." % nowPrompt())
                mw.txtBuildOutput.appendPlainText("%s" % nowPrompt())
                # mw.lblLEDBuild.setPixmap(QPixmap("pix/led_red.png"))
                mw.btnRunEXE.setEnabled(False)
                mw.btnOpenFolder.setEnabled(False)
                mw.lblRunEXE.setText(const.db['PROGRAM_NONE'])
                mw.showMessage("Build failed")
        else:
            mw.btnRunEXE.setEnabled(True)
            mw.btnOpenFolder.setEnabled(True)
            mw.showMessage("End of runnning builded executable with return code %d" % tCmd.returncode)
    mw.setCursor(Qt.ArrowCursor)

#-------------------------------------------------------------------------------
# nowPrompt()
#-------------------------------------------------------------------------------
def nowPrompt():
    now = datetime.datetime.now()
    return now.strftime(settings.db['OUTPUT_TIMESTAMP'])

#-------------------------------------------------------------------------------
# patchChars()
#-------------------------------------------------------------------------------
def patchChars(s):
    myChars = {'“':'ô', 'Š':'ê', '‚':'é', 'ÿ':''}
    foo = s.split()
    ret = []
    for item in foo:
        ret.append(myChars.get(item, item)) # Try to get from dict, otherwise keep value
    return(" ".join(ret))

#-------------------------------------------------------------------------------
# loadPythonFile()
#-------------------------------------------------------------------------------
def loadPythonFile(name, path):
    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

#-------------------------------------------------------------------------------
# readSpecFile()
#-------------------------------------------------------------------------------
def readSpecFile(specfile):
    # not finished...
    # The purpose of this function is to read options from spec file
    # and fill the GUI options according to what we get from the spec file
    pyfile = shutil.copy(specfile, os.path.join(tempfile.gettempdir(),"spec.py"))
    specmodule = loadPythonFile("spec", pyfile)
    print(specmodule.a.datas)

#-------------------------------------------------------------------------------
# postProcess()
#-------------------------------------------------------------------------------
def postProcess(mw):
    global dist_path
    mw.showMessage("Post Processing")
