# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..bastion_module import BastionModule
from BastionLib.bastion_folder import BastionFolder
from logger import Logger

from .wave_banks import WaveBanksDocument
from .sounds import SoundsDocument
from .cues import CuesDocument


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

        if self.bastion_folder.version != BastionFolder.VERSION_LINUX:
            Logger.error('Audio module only available on Linux.')
            return

        a = self.add_browser_entry('Audio')
        self.add_browser_entry('Wave Banks', None, a, self.open_wave_banks)
        self.add_browser_entry('Sounds', None, a, self.open_sounds)
        self.add_browser_entry('Cues', None, a, self.open_cues)

    def get_document(self, cls, switch=True):
        """
            Returns an existing instance of the document, if possible.

            This method searches for an existing document with the same class;
            if it finds one, it switches to it and returns it, otherwise it
            returns None.
        """

        for i in range(self.window.editor.count()):
            document = self.window.editor.widget(i)
            if isinstance(document, cls):
                if switch:
                    self.window.editor.setCurrentIndex(i)
                return document
        return None

    def open_wave_banks(self):
        """
            Opens the Wave Banks document.
        """

        document = self.get_document(WaveBanksDocument)
        if not document:
            document = WaveBanksDocument(self)
            self.add_document('Wave Banks', document)
        else:
            self.window.editor.setCurrentWidget(document)

    def open_sounds(self):
        """
            Opens the Sounds document.
        """

        document = self.get_document(SoundsDocument)
        if not document:
            document = SoundsDocument(self)
            self.add_document('Sounds', document)
        else:
            self.window.editor.setCurrentWidget(document)

    def open_cues(self):
        """
            Opens the Cues document.
        """

        document = self.get_document(CuesDocument)
        if not document:
            document = CuesDocument(self)
            self.add_document('Cues', document)
        else:
            self.window.editor.setCurrentWidget(document)

    def modify_sound_bank(self):
        """
            Modifies both the Cues and Sounds documents.
        """

        sd = self.get_document(SoundsDocument, False)
        if sd:
            sd.modify()
        cd = self.get_document(CuesDocument, False)
        if cd:
            cd.modify()


    def save_sound_bank(self):
        """
            Saves the sound bank, taking into account both Cues and Sounds.
        """

        if self.sound_bank:
            self.sound_bank.save(self.bastion_folder.sound_bank)

        s = self.get_document(SoundsDocument, False)
        if s:
            s.save(False)
        d = self.get_document(CuesDocument, False)
        if d:
            d.save(False)