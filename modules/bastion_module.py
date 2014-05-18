# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

from document import *
from file_browser import *
from logger import *


class BastionModule:
    """Base class for BastionMod modules."""

    def __init__(self, bastion_folder, window):
        """Initializes the module."""

        self.bastion_folder = bastion_folder
        self.window = window

    def add_browser_entry(self,
        name,
        value=None,
        parent=None,
        on_select=None):
        """Adds a new entry in the main window's file browser."""

        if not parent:
            parent = self.window.file_browser.invisibleRootItem()
        entry = QTreeWidgetItem(QTreeWidgetItem.UserType)
        entry.setText(0, name)
        entry.setData(0, Qt.UserRole, value)
        entry.setData(0, Qt.UserRole + 1, on_select)
        parent.addChild(entry)
        return entry

    def add_document(self, name, document):
        """Adds a new document to the list."""

        idx = self.window.editor.addTab(document, name)
        self.window.editor.setCurrentIndex(idx)
