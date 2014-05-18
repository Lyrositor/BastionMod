#!/usr/bin/env python3
# BastionMod
# Allows for the modding of Bastion, by Supergiant Games.
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

from BastionLib.bastion_folder import BastionFolder
from logger import Logger
import modules
from resources import *


class BastionModApp(QApplication):
    """
        BastionMod's main Qt application.
    """

    MAIN_WINDOW_UI_FILE = 'ui/main_window.ui'

    def __init__(self, args):
        """
            Shows the main window.
        """

        super().__init__(args)

        # Status variables.
        self.bastion_folder = None
        self.current_path = None

        # Load the main window.
        self.main = QMainWindow()
        uic.loadUi(BastionModApp.MAIN_WINDOW_UI_FILE, self.main)
        self.main.closeEvent = self.closeEvent
        self.main.show()

        # Prepare the file browser.
        self.setup_file_browser()

        # Connect the signals to their respective actions.
        self.main.quit.triggered.connect(self.main.close)
        self.main.open.triggered.connect(lambda: self.open_bastion_folder())
        self.main.save_document.triggered.connect(lambda: self.save_document())
        self.main.close_document.triggered.connect(lambda: self.close_document())
        self.main.toggle_debug_mode.triggered.connect(self.toggle_debug_mode)
        self.main.editor.currentChanged.connect(self.update_document_actions)
        self.main.editor.tabCloseRequested.connect(self.close_document)

    def print(self, msg, status=False):
        """Prints information to the main window's debug screen."""

        self.main.output.appendPlainText(str(msg))
        if status:
            self.main.status_bar.showMessage(str(msg))

    def setup_file_browser(self, bastion_folder=None):
        """
            Sets up the file browser to its default state.
        """

        self.main.file_browser.setEnabled(bool(bastion_folder))
        self.main.file_browser.itemSelectionChanged.connect(self.on_select)

    def on_select(self):
        """
            Called when the file browser selection changes.
        """

        selected = self.main.file_browser.currentItem()
        if selected:
            on_select = selected.data(0, Qt.UserRole + 1)
            if on_select:
                on_select()

    def open_bastion_folder(self, bastion_path=None):
        """
            Opens the Bastion root folder for editing.
        """

        if not bastion_path:
            bastion_path = QFileDialog.getExistingDirectory(self.main,
                'Open Bastion Folder', self.current_path)
            if not bastion_path:
                return
        self.current_path = bastion_path
        if not self.close_bastion_folder():
            return
        Logger.info('Loading data from "{}"...'.format(bastion_path))
        self.bastion_folder = BastionFolder(bastion_path)
        if self.bastion_folder.version != BastionFolder.VERSION_UNKNOWN:
            self.main.toggle_debug_mode.setEnabled(True)
            self.main.toggle_debug_mode.setChecked(
                bool(self.bastion_folder.is_debug()))
        self.setup_file_browser(self.bastion_folder)
        modules.load_modules(self.bastion_folder, self.main)
        Logger.info('Loaded data.')

    def close_bastion_folder(self):
        """
            Closes the active Bastion folder.
        """

        if self.bastion_folder:
            for i in range(self.main.editor.count()):
                w = self.main.editor.widget(0)
                if w and not w.close():
                    return False
                self.main.editor.removeTab(0)
        self.setup_file_browser()
        self.main.toggle_debug_mode.setEnabled(False)
        self.main.toggle_debug_mode.setChecked(False)
        self.bastion_folder = None
        return True

    def toggle_debug_mode(self):
        """
            Enables or disables the debug mode in Bastion.
        """

        if not self.bastion_folder:
            return
        self.bastion_folder.toggle_debug_mode(
            not self.bastion_folder.is_debug())
        self.bastion_folder.save_exe()
        self.main.toggle_debug_mode.setChecked(
            bool(self.bastion_folder.is_debug()))

    def close_document(self, idx=None):
        """
            Requests that the indexed document be closed.
        """

        if idx is None:
            idx = self.main.editor.currentIndex()
            if idx is -1:
                return
        document = self.main.editor.widget(idx)
        if document.close():
            self.main.editor.removeTab(idx)

    def save_document(self, idx=None):
        """
            Requests that the indexed document be saved.
        """

        if idx is None:
            idx = self.main.editor.currentIndex()
            if idx is -1:
                return
        document = self.main.editor.widget(idx)
        document.save()

    def update_document_actions(self, idx):
        """
            Updates the available document actions in the main menu.
        """

        if idx == -1:
            self.main.save_document.setEnabled(False)
            self.main.close_document.setEnabled(False)
        else:
            self.main.save_document.setEnabled(True)
            self.main.close_document.setEnabled(True)

    def closeEvent(self, event):
        """
            Called when the window is about to close.
        """

        if self.close_bastion_folder():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = BastionModApp(sys.argv)
    Logger.set_level(Logger.INFO_LEVEL)
    Logger.set_output(app.print)
    result = app.exec_()
    sys.exit(result)