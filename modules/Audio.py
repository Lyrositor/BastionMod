# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os
import tempfile

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from document import Document
from .bastion_module import BastionModule
from BastionLib.binary_stream import BinaryStream
from BastionLib.audio.sound_bank import SoundBank
from BastionLib.audio.wave_bank import WaveBank
from logger import Logger


class Audio(BastionModule):
    """
        Manages, plays and saves audio files.
    """

    def __init__(self, bastion_folder, window):
        """
            Loads the available audio data and displays it.
        """

        super().__init__(bastion_folder, window)
        self.sound_bank = None

        a = self.add_browser_entry('Audio')
        self.add_browser_entry('Wave Banks', None, a, self.open_wave_banks)
        self.add_browser_entry('Sounds', None, a, self.open_sounds)
        self.add_browser_entry('Cues', None, a, self.open_cues)

    def get_document(self, cls):
        """
            Returns an existing instance of the document, if possible.

            This method searches for an existing document with the same class;
            if it finds one, it switches to it and returns it, otherwise it
            returns None.
        """

        for i in range(self.window.editor.count()):
            document = self.window.editor.widget(i)
            if isinstance(document, cls):
                self.window.editor.setCurrentIndex(i)
                return document
        return None

    def open_wave_banks(self, entry_value):
        """
            Opens the Wave Banks document.
        """

        document = self.get_document(WaveBanksDocument)
        if not document:
            document = WaveBanksDocument(self)
            self.add_document('Wave Banks', document)
        else:
            self.window.editor.setCurrentWidget(document)

    def open_sounds(self, entry_value):
        """
            Opens the Sounds document.
        """

        document = self.get_document(SoundsDocument)
        if not document:
            document = SoundsDocument(self)
            self.add_document('Sounds', document)
        else:
            self.window.editor.setCurrentWidget(document)

    def open_cues(self, entry_value):
        """
            Opens the Cues document.
        """

        document = self.get_document(CuesDocument)
        if not document:
            document = CuesDocument(self)
            self.add_document('Cues', document)
        else:
            self.window.editor.setCurrentWidget(document)


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
        self.wave_banks_list.insertAction(None, add_wave_bank)
        add_file = QAction('Add File', self.files_list)
        add_file.triggered.connect(self.add_file)
        self.files_list.insertAction(None, add_file)

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
        input_path = QFileDialog.getOpenFileName(self, 'Open Wave Bank File',
            '', 'Ogg File (*.ogg)')
        if not input_path:
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


class SoundsDocument(Document):
    """
        Presents all available sounds for modification.
    """

    UI_FILE = 'ui/audio_sounds_document.ui'

    def __init__(self, module):
        """
            Creates a new document.
        """

        super().__init__(self.UI_FILE)
        self.module = module

        self.reset()

    def reset(self):
        """
            Loads the data from the sound bank file.
        """

        if not self.module.sound_bank:
            self.module.sound_bank = SoundBank.from_file(
                self.module.bastion_folder.sound_bank)
        sb = self.module.sound_bank


class CuesDocument(Document):
    """
        Presents all available cues for modification.
    """

    UI_FILE = 'ui/audio_cues_document.ui'

    def __init__(self, module):
        """
            Creates a new document.
        """

        super().__init__(self.UI_FILE)
        self.module = module

        self.reset()

    def reset(self):
        """
            Loads the data from the sound bank file.
        """

        if not self.module.sound_bank:
            self.module.sound_bank = SoundBank.from_file(
                self.module.bastion_folder.sound_bank)
        sb = self.module.sound_bank
