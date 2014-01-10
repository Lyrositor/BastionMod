# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

from ..binary_file import BaseBinaryRepresentation, BinaryProperty, Types
from ..binary_stream import BinaryStream


class WaveBank(BaseBinaryRepresentation):
    """
        Represents an XNA WaveBank.
    """

    ENDIAN = BinaryStream.LITTLE_ENDIAN
    VERSION = 0x5

    STREAMING = 'StreamingWaveBank'
    OGG_HEADER = b'OggS'

    _properties = (
        BinaryProperty('version', Types.INT, default=VERSION, equals=VERSION),
    )

    def __init__(self, name=None):
        """
            Registers the wave bank's properties, with an optional name.

            'name' is only useful to identify the wave bank and is not
            actually used.
        """

        super().__init__()
        self.files = []
        self.name = name

    def read(self, stream, streaming_dir=None):
        """
            Reads the wave bank's file data.
        """

        super().read(stream)

        # Get the file sizes.
        num = stream.read_uint()
        file_sizes = []
        for i in range(num):
            file_sizes.append(stream.read_ulong())

        # Load the file data.
        self.files = []
        if streaming_dir:
            for n, size in enumerate(file_sizes):
                o_path = os.path.join(streaming_dir, '{}.ogg'.format(n))
                with open(o_path, 'rb') as o:
                    ogg = o.read()
                    if ogg[:4] != WaveBank.OGG_HEADER:
                        raise ValueError('Invalid Ogg header.')
                    self.files.append(ogg)
        else:
            for size in file_sizes:
                ogg = stream.read(size)
                if ogg[:4] != WaveBank.OGG_HEADER:
                    raise ValueError('Invalid Ogg header.')
                self.files.append(ogg)

        return self

    def write(self, stream, streaming_dir=None):
        """
            Writes the wave bank's file data.
        """

        super().write(stream)
        stream.write_uint(len(self.files))
        for f in self.files:
            stream.write_ulong(len(f))
        if streaming_dir:
            for n, f in enumerate(self.files):
                self.write_ogg(streaming_dir, n)
        else:
            for f in self.files:
                stream.write(f)

    def write_ogg(self, output_dir, file_id):
        """
            Outputs one of the files to an Ogg file.
        """

        o_path = os.path.join(output_dir, '{}.ogg'.format(file_id))
        with open(o_path, 'wb') as f:
            f.write(self.files[file_id])

    def save(self, file_path, streaming_dir=None):
        """
            Saves the WaveBank to a file.
        """

        if streaming_dir:
            os.makedirs(streaming_dir, exist_ok=True)
        stream = BinaryStream(None, WaveBank.ENDIAN)
        self.write(stream, streaming_dir)
        stream.save(file_path)

    def from_file(file_path, streaming_dir=None):
        """
            Returns a new WaveBank, optionally with the "Streaming" directory
            path.
        """

        stream = BinaryStream.from_file(file_path, WaveBank.ENDIAN)
        if not stream:
            return None
        rep = WaveBank(os.path.splitext(os.path.basename(file_path))[0])
        rep.read(stream, streaming_dir)
        return rep
