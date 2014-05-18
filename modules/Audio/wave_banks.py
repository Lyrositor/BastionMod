# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os
import tempfile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from document import Document
from BastionLib.binary_stream import BinaryStream
from BastionLib.audio.wave_bank import WaveBank


class WaveBanksDocument(Document):
    """
        Presents all available wave banks for modification.
    """

    UI_FILE = 'ui/audio_wave_banks_document.ui'

    def __init__(self, module):
        """
            Creates a new document.
        """

        super().__init__(self.UI_FILE)
        self.module = module

        # Connect the signals.
        self.wave_banks_list.itemSelectionChanged.connect(self.load_wave_bank)
        self.files_list.itemSelectionChanged.connect(self.load_file)
        self.save_button.clicked.connect(self.save_to_file)
        self.load_button.clicked.connect(self.load_from_file)
        self.play_button.clicked.connect(self.play_file)
        self.stop_button.clicked.connect(self.stop_file)

        # Create the actions.
        add_wave_bank = QAction('Add Wave Bank', self.wave_banks_list)
        add_wave_bank.triggered.connect(self.add_wave_bank)
        self.wave_banks_list.addAction(add_wave_bank)
        add_file = QAction('Add File', self.files_list)
        add_file.triggered.connect(self.add_file)
        rm_file = QAction('Remove File', self.files_list)
        rm_file.triggered.connect(self.remove_file)
        rm_file.setEnabled(False)
        self.files_list.addActions([add_file, rm_file])

        self.reset()

    def reset(self):
        """
            Loads the data from the files.
        """

        self.toggle_files(False)
        self.wave_bank = None
        self.wave_banks_list.clear()
        for w_name, w_path in self.module.bastion_folder.wave_banks.items():
            self.wave_banks_list.addItem(w_name)

    def save(self):
        """
            Saves the wave banks to their files.
        """

        if not self.is_saved and self.wave_bank:
            self.wave_bank.save(
                self.module.bastion_folder.wave_banks[self.wave_bank.name])
        super().save()

    def load_wave_bank(self, reload_files=False):
        """
            Loads the wave bank associated with a list item.

            If reload_files is True, this will just reload the files list.
        """

        if self.wave_bank and not reload_files:
            if not self.close():
                return

        item = self.wave_banks_list.currentItem()
        if not item:
            self.wave_bank = None
            self.toggle_files(False)
            return
        self.toggle_files(True)
        name = item.text()

        # Load the wave bank file.
        if not reload_files:
            if name != WaveBank.STREAMING:
                self.wave_bank = WaveBank.from_file(
                    self.module.bastion_folder.wave_banks[name])
            else:
                self.wave_bank = WaveBank.from_file(
                    self.module.bastion_folder.wave_banks[name],
                    self.module.bastion_folder.streaming_dir)

        # Load the wave bank's files.
        self.files_list.reset()
        self.files_list.clear()
        self.files_list.scrollToTop()
        for n, ogg_file in enumerate(self.wave_bank.files):
            item = QListWidgetItem('{}_{:03}.ogg'.format(name, n))
            self.files_list.addItem(item)

    def load_file(self):
        """
            Loads the file associated with a list item.
        """

        item = self.files_list.currentItem()
        if not item:
            self.toggle_files(False, True)
            return
        self.toggle_files(True, True)

    def toggle_files(self, enabled=True, buttons=False):
        """
            Disables the files widgets.
        """

        self.files_label.setEnabled(enabled)
        self.files_list.setEnabled(enabled)
        if enabled and buttons:
            self.load_button.setEnabled(enabled)
            self.save_button.setEnabled(enabled)
            self.play_button.setEnabled(enabled)
            self.stop_button.setEnabled(enabled)
        else:
            self.load_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(False)
        if buttons:
            self.files_list.actions()[1].setEnabled(enabled)

    def get_file(self):
        """
            Gets the currently selected file index.
        """

        item = self.files_list.currentItem()
        if not self.wave_bank or not item:
            return None
        return self.files_list.row(item)

    def save_to_file(self):
        """
            Saves the current file to an actual file on the disk.
        """

        i = self.get_file()
        if i is None:
            return
        item = self.files_list.currentItem()
        data = self.wave_bank.files[i]
        output_path = QFileDialog.getSaveFileName(self, 'Save Wave Bank File',
            item.text(), 'Ogg File (*.ogg)')
        if not output_path:
            return
        s = BinaryStream(data)
        s.save(output_path)

    def load_from_file(self, i=None):
        """
            Loads audio data from a file on the disk to the wave bank file.
        """

        if i is None:
            i = self.get_file()
            if i is None:
                return
        input_path, status = QFileDialog.getOpenFileName(self,
            'Open Wave Bank File', '', 'Ogg File (*.ogg)')
        if not input_path or not status:
            return
        s = BinaryStream.from_file(input_path)
        if i < len(self.wave_bank.files):
            self.wave_bank.files[i] = s.getvalue()
        else:
            self.wave_bank.files.append(s.getvalue())
        self.modify()

    def play_file(self):
        """
            Plays the file by writing it to a temporary file first.
            @todo Implement using an audio library
        """

        i = self.get_file()
        if i is None:
            return
        data = self.wave_bank.files[i]
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(data)
        os.spawnlp(os.P_WAIT, 'totem', '', temp_file.name)

    def stop_file(self):
        """
            Stops the currently playing file.
            @todo Implement using an audio library
        """

    def add_wave_bank(self):
        """
            Adds a new wave bank in the list.
        """

        name, status = QInputDialog.getText(self, 'Add Wave Bank',
            'Name (without "WaveBank"):')
        if not name or not status:
            return
        name += 'WaveBank'
        if name in self.module.bastion_folder.wave_banks:
            QMessageBox.critical(self, 'Error',
                'Name is already in use. Please choose another one.')
            return

        path = os.path.join(self.module.bastion_folder.audio, name + '.xwb')
        bank = WaveBank()
        bank.save(path)
        self.module.bastion_folder.wave_banks[name] = path

        self.reset()
        items = self.wave_banks_list.findItems(name, Qt.MatchExactly)
        if not items:
            QMessageBox.critical(self, 'Error',
                'Something went wrong while creating the wave bank.')
            return
        self.wave_banks_list.scrollToItem(items[0])
        self.wave_banks_list.setCurrentItem(items[0])

    def add_file(self):
        """
            Adds a new file in the list.
        """

        if not self.wave_bank:
            return

        i = len(self.wave_bank.files)
        self.load_from_file(i)
        self.load_wave_bank(True)
        item = self.files_list.item(i)
        self.files_list.scrollToItem(item)
        self.files_list.setCurrentItem(item)
        self.modify()

    def remove_file(self):
        """
            Removes a file from the wave bank.
        """

        if not self.wave_bank:
            return

        i = self.get_file()
        if i is None:
            return
        del self.wave_bank.files[i]
        self.load_wave_bank(True)
        self.modify()