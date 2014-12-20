# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..bastion_module import BastionModule
from .map_file import MapFileDocument


class Maps(BastionModule):
    """
        Manages the modification of Bastion maps.
    """

    def __init__(self, bastion_folder, window):
        """
            Loads the list of available maps and displays them.
        """

        super().__init__(bastion_folder, window)

        self.maps_entry = self.add_browser_entry('Maps')
        self.reload()

    def reload(self):
        """
            Reloads the file list.
        """

        for c in self.maps_entry.takeChildren():
            del c
        self.bastion_folder.load(self.bastion_folder.path)
        for map_name in sorted(self.bastion_folder.maps_files):
            self.add_browser_entry(map_name, None, self.maps_entry, self.open_map)

    def get_map_document(self, name):
        """
            Searches for a named map's document, if it exists.
        """

        for i in range(self.window.editor.count()):
            item = self.window.editor.widget(i)
            if isinstance(item, MapFileDocument) and item.name == name:
                return item
        return None

    def open_map(self):
        """
            Opens a map file.
        """

        for item in self.window.file_browser.selectedItems():
            document = self.get_map_document(item.text(0))
            if not document:
                f_path = self.bastion_folder.maps_files[item.text(0)]
                document = MapFileDocument(self, f_path)
                self.add_document(item.text(0), document)
            else:
                self.window.editor.setCurrentWidget(document)