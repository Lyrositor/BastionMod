# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from glob import glob
import os

from .binary_stream import BinaryStream
from .audio.sound_bank import SoundBank
from .audio.wave_bank import WaveBank


class BastionFolder:
    """
        Provides access to Bastion's folder contents.

        Note that it only provides a list of file paths, not actual contents.
        This is to ensure that folder contents are loaded only when they are
        required.
    """

    VERSION_UNKNOWN = 0
    VERSION_LINUX = 1
    VERSION_WINDOWS = 2
    VERSION_OS_X = 3

    EXE_NAME = 'Bastion.exe'

    DEBUG_OFFSET = {
        VERSION_LINUX: 0x279D7,
        VERSION_WINDOWS: 0x79aab
    }

    def __init__(self, path=None):
        """
            Initializes the folder's contents.
        """

        self.load(path)

    def load(self, path):
        """
            Loads the file paths from the specified folder path."""

        self.path = path
        self.version = BastionFolder.VERSION_UNKNOWN
        self.exe = None
        self.audio = None
        self.streaming_dir = None
        self.sound_bank = None
        self.wave_banks = {}

        if not path:
            return

        # Find out which version of Bastion this is.
        real_path = path
        if BastionFolder.EXE_NAME in os.listdir(path):
            self.version = BastionFolder.VERSION_WINDOWS
            content_path = os.path.join(real_path, 'Content')
        elif (not BastionFolder.EXE_NAME in os.listdir(path)
            and 'Linux' in os.listdir(path)):
            self.version = BastionFolder.VERSION_LINUX
            real_path = os.path.join(path, 'Linux')
            content_path = os.path.join(real_path, 'Content')
        else:
            raise ValueError('Invalid Bastion version.')

        self.exe = os.path.join(real_path, BastionFolder.EXE_NAME)

        # Audio
        self.audio = os.path.join(content_path, 'Audio')
        self.streaming_dir = os.path.join(self.audio, 'Streaming')
        self.sound_bank = os.path.join(self.audio, SoundBank.NAME)
        self.wave_banks = {os.path.basename(f)[:-4] :
            f for f in glob(os.path.join(self.audio, '*.xwb'))}

    def is_debug(self):
        """Checks if the exe is in debug mode."""

        exe_file = BinaryStream.from_file(self.exe)
        debug_offset = BastionFolder.DEBUG_OFFSET[self.version]
        exe_file.seek(debug_offset)
        b = exe_file.read_byte()
        if b == 0x16:
            return False
        elif b == 0x17:
            return True
        return None

    def toggle_debug_mode(self, debug):
        """Toggles the debug mode in Bastion."""

        # Make sure the version of Bastion is known.
        if self.version == BastionFolder.VERSION_UNKNOWN or not self.exe:
            return

        # Toggle the debug setting.
        exe_file = BinaryStream.from_file(self.exe)
        debug_offset = BastionFolder.DEBUG_OFFSET[self.version]
        exe_file.seek(debug_offset)
        val = exe_file.read_byte()
        if val == 0x16:
            val = 0x17
        elif val == 0x17:
            val = 0x16
        exe_file.seek(-1, 1)
        exe_file.write_byte(val)
        exe_file.save(self.exe)
