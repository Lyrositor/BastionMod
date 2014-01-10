# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from ..binary_file import BaseBinaryRepresentation, BinaryProperty, Types
from ..binary_stream import BinaryStream


class WaveBankFileLink(BaseBinaryRepresentation):
    """
        Represents a link to a wave bank file.
    """

    _properties = (
        BinaryProperty('bank_name', Types.STRING, default='BastionWaveBank', param=2),
        BinaryProperty('file_id', Types.UINT),
        BinaryProperty('unknown', Types.BYTE)
    )


class Track(BaseBinaryRepresentation):
    """
        Represents a track, a set of wave bank files to be played.
    """

    _properties = (
        BinaryProperty('files', WaveBankFileLink, repeat=Types.UINT),
        BinaryProperty('unknown', Types.BYTE, repeat=0x2a)
    )


class Sound(BaseBinaryRepresentation):
    """
        Represents an XNA sound, a set of tracks to be played.
    """

    _properties = (
        BinaryProperty('unknown1', Types.BYTE, repeat=4),
        BinaryProperty('unknown2', Types.BYTE, repeat=4),
        BinaryProperty('tracks', Track, repeat=Types.UINT),
        BinaryProperty('category', Types.STRING, default='Default', param=2),
        BinaryProperty('properties', Types.STRING_LIST, param=2, require='tracks'),
        BinaryProperty('reverb', Types.STRING, param=2, require='tracks'),
        BinaryProperty('unknown3', Types.BYTE, repeat=4)
    )


class Cue(BaseBinaryRepresentation):
    """
        Represents an XNA cue, a set of sounds to be played.
    """

    _properties = (
        BinaryProperty('name', Types.STRING, param=2),
        BinaryProperty('unknown1', Types.BYTE, repeat=4),
        BinaryProperty('sounds', Types.UINT, repeat=Types.UINT),
        BinaryProperty('unknown2', Types.BYTE, repeat=4)
    )


class SoundBank(BaseBinaryRepresentation):
    """
        Represents an XNA SoundBank.
    """

    ENDIAN = BinaryStream.LITTLE_ENDIAN
    NAME = 'BastionSoundBank.xsb'
    VERSION = 0x5

    _properties = (
        BinaryProperty('version', Types.INT, default=VERSION, equals=VERSION),
        BinaryProperty('sounds', Sound, repeat=Types.ULONG),
        BinaryProperty('cues', Cue, repeat='eof')
    )
