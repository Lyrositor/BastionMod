# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from BastionLib.audio.sound_bank import Sound, SoundBank, Track, WaveBankFileLink
from document import Document
from logger import Logger
from utils import format_hex, deformat_hex


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

        # Create the reverb button group.
        self.reverb = QButtonGroup(self)
        self.reverb.addButton(self.reverb_none)
        self.reverb.addButton(self.reverb_microsoft)

        # Create the properties button group.
        self.properties = QButtonGroup(self)
        self.properties.setExclusive(False)
        for button in {self.property_1, self.property_2, self.property_3,
            self.property_4, self.property_5, self.property_6,
            self.property_7}:
            self.properties.addButton(button)

        # Connect the signals.
        self.sounds_list.itemSelectionChanged.connect(self.load_sound)
        self.tracks_list.itemSelectionChanged.connect(self.load_track)
        self.wave_bank_files_list.itemSelectionChanged.connect(self.load_wbf)

        self.category_list.activated.connect(self.update_sound)
        self.properties.buttonClicked.connect(self.update_sound)
        self.reverb.buttonClicked.connect(self.update_sound)
        for unknown in {
            self.unknown1_edit, self.unknown2_edit, self.unknown3_edit}:
            unknown.textEdited.connect(self.update_sound)

        # Create the sound actions.
        sound_add = QAction('Add Sound', self.sounds_list)
        sound_remove = QAction('Remove Sound', self.sounds_list)
        sound_remove.setEnabled(False)
        sound_add.triggered.connect(self.sound_add)
        sound_remove.triggered.connect(self.sound_remove)
        self.sounds_list.addActions([sound_add, sound_remove])

        # Create the track actions.
        track_add = QAction('Add Track', self.tracks_list)
        track_edit_u = QAction('Edit Unknown Variable', self.tracks_list)
        track_remove = QAction('Remove Track', self.tracks_list)
        track_edit_u.setEnabled(False)
        track_remove.setEnabled(False)
        track_add.triggered.connect(self.track_add)
        track_edit_u.triggered.connect(self.track_edit_unknown)
        track_remove.triggered.connect(self.track_remove)
        self.tracks_list.addActions([track_add, track_edit_u, track_remove])

        # Create the wave bank file actions.
        wbf_add = QAction('Add Wave Bank File', self.wave_bank_files_list)
        wbf_edit_u = QAction('Edit Unknown Variable', self.wave_bank_files_list)
        wbf_remove = QAction('Remove Wave Bank File', self.wave_bank_files_list)
        wbf_edit_u.setEnabled(False)
        wbf_remove.setEnabled(False)
        wbf_add.triggered.connect(self.wbf_add)
        wbf_edit_u.triggered.connect(self.wbf_edit_unknown)
        wbf_remove.triggered.connect(self.wbf_remove)
        self.wave_bank_files_list.addActions([wbf_add, wbf_edit_u, wbf_remove])

        self.reset()

    def reset(self):
        """
            Loads the data from the sound bank file.
        """

        if not self.module.sound_bank:
            self.module.sound_bank = SoundBank.from_file(
                self.module.bastion_folder.sound_bank)
            Logger.info('Loaded sound bank.')
        sounds = self.module.sound_bank.sounds

        self.sounds_list.reset()
        self.sounds_list.clear()
        for i, sound in enumerate(sounds):
            self.sounds_list.addItem('Sound {}'.format(i))

    def save(self, to_file=True):
        """
            Saves the sound bank's data.
        """

        if to_file and not self.is_saved and self.module.sound_bank:
            self.module.save_sound_bank()
        else:
            super().save()

    def get_idx(self, l):
        """
            Fetches the currently selected index for a list.
        """

        item = l.currentItem()
        if not item:
            return None
        return l.row(item)

    def get_selected_sound_idx(self):
        """
            Returns the currently selected sound's index.
        """

        return self.get_idx(self.sounds_list)

    def get_selected_track_idx(self):
        """
            Returns the currently selected track's index.
        """

        return self.get_idx(self.tracks_list)

    def get_selected_wbf_idx(self):
        """
            Returns the currently selected wave bank file's index.
        """
        return self.get_idx(self.wave_bank_files_list)

    def load_sound(self):
        """
            Loads the sound's data and displays it.
        """

        idx = self.get_selected_sound_idx()
        if idx is -1:
            self.toggle_sound(False)
            return
        sound = self.module.sound_bank.sounds[idx]
        self.toggle_sound(True)

        for button in self.properties.buttons():
            button.setChecked(button.text() in sound.properties)
        self.reverb_none.setEnabled(True)
        self.reverb_none.setChecked(True)
        if sound.reverb == 'Microsoft Reverb':
            self.reverb_microsoft.setChecked(True)
        self.category_list.setCurrentIndex(
            self.category_list.findText(sound.category))

        self.unknown1_edit.setText(format_hex(sound.unknown1))
        self.unknown2_edit.setText(format_hex(sound.unknown2))
        self.unknown3_edit.setText(format_hex(sound.unknown3))

        for i, track in enumerate(sound.tracks):
            self.tracks_list.addItem('Track {}'.format(i))
        if sound.tracks:
            self.tracks_list.setCurrentRow(0)

    def toggle_sound(self, enabled=True):
        """
            Toggles the display of the sound properties.
        """

        self.tracks_label.setEnabled(enabled)
        self.tracks_list.setEnabled(enabled)
        self.tracks_list.reset()
        self.tracks_list.clear()
        self.tracks_list.actions()[1].setEnabled(False)
        self.wave_bank_files_label.setEnabled(False)
        self.wave_bank_files_list.setEnabled(False)
        self.wave_bank_files_list.reset()
        self.wave_bank_files_list.clear()
        self.wave_bank_files_list.actions()[1].setEnabled(False)
        self.tracks_list.setEnabled(enabled)
        self.properties_box.setEnabled(enabled)
        self.unknown_box.setEnabled(enabled)
        self.reverb_none.setChecked(True)
        for button in self.properties.buttons():
            button.setChecked(False)
        actions = self.sounds_list.actions()
        actions[1].setEnabled(enabled)

    def load_track(self):
        """
            Loads the track's data and displays it.
        """

        idx = self.get_selected_track_idx()
        actions = self.tracks_list.actions()
        self.wave_bank_files_list.reset()
        self.wave_bank_files_list.clear()
        self.load_wbf(True)
        if idx is -1:
            actions[1].setEnabled(False)
            self.wave_bank_files_label.setEnabled(False)
            self.wave_bank_files_list.setEnabled(False)
            return
        sound = self.module.sound_bank.sounds[self.get_selected_sound_idx()]
        track = sound.tracks[idx]
        self.wave_bank_files_label.setEnabled(True)
        self.wave_bank_files_list.setEnabled(True)
        actions[1].setEnabled(True)
        actions[2].setEnabled(True)

        for wbf in track.files:
            self.wave_bank_files_list.addItem(
                '{} {}'.format(wbf.bank_name, wbf.file_id))

    def load_wbf(self, none=False):
        """
            Enables and disables a file-specific actions.
        """

        idx = self.get_selected_track_idx()
        actions = self.wave_bank_files_list.actions()
        if idx is -1 or none:
            actions[1].setEnabled(False)
            actions[2].setEnabled(False)
        else:
            actions[1].setEnabled(True)
            actions[2].setEnabled(True)

    def update_sound(self):
        """
            Loads the latest values of the sound's settings.
        """

        idx = self.get_selected_sound_idx()
        if idx is -1:
            self.toggle_sound(False)
            return
        sound = self.module.sound_bank.sounds[idx]

        sound.category = self.category_list.currentText()
        sound.reverb = self.reverb.checkedButton().text()
        sound.properties = [
            c.text() for c in self.properties.buttons() if c.isChecked()]
        sound.unknown1 = deformat_hex(self.unknown1_edit.text())
        sound.unknown2 = deformat_hex(self.unknown2_edit.text())
        sound.unknown3 = deformat_hex(self.unknown3_edit.text())

        self.module.modify_sound_bank()

    def sound_add(self):
        """
            Adds a new sound entry.
        """

        new_sound = Sound()
        self.module.sound_bank.sounds.append(new_sound)

        self.reset()
        self.sounds_list.setCurrentRow(self.sounds_list.count() - 1)
        self.sounds_list.scrollToBottom()

        self.module.modify_sound_bank()

    def sound_remove(self):
        """
            Removes the selected sound.
        """

        idx = self.get_selected_sound_idx()
        if idx is -1:
            return
        del self.module.sound_bank.sounds[idx]
        self.reset()

        self.module.modify_sound_bank()

    def track_add(self):
        """
            Adds a new track to the current sound.
        """

        s_idx = self.get_selected_sound_idx()
        if s_idx is -1:
            return
        new_track = Track()
        sound = self.module.sound_bank.sounds[s_idx]
        sound.tracks.append(new_track)

        self.load_sound()
        self.tracks_list.setCurrentRow(self.tracks_list.count() - 1)
        self.tracks_list.scrollToBottom()

        self.module.modify_sound_bank()

    def track_edit_unknown(self):
        """
            Edits the unknown track variable.
        """

        s_idx = self.get_selected_sound_idx()
        t_idx = self.get_selected_track_idx()
        if s_idx is -1 or t_idx is -1:
            return
        track = self.module.sound_bank.sounds[s_idx].tracks[t_idx]
        new_unknown, status = QInputDialog.getText(
            self, 'Edit Unknown Variable', 'Value:',
            text=format_hex(track.unknown))
        if status and new_unknown:
            track.unknown = deformat_hex(new_unknown)
            self.module.modify_sound_bank()

    def track_remove(self):
        """
            Removes the selected track.
        """

        s_idx = self.get_selected_sound_idx()
        t_idx = self.get_selected_track_idx()
        if s_idx is -1 or t_idx is -1:
            return
        del self.module.sound_bank.sounds[s_idx].tracks[t_idx]
        self.load_sound()

        self.module.modify_sound_bank()

    def wbf_add(self):
        """
            Adds a new wave bank file to the current track.
        """

        s_idx = self.get_selected_sound_idx()
        t_idx = self.get_selected_track_idx()
        if s_idx is -1 or t_idx is -1:
            return
        track = self.module.sound_bank.sounds[s_idx].tracks[t_idx]
        new_wbf = WaveBankFileLink()
        new_name, status = QInputDialog.getText(
            self, 'New Wave Bank File', 'Name (without "WaveBank"):',
            text=new_wbf.bank_name[:-8])
        if not status:
            return
        new_id, status = QInputDialog.getInt(
            self, 'New Wave Bank File', 'File ID:', min=0)
        if not status:
            return
        new_wbf.bank_name = new_name + 'WaveBank'
        new_wbf.file_id = new_id
        track.files.append(new_wbf)

        self.load_track()
        self.wave_bank_files_list.setCurrentRow(
            self.wave_bank_files_list.count() - 1)
        self.wave_bank_files_list.scrollToBottom()

        self.module.modify_sound_bank()

    def wbf_edit_unknown(self):
        """
            Edits the unknown wave bank file variable.
        """

        s_idx = self.get_selected_sound_idx()
        t_idx = self.get_selected_track_idx()
        w_idx = self.get_selected_wbf_idx()
        if s_idx is -1 or t_idx is -1 or w_idx is -1:
            return
        wbf = self.module.sound_bank.sounds[s_idx].tracks[t_idx].files[w_idx]
        new_unknown, status = QInputDialog.getText(
            self, 'Edit Unknown Variable', 'Value:',
            text=format_hex([wbf.unknown]))
        if status and new_unknown:
            wbf.unknown = deformat_hex(new_unknown)[0]
            self.module.modify_sound_bank()

    def wbf_remove(self):
        """
            Removes the selected wave bank file.
        """

        s_idx = self.get_selected_sound_idx()
        t_idx = self.get_selected_track_idx()
        w_idx = self.get_selected_wbf_idx()
        if s_idx is -1 or t_idx is -1 or w_idx is -1:
            return
        del self.module.sound_bank.sounds[s_idx].tracks[t_idx].files[w_idx]
        self.load_track()

        self.module.modify_sound_bank()
