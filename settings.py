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
from PyQt5.QtWidgets import QWidget, QPushButton, QGroupBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QSpacerItem, QSizePolicy, QFileDialog, QDialog, QMessageBox
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPixmap
from PyQt5 import uic
import shelve
import copy
import json

import const
import os
import utils

#-------------------------------------------------------------------------------
# These are the default values
#-------------------------------------------------------------------------------
defaultValues = [
    ['APP_TIMER_STATUS', 3000, "Time delay (in ms) for displaying message in status bar"],\
    ['EDITOR_TAB_SPACES', 4, "Tab width in spaces"],\
    ['EDITOR_FONT', "Courier", "Editor font's name"],\
    ['EDITOR_FONT_SIZE', 9, "Editor font's size"],\
    ['EDITOR_COLOR_BACKGROUND', "#eaf2ce", "Editor background's color"],\
    ['EDITOR_COLOR_CURRENT_LINE', "white", "Editor current line background's color"],\
    ['EDITOR_RIGHT_MARGIN', True, "Right margin displayed or not"],\
    ['EDITOR_RIGHT_MARGIN_COLUMN', 80, "Right margin place in characters"],\
    ['EDITOR_RIGHT_MARGIN_COLOR', "#FFA8A8", "Right margin color"],\
    ['EDITOR_LINES_AREA_COLOR', "#E9E8E2", "Background color for the lines numbers area"],\
    ['EDITOR_LINES_NUMBER_COLOR', "black", "Text color for the lines numbers area"],\
    ['APP_EXIT_CONFIRM', True, "Warning for confirmation or not when exiting the application"],\
    ['APP_THEME', "LIGHT", "Look and feel theme for the application.\nThree values are available : LIGHT, DARK (both themes are hardcoded) and CUSTOM (which can be customized later)"],\
    ['SHELL_CODEPAGE', "utf-8", "Codepage used for running compiled application"],\
    ['SHELL_PROMPT', "$>", "Prompt displayed in output log when running compiled application"],\
    ['OUTPUT_STYLE_FONT_SIZE', 9, "Output log font size"],\
    ['OUTPUT_STYLE_FONT_NAME', 'Courier', "Output log font name"],\
    ['OUTPUT_STYLE_COLOR', "#ffa500", "Output log text color"],\
    ['OUTPUT_STYLE_COLOR_BACKGROUND', "#49453e", "Output log background color"],\
    ['OUTPUT_TIMESTAMP', "[%Y%m%d-%H%M%S] ", "Output log timestamp displayed"],\
    ['SYNTAX_PYTHON_KEYWORD', 'brown normal', "Python keyword color"],\
    ['SYNTAX_PYTHON_OPERATOR', 'red normal', "Python operator color"],\
    ['SYNTAX_PYTHON_BRACE', 'darkgray normal', "Python color for braces"],\
    ['SYNTAX_PYTHON_DEF', 'black bold', "Python color for def"],\
    ['SYNTAX_PYTHON_CLASS', 'red bold', "Python color for class"],\
    ['SYNTAX_PYTHON_STRING', '#E8AF30 normal', "Python color for strings between \"\""],\
    ['SYNTAX_PYTHON_STRING2', '#E8AF30 normal', "Python color for strings between ''"],\
    ['SYNTAX_PYTHON_COMMENT', '#969696 italic', "Python color for comments"],\
    ['SYNTAX_PYTHON_SELF', '#0066F6 italic', "Python color for self"],\
    ['SYNTAX_PYTHON_NUMBERS', 'brown normal', "Python color for numbers"],\
    ['SYNTAX_PYTHON_DUNDERS', '#0066F6 italic bold', "Python color for __keywords__"],\
    ['THEME_CUSTOM_WINDOW', "#efefef", "Custom theme color for windows background"],\
    ['THEME_CUSTOM_WINDOW_TEXT', "#000000", "Custom theme color for windows text"],\
    ['THEME_CUSTOM_BASE', "#ffffff", "Custom theme color for base"],\
    ['THEME_CUSTOM_ALTERNATE_BASE', "#f7f7f7", "Custom theme color for alternate base"],\
    ['THEME_CUSTOM_TOOLTIP_BASE', "#ffffdc", "Custom theme color for tooltips background"],\
    ['THEME_CUSTOM_TOOLTIP_TEXT', "#000000", "Custom theme color for tooltips text"],\
    ['THEME_CUSTOM_TEXT', "#000000", "Custom theme color for texts"],\
    ['THEME_CUSTOM_BUTTON', "#efefef", "v theme color for buttons background"],\
    ['THEME_CUSTOM_BUTTON_TEXT', "#000000", "Custom theme color for buttons text"],\
    ['THEME_CUSTOM_BRIGHT_TEXT', "#ffffff", "Custom theme color for bright text"],\
    ['THEME_CUSTOM_LINK', "#0000ff", "Custom theme color for links"],\
    ['THEME_CUSTOM_HIGHLIGHT', "#308cc6", "Custom theme color for highlighted backgrounds"],\
    ['THEME_CUSTOM_HIGHLIGHTED_TEXT', "#ffffff", "Custom theme color for highlighted text"]\
]

#-------------------------------------------------------------------------------
# Open config file
#-------------------------------------------------------------------------------
firstTime = False

appDir = os.path.join(os.path.expanduser("~"), const.db["APP_FOLDER"])
if not os.path.exists(appDir):
    os.makedirs(appDir)
    firstTime = True
dbFileName = os.path.join(os.path.join(appDir, const.db["CONFIG_FILE"]))
db = shelve.open(dbFileName, writeback=True)

#-------------------------------------------------------------------------------
# Set default values if they not exists in config file
#-------------------------------------------------------------------------------
for x in defaultValues:
   if not x[0] in db:
      db[x[0]] = x[1]

#-------------------------------------------------------------------------------
# Save config file
#-------------------------------------------------------------------------------
db.sync()

cached_db = shelve.open(os.path.join(os.path.join(appDir, const.db["CACHED_CONFIG_FILE"])))
cached_db.update(copy.deepcopy(dict(db)))
cached_db.close()

#-------------------------------------------------------------------------------
# resetSettings()
#-------------------------------------------------------------------------------
def resetSettings():
    for x in defaultValues:
        db[x[0]] = x[1]

#-------------------------------------------------------------------------------
# getSet()
#-------------------------------------------------------------------------------
def getSet(param):
    """
    Return a dict of all parameters beginning by the provided string with their values
    """
    rc = {}
    for x in db:
        if x in (i[0] for i in defaultValues):
            if x.startswith(param) or param == "":
                rc.update({x:db[x]})
    return rc

#-------------------------------------------------------------------------------
# Class TabSettings
#-------------------------------------------------------------------------------
class TabSettings(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mw = parent
        self.initUI()

#-------------------------------------------------------------------------------
# initUI()
#-------------------------------------------------------------------------------
    def initUI(self):
        self.vLayout = QVBoxLayout()
        self.central = QWidget()
        self.central.setLayout(self.vLayout)

        i = 0
        fields = []
        self.layout = QFormLayout()
        prevKeyword = ""

        self.formGroupBox = QGroupBox("About")
        self.formGroupBox.setStyleSheet("font-weight: bold;")
        self.fLayout = QFormLayout()
        self.formGroupBox.setLayout(self.fLayout)
        a = self.getField('APPLICATION_NAME')
        self.fLayout.addRow(a[0], a[1])
        a = self.getField('VERSION')
        self.fLayout.addRow(a[0], a[1])
        a = self.getField('COPYRIGHT')
        self.fLayout.addRow(a[0], a[1])
        a = self.getField('ORGANIZATION_NAME')
        self.fLayout.addRow(a[0], a[1])
        a = self.getField('ORGANIZATION_DOMAIN')
        self.fLayout.addRow(a[0], a[1])
        a = self.getField('EMAIL')
        self.fLayout.addRow(a[0], a[1])
        self.vLayout.addWidget(self.formGroupBox)

        self.formGroupBox = QGroupBox("Configuration")
        self.formGroupBox.setStyleSheet("font-weight: bold;")
        self.hLayout = QHBoxLayout()
        # Export Button
        self.btnExport = QPushButton(QIcon(QPixmap(utils.resource_path("pix/16x16/Go Out.png"))), "")
        self.btnExport.clicked.connect(self.exportJSON)
        self.btnExport.setToolTip("Export this configuration to JSON file")
        self.btnExport.setStyleSheet("font-weight: normal;")
        self.hLayout.addWidget(self.btnExport)
        # Import Button
        self.btnImport = QPushButton(QIcon(QPixmap(utils.resource_path("pix/16x16/Go In.png"))), "")
        self.btnImport.clicked.connect(self.importJSON)
        self.btnImport.setToolTip("Import configuration from JSON file")
        self.btnImport.setStyleSheet("font-weight: normal;")
        self.hLayout.addWidget(self.btnImport)
        # Reset to default Button
        self.btnResetDefault = QPushButton(QIcon(QPixmap(utils.resource_path("pix/16x16/Loop.png"))), "")
        self.btnResetDefault.clicked.connect(self.resetDefault)
        self.btnResetDefault.setToolTip("Reset configuration to default")
        self.btnResetDefault.setStyleSheet("font-weight: normal;")
        self.hLayout.addWidget(self.btnResetDefault)
        # Spacer
        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)
        self.hLayout.addSpacerItem(self.spaceItem)
        self.formGroupBox.setLayout(self.hLayout)
        self.vLayout.addWidget(self.formGroupBox)

        self.formGroupBox = QGroupBox("Warning")
        self.formGroupBox.setStyleSheet("font-weight: bold;")
        self.fLayout = QHBoxLayout()
        self.formGroupBox.setLayout(self.fLayout)
        pixLabel = QLabel()
        pixLabel.setPixmap(QPixmap(utils.resource_path("pix/16x16/Warning.png")))
        self.fLayout.addWidget(pixLabel)
        self.fLayout.addWidget(QLabel("Some settings require restarting the application to be applied"))
        self.spaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)
        self.fLayout.addSpacerItem(self.spaceItem)
        self.vLayout.addWidget(self.formGroupBox)

        for key, value in sorted(db.items(), key=lambda kv: kv[0]):
            if key in (i[0] for i in defaultValues):    # don't display obsolete settings removed from defaultValues array
                thisKeyword = key.split('_')[0]
                if thisKeyword != prevKeyword:
                    self.layout = QFormLayout()
                    self.formGroupBox = QGroupBox(thisKeyword)
                    self.formGroupBox.setStyleSheet("font-weight: bold;")
                sValue =  str(value)
                toolTip = self.getToolTip(key)
                fields.append(list([QLabel(key),QLineEdit(sValue)]))
                fields[i][0].setStyleSheet("font-weight: normal;")
                fields[i][0].setToolTip(toolTip)
                if sValue[0] == "#" or utils.isColorName(sValue.split()[0]) == True:
                    fields[i][1].setStyleSheet("font-weight: normal; background-color: %s" % sValue.split()[0])
                else:
                    fields[i][1].setStyleSheet("font-weight: normal;")
                # fields[i][1].setToolTip(toolTip)
                self.layout.addRow(fields[i][0], fields[i][1])
                fields[i][1].textChanged.connect(lambda text, label=fields[i][0].text(), x=i: self.lineChanged(label, text, x))
                i = i + 1
                if thisKeyword != prevKeyword:
                    self.formGroupBox.setLayout(self.layout)
                    self.vLayout.addWidget(self.formGroupBox)
                    prevKeyword = thisKeyword

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.central)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)

#-------------------------------------------------------------------------------
# lineChanged()
#-------------------------------------------------------------------------------
    def lineChanged(self, label, text, i):
        if type(db[label]) is str:
            db[label] = text
        elif type(db[label]) is int:
            db[label] = int(text)
        elif type(db[label]) is float:
            db[label] = float(text)
        elif type(db[label]) is bool:
            if text.lower() == "true":
                db[label] = True
            else:
                db[label] = False
        else:
            db[label] = str(text)

#-------------------------------------------------------------------------------
# getField()
# for the About panel, return a tuple of two QLabels
#-------------------------------------------------------------------------------
    def getField(self, tag):
        lbl = QLabel(utils.tagNameToString(tag))
        lbl.setStyleSheet("font-weight: normal;")
        txt = QLabel(const.db[tag])
        txt.setStyleSheet("font-weight: bold;")
        return lbl, txt

#-------------------------------------------------------------------------------
# getToolTip()
# return the tooltip for the given tag
#-------------------------------------------------------------------------------
    def getToolTip(self, tag):
        toolTip = ""
        for row in defaultValues:
            if tag == row[0]:
                toolTip = row[2]
                break
        return toolTip

#-------------------------------------------------------------------------------
# exportJSON()
#-------------------------------------------------------------------------------
    def exportJSON(self):
        filename,_ = QFileDialog.getSaveFileName(self, "Export file", "./", "JSON file (*.json);;All files (*.*)")
        if filename:
            dbList = []
            for key, value in sorted(db.items(), key=lambda kv: kv[0]):
                row = []
                row.append(key)
                row.append(value)
                dbList.append(row)

            with open(filename, "w") as jsonFile:
                jsonFile.write(json.dumps(dbList, indent='\t', separators=(',', ':'), sort_keys=True))
            self.mw.showMessage("Configuration exported as JSON to %s" % (filename))

#-------------------------------------------------------------------------------
# importJSON()
#-------------------------------------------------------------------------------
    def importJSON(self):
        filename,_ = QFileDialog.getOpenFileName(self, "Import file", "./", "JSON file (*.json);;All files (*.*)")
        if filename:
            result = QMessageBox.question(self, "Import configuration from file", "This will replace the current configuration.\nAre you sure you want to proceed ?", QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                with open(filename, "r") as jsonFile:
                    dbList = json.loads(jsonFile.read())
                for row in dbList:
                    db[row[0]] = row[1]
                self.mw.showMessage("Configuration imported from %s" % (filename))

#-------------------------------------------------------------------------------
# resetDefault()
#-------------------------------------------------------------------------------
    def resetDefault(self):
        result = QMessageBox.question(self, "Reset the configuration to default", "This will restore the default configuration.\nAre you sure you want to proceed ?", QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            resetSettings()
            self.mw.showMessage("Configuration resetted to default")
