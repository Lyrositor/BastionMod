# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from BastionLib.audio.sound_bank import Cue, SoundBank
from document import Document
from logger import Logger
from utils import format_hex, deformat_hex


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

        # Connect the signals.
        self.cues_list.itemSelectionChanged.connect(self.load_cue)
        self.sounds_list.itemSelectionChanged.connect(self.load_sound)

        # Create the cues actions.
        cue_add = QAction('Add Cue', self.cues_list)
        cue_remove = QAction('Remove Cue', self.cues_list)
        cue_remove.setEnabled(False)
        cue_add.triggered.connect(self.cue_add)
        cue_remove.triggered.connect(self.cue_remove)
        self.cues_list.addActions([cue_add, cue_remove])
        self.cues_list.itemChanged.connect(self.cue_rename)

        # Create the sound actions.
        sound_add = QAction('Add Sound', self.sounds_list)
        sound_remove = QAction('Remove Sound', self.sounds_list)
        sound_remove.setEnabled(False)
        sound_add.triggered.connect(self.sound_add)
        sound_remove.triggered.connect(self.sound_remove)
        self.sounds_list.addActions([sound_add, sound_remove])
        self.sounds_list.itemChanged.connect(self.sound_change)

        for unknown in {self.unknown1_edit, self.unknown2_edit}:
            unknown.textEdited.connect(self.cue_update)

        self.reset()

    def reset(self):
        """
            Loads the data from the sound bank file.
        """

        if not self.module.sound_bank:
            self.module.sound_bank = SoundBank.from_file(
                self.module.bastion_folder.sound_bank)
            Logger.info('Loaded sound bank.')
        cues = self.module.sound_bank.cues

        self.cues_list.reset()
        self.cues_list.clear()
        for cue in cues:
            item = QListWidgetItem(cue.name, self.cues_list)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def save(self, to_file=True):
        """
            Saves the sound bank's data.
        """

        if to_file and not self.is_saved and self.module.sound_bank:
            self.module.save_sound_bank()
        else:
            super().save()

    def load_cue(self):
        """
            Loads the cue's data and displays it.
        """

        idx = self.cues_list.currentIndex().row()
        if idx is -1:
            self.toggle_cue(False)
            return
        cue = self.module.sound_bank.cues[idx]
        self.toggle_cue(True)

        self.unknown1_edit.setText(format_hex(cue.unknown1))
        self.unknown2_edit.setText(format_hex(cue.unknown2))

        for sound in cue.sounds:
            item = QListWidgetItem(str(sound), self.sounds_list)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def toggle_cue(self, enabled=True):
        """
            Toggles the cue's display.
        """

        self.cues_list.actions()[1].setEnabled(True)

        self.sounds_label.setEnabled(enabled)
        self.sounds_list.setEnabled(enabled)
        self.sounds_list.reset()
        self.sounds_list.clear()
        self.sounds_list.actions()[1].setEnabled(False)

        self.unknown1_edit.setEnabled(enabled)
        self.unknown1_label.setEnabled(enabled)
        self.unknown2_edit.setEnabled(enabled)
        self.unknown2_label.setEnabled(enabled)

        self.unknown1_edit.clear()
        self.unknown2_edit.clear()

    def load_sound(self):
        """
            Loads the sound-specific properties.
        """

        idx = self.cues_list.currentIndex().row()
        if idx is -1:
            self.sounds_list.actions()[1].setEnabled(False)
        else:
            self.sounds_list.actions()[1].setEnabled(True)

    def cue_add(self):
        """
            Adds a new cue entry.
        """

        if not self.module.sound_bank:
            return
        new_cue = Cue()
        new_name, status = QInputDialog.getText(
            self, 'New Cue Name', 'Name:')
        if status and new_name:
            new_cue.name = new_name
            self.module.sound_bank.cues.append(new_cue)

            self.reset()
            self.cues_list.setCurrentRow(self.cues_list.count() - 1)
            self.cues_list.scrollToBottom()

            self.module.modify_sound_bank()

    def cue_rename(self, item):
        """
            Renames the cue.
        """

        if not self.module.sound_bank:
            return
        idx = self.cues_list.indexFromItem(item).row()
        if idx is not -1:
            cue = self.module.sound_bank.cues[idx]
            if cue.name != item.text():
                self.module.sound_bank.cues[idx].name = item.text()
                self.module.modify_sound_bank()

    def cue_update(self):
        """
            Updates the cue's properties.
        """

        if not self.module.sound_bank:
            return
        idx = self.cues_list.currentIndex().row()
        if idx is not -1:
            cue = self.module.sound_bank.cues[idx]
            cue.unknown1 = deformat_hex(self.unknown1_edit.text())
            cue.unknown2 = deformat_hex(self.unknown2_edit.text())
            self.module.modify_sound_bank()

    def cue_remove(self):
        """
            Removes the selected cue entry.
        """

        if not self.module.sound_bank:
            return
        idx = self.cues_list.currentIndex().row()
        if idx is not -1:
            del self.module.sound_bank.cues[idx]
            self.reset()
            self.cues_list.scrollToBottom()
            self.module.modify_sound_bank()

    def sound_add(self):
        """
            Adds a new sound to the current cue.
        """

        if not self.module.sound_bank:
            return
        c_idx = self.cues_list.currentIndex().row()
        if c_idx is not -1:
            cue = self.module.sound_bank.cues[c_idx]
            new_id, status = QInputDialog.getInt(
                self, 'New Sound ID', 'ID:', min=0,
                max=len(self.module.sound_bank.sounds) - 1)
            if status:
                cue.sounds.append(int(new_id))
                self.load_cue()
                self.sounds_list.scrollToBottom()
                self.module.modify_sound_bank()

    def sound_change(self, item):
        """
            Changes the value of the currently selected sound.
        """

        if not self.module.sound_bank:
            return
        c_idx = self.cues_list.currentIndex().row()
        s_idx = self.sounds_list.indexFromItem(item).row()
        if c_idx is not -1 and s_idx is not -1:
            cue = self.module.sound_bank.cues[c_idx]
            cue.sounds[s_idx] = int(item.text())
            self.module.modify_sound_bank()

    def sound_remove(self):
        """
            Removes a sound from the current cue.
        """

        if not self.module.sound_bank:
            return
        c_idx = self.cues_list.currentIndex().row()
        s_idx = self.sounds_list.currentIndex().row()
        if c_idx is not -1 and s_idx is not -1:
            del self.module.sound_bank.cues[c_idx].sounds[s_idx]
            self.load_cue()
            self.sounds_list.scrollToBottom()
            self.module.modify_sound_bank()