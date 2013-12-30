# BastionMod - Audio
# Manages the extraction and compilation of audio files from Bastion.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import glob
import os
import struct
import xml.dom.minidom as X

from Common import *


class SoundBank:
    """Manages all sounds, including narration and music.

    Stored in XSB files."""

    FILE = 'BastionSoundBank.xsb'
    VERSION = 0x5

    def __init__(self, file_path):
        """Opens the sound bank."""

        self.version = 0
        self.num_sounds = 0

        try:
            with open(file_path, 'rb') as f:
                if os.path.splitext(file_path)[1] == '.xsb':
                    self.data = self.parse_xsb_file(f)
                elif os.path.splitext(file_path)[1] == '.xml':
                    self.data = self.parse_xml_file(f)
                else:
                    raise AudioError('Invalid sound bank file.')
        except (OSError, IOError):
            raise AudioError('Failed to open sound bank file.')

    def parse_xsb_file(self, f):
        """Parses an XSB file for sound bank entries."""

        data = []

        # Load the XSB header.
        self.version, self.num_sounds = struct.unpack('<IQ', f.read(0xC))
        if self.version != SoundBank.VERSION:
            raise AudioError('Invalid XSB version.')

        # Load the sounds.
        n = 0
        while n < self.num_sounds:

            # Load the sound entries.
            u1 = f.read(4)
            u2 = f.read(4)
            entries_num = struct.unpack('<I', f.read(0x4))[0]
            entries = []
            for e in range(0, entries_num):
                files_num = struct.unpack('<I', f.read(0x4))[0]
                files = []
                for f_i in range(0, files_num):
                    bank_name = read_string(f, 2)
                    file_num = struct.unpack('<Ix', f.read(0x5))[0]
                    files.append({'Bank': bank_name, 'Id': file_num})
                u3 = f.read(0x2A)  # Unknown data.
                entries.append({'Files': files, 'Unknown3': u3})
            category = read_string(f, 2)

            # Load the sound's properties.
            properties = reverb = None
            if entries_num:
                properties_num = struct.unpack('<I', f.read(0x4))[0]
                properties = []
                for prop in range(0, properties_num):
                    prop_name = read_string(f, 2)
                    properties.append(prop_name)

                reverb = read_string(f, 2)

            u4 = f.read(0x4)  # Unknown data.

            # Prepare the data before returning it.
            sound = {
                'Unknown1': u1,
                'Unknown2': u2,
                'Entries': entries,
                'Category': category,
                'Properties': properties,
                'Reverb': reverb,
                'Unknown4': u4,

                # The following will be filled during the name loop.
                'Name': None,
                'Unknown5': None,
                'Unknown6': None
            }
            data.append(sound)
            n += 1

        # Load the sounds' names.
        while f.read(1):
            f.seek(-1, 1)
            name = read_string(f, 2)
            u5 = f.read(4)
            num_data_num = struct.unpack('<I', f.read(4))[0]
            data_nums = []
            for i in range(0, num_data_num):
                data_num = struct.unpack('<I', f.read(4))[0]
                data_nums.append(data_num)
            u6 = f.read(4)
            for data_num in data_nums:
                data[data_num]['Name'] = name
                data[data_num]['Unknown5'] = u5
                data[data_num]['Unknown6'] = u6

        return data

    def save_xsb(self, file_path):
        """Saves the sound bank's data to an XSB file."""

        try:
            f = open(file_path, 'wb')
        except (OSError, IOError):
            raise AudioError('Failed to save Sound Bank file for writing.')
        f.close()

    def save_xml(self, file_path):
        """Saves the sound bank's data to an XML file."""

        # Build the XML data.
        impl = X.getDOMImplementation()
        doc = impl.createDocument(None, 'SoundBank', None)
        root = doc.documentElement
        for i, b in enumerate(self.data):
            sound = doc.createElement('Sound')
            sound.setAttribute('Id', str(i))
            if b['Name'] is not None:
                sound.setAttribute('Name', str(b['Name']))
            if b['Category'] is not None:
                sound.setAttribute('Category', str(b['Category']))
            if b['Reverb'] is not None:
                reverb = doc.createElement('Reverb')
                reverb.appendChild(doc.createTextNode(str(b['Reverb'])))
                sound.appendChild(reverb)

            # Add the entries.
            if b['Entries'] is not None:
                for e in b['Entries']:
                    entry = doc.createElement('Entry')
                    for s in e['Files']:
                        file_e = doc.createElement('File')
                        file_e.setAttribute('Bank', str(s['Bank']))
                        file_e.setAttribute('Id', str(s['Id']))
                        entry.appendChild(file_e)
                    unknown3 = doc.createElement('RawData')
                    unknown3.setAttribute('Id', '3')
                    unknown3.setAttribute('Value', F(e['Unknown3']))
                    entry.appendChild(unknown3)
                    sound.appendChild(entry)

            # Add the unknown blocks of data.
            for u in ('1', '2', '4', '5', '6'):
                if b['Unknown' + u] is not None:
                    unknown = doc.createElement('RawData')
                    unknown.setAttribute('Id', u)
                    unknown.setAttribute('Value', F(b['Unknown' + u]))
                    sound.appendChild(unknown)

            root.appendChild(sound)

        # Write the XML data.
        xml_data = doc.toprettyxml(encoding='utf-8')
        try:
            with open(file_path, 'wb') as f:
                f.write(xml_data)
        except (OSError, IOError):
            raise AudioError('Failed to write XML Sound Bank.')


class WaveBank:
    """Stores the sizes and (usually) the data of sound files.

    Stored in XWB files."""

    VERSION = 0x5

    def __init__(self, file_path, streaming_dir=None):
        """Opens the wave bank."""

        self.version = 0
        self.num_files = 0
        self.name = os.path.splitext(os.path.basename(file_path))[0]

        try:
            with open(file_path, 'rb') as f:
                self.files = self.parse_file(f, streaming_dir)
        except (OSError, IOError):
            raise AudioError('Failed to open sound bank file.')

    def parse_file(self, f, streaming_dir):
        """Parses an XWB file for Ogg files."""

        files = []

        # Load the XWB header.
        self.version, self.num_files = struct.unpack('<II', f.read(0x8))
        if self.version != WaveBank.VERSION:
            raise AudioError('Invalid XWB version.')

        # Load the audio files.
        file_sizes = []
        for i in range(0, self.num_files):
            file_sizes.append(struct.unpack('<Q', f.read(0x8))[0])

        # Either load the files from the same file, or load their individual
        # streaming files.
        if self.name != 'StreamingWaveBank':
            for size in file_sizes:
                files.append(f.read(size))
        elif streaming_dir:
            for i, size in enumerate(file_sizes):
                s_path = os.path.join(streaming_dir, '{}.ogg'.format(i))
                try:
                    with open(s_path, 'rb') as s:
                        files.append(s.read())
                except (OSError, IOError):
                    raise AudioError('Failed to open streaming audio file.')

        return files

    def write_ogg(self, file_id, file_path):
        """Writes the file to an Ogg file."""

        try:
            data = self.files[file_id]
        except IndexError:
            raise AudioError('The specified file could not be found.')
        try:
            with open(file_path, 'wb') as f:
                f.write(data)
        except (OSError, IOError):
            raise AudioError('Failed to write audio file.')

class Audio(BastionModule):
    """Extracts and compiles audio files."""

    DATA_TYPE = 'audio'

    CONTENT_DIR = 'Audio'
    EXTRACT_DIR = 'Audio'

    def extract(self, audio_dir, extract_dir):
        """Extracts the audio data."""

        super().extract(audio_dir, extract_dir)

        # Load the sound bank data and write it to XML.
        sound_bank = SoundBank(os.path.join(audio_dir, SoundBank.FILE))
        xml_path = os.path.join(extract_dir, 'SoundBank.xml')
        sound_bank.save_xml(xml_path)

        # Load the wave bank data.
        xwb_files = glob.glob(os.path.join(audio_dir, '*.xwb'))
        wave_banks = {}
        for f in xwb_files:
            wave_bank = WaveBank(f, os.path.join(audio_dir, 'Streaming'))
            wave_banks[wave_bank.name] = wave_bank

        # Output the files into their categories' folders.
        for sound in sound_bank.data:
            sound_dir = os.path.join(extract_dir, sound['Category'])
            for entry in sound['Entries']:
                file_dir = os.path.join(sound_dir, sound['Name'])
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                for file_e in entry['Files']:
                    file_path = os.path.join(file_dir,
                        '{}_{}.ogg'.format(file_e['Bank'], file_e['Id']))
                    bank = wave_banks[file_e['Bank']]
                    bank.write_ogg(file_e['Id'], file_path)

MODULES.append(Audio)
