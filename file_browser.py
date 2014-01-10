# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class FileBrowser(QStandardItemModel):
    """Lists all file-like entries for Bastion's content folder."""

    def on_select(self, selected):
        """Called when an entry is selected."""

        if selected:
            item = self.itemFromIndex(selected[0].topLeft())
            if item.on_select:
                item.on_select()


class FileBrowserEntry(QStandardItem):
    """Represents an entry in the file browser."""

    def __init__(self, name, on_select=None):
        """Creates a new named file browser entry."""

        super().__init__(name)
        self.on_select = lambda: on_select(self.data()) if on_select else None
        self.setEditable(False)
