# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic


class Document(QWidget):
    """
        Base class for BastionMod documents.
    """

    def __init__(self, ui_file=None):
        """
            Loads the document's layout.
        """

        super().__init__()
        self.is_saved = True
        if ui_file:
            uic.loadUi(ui_file, self)

    def reset(self):
        """
            Resets the document to its default state.
        """

    def close(self):
        """
            Called whenever the document is closed.
        """

        if not self.is_saved:
            message = QMessageBox.question(
                self,
                'Save Document',
                'This document has been modified. Would you like to save your changes?',
                QMessageBox.Cancel | QMessageBox.Discard | QMessageBox.Save,
                QMessageBox.Save)
            if message == QMessageBox.Save:
                self.save()
                return True
            elif message == QMessageBox.Discard:
                return True
            return False
        return True

    def modify(self):
        """
            Called when a modification has been made.
        """


        tabs = self.parent().parent()
        idx = tabs.indexOf(self)
        if tabs.tabText(idx)[-1] != '*':
            tabs.setTabText(idx, tabs.tabText(idx) + '*')
        self.is_saved = False

    def save(self):
        """
            Called when a document save is requested.
        """

        if not self.is_saved:
            tabs = self.parent().parent()
            idx = tabs.indexOf(self)
            if tabs.tabText(idx)[-1] == '*':
                tabs.setTabText(idx, tabs.tabText(idx)[:-1])
            self.is_saved = True
