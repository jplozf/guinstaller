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
import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from mainwindow import MainWindow

import const
import settings

#-------------------------------------------------------------------------------
# setTheme()
#-------------------------------------------------------------------------------
def setTheme(theme):
    app.setStyle('Fusion')
    palette = QPalette()
    try:
        palette.setColor(QPalette.Window, QColor(theme[0]))
        palette.setColor(QPalette.WindowText, QColor(theme[1]))
        palette.setColor(QPalette.Base, QColor(theme[2]))
        palette.setColor(QPalette.AlternateBase, QColor(theme[3]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme[4]))
        palette.setColor(QPalette.ToolTipText, QColor(theme[5]))
        palette.setColor(QPalette.Text, QColor(theme[6]))
        palette.setColor(QPalette.Button, QColor(theme[7]))
        palette.setColor(QPalette.ButtonText, QColor(theme[8]))
        palette.setColor(QPalette.BrightText, QColor(theme[9]))
        palette.setColor(QPalette.Link, QColor(theme[10]))
        palette.setColor(QPalette.Highlight, QColor(theme[11]))
        palette.setColor(QPalette.HighlightedText, QColor(theme[12]))
    except:
        palette.setColor(QPalette.Window, QColor(const.db['THEME_LIGHT_WINDOW']))
        palette.setColor(QPalette.WindowText, QColor(const.db['THEME_LIGHT_WINDOW_TEXT']))
        palette.setColor(QPalette.Base, QColor(const.db['THEME_LIGHT_BASE']))
        palette.setColor(QPalette.AlternateBase, QColor(const.db['THEME_LIGHT_ALTERNATE_BASE']))
        palette.setColor(QPalette.ToolTipBase, QColor(const.db['THEME_LIGHT_TOOLTIP_BASE']))
        palette.setColor(QPalette.ToolTipText, QColor(const.db['THEME_LIGHT_TOOLTIP_TEXT']))
        palette.setColor(QPalette.Text, QColor(const.db['THEME_LIGHT_TEXT']))
        palette.setColor(QPalette.Button, QColor(const.db['THEME_LIGHT_BUTTON']))
        palette.setColor(QPalette.ButtonText, QColor(const.db['THEME_LIGHT_BUTTON_TEXT']))
        palette.setColor(QPalette.BrightText, QColor(const.db['THEME_LIGHT_BRIGHT_TEXT']))
        palette.setColor(QPalette.Link, QColor(const.db['THEME_LIGHT_LINK']))
        palette.setColor(QPalette.Highlight, QColor(const.db['THEME_LIGHT_HIGHLIGHT']))
        palette.setColor(QPalette.HighlightedText, QColor(const.db['THEME_LIGHT_HIGHLIGHTED_TEXT']))
    app.setPalette(palette)

#-------------------------------------------------------------------------------
# main()
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    # Create application
    app = QApplication(sys.argv)
    app.setOrganizationName(const.db["ORGANIZATION_NAME"])
    app.setOrganizationDomain(const.db["ORGANIZATION_DOMAIN"])
    app.setApplicationName(const.db["APPLICATION_NAME"])

    if settings.db["APP_THEME"] == "LIGHT":
        light = [\
            const.db['THEME_LIGHT_WINDOW'],\
            const.db['THEME_LIGHT_WINDOW_TEXT'],\
            const.db['THEME_LIGHT_BASE'],\
            const.db['THEME_LIGHT_ALTERNATE_BASE'],\
            const.db['THEME_LIGHT_TOOLTIP_BASE'],\
            const.db['THEME_LIGHT_TOOLTIP_TEXT'],\
            const.db['THEME_LIGHT_TEXT'],\
            const.db['THEME_LIGHT_BUTTON'],\
            const.db['THEME_LIGHT_BUTTON_TEXT'],\
            const.db['THEME_LIGHT_BRIGHT_TEXT'],\
            const.db['THEME_LIGHT_LINK'],\
            const.db['THEME_LIGHT_HIGHLIGHT'],\
            const.db['THEME_LIGHT_HIGHLIGHTED_TEXT']]
        setTheme(light)
    elif settings.db["APP_THEME"] == "DARK":
        dark = [\
            const.db['THEME_DARK_WINDOW'],\
            const.db['THEME_DARK_WINDOW_TEXT'],\
            const.db['THEME_DARK_BASE'],\
            const.db['THEME_DARK_ALTERNATE_BASE'],\
            const.db['THEME_DARK_TOOLTIP_BASE'],\
            const.db['THEME_DARK_TOOLTIP_TEXT'],\
            const.db['THEME_DARK_TEXT'],\
            const.db['THEME_DARK_BUTTON'],\
            const.db['THEME_DARK_BUTTON_TEXT'],\
            const.db['THEME_DARK_BRIGHT_TEXT'],\
            const.db['THEME_DARK_LINK'],\
            const.db['THEME_DARK_HIGHLIGHT'],\
            const.db['THEME_DARK_HIGHLIGHTED_TEXT']]
        setTheme(dark)
    elif settings.db["APP_THEME"] == "CUSTOM":
        custom = [\
            settings.db['THEME_CUSTOM_WINDOW'],\
            settings.db['THEME_CUSTOM_WINDOW_TEXT'],\
            settings.db['THEME_CUSTOM_BASE'],\
            settings.db['THEME_CUSTOM_ALTERNATE_BASE'],\
            settings.db['THEME_CUSTOM_TOOLTIP_BASE'],\
            settings.db['THEME_CUSTOM_TOOLTIP_TEXT'],\
            settings.db['THEME_CUSTOM_TEXT'],\
            settings.db['THEME_CUSTOM_BUTTON'],\
            settings.db['THEME_CUSTOM_BUTTON_TEXT'],\
            settings.db['THEME_CUSTOM_BRIGHT_TEXT'],\
            settings.db['THEME_CUSTOM_LINK'],\
            settings.db['THEME_CUSTOM_HIGHLIGHT'],\
            settings.db['THEME_CUSTOM_HIGHLIGHTED_TEXT']]
        setTheme(custom)
    else:
        setTheme(const.db['THEME_LIGHT'])

    # Set icon https://www.iconsdb.com/icon-sets/web-2-green-icons/python-icon.html
    icon = QIcon("./pix/guinstaller.png")
    app.setWindowIcon(icon)

    # Create main widget
    if len(sys.argv) > 1:
        w = MainWindow(mainFile = sys.argv[1])
    else:
        w = MainWindow()
    w.setWindowTitle("%s %s" % (const.db["APPLICATION_NAME"], const.db["VERSION"]))
    w.show()

    # Execute application
    currentExitCode = app.exec_()
    app = None
