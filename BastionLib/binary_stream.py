# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import io
import os
import struct


class BinaryStream(io.BytesIO):
    """
        Base class for binary files.
    """

    BIG_ENDIAN = '>'
    LITTLE_ENDIAN = '<'
    DEFAULT_ENDIAN = BIG_ENDIAN

    def __init__(self, data=None, endian=None):
        """
            Initializes a stream, optionally from some initial data.
        """

        if not endian:
            endian = self.DEFAULT_ENDIAN
        super().__init__(data)
        self._endian = endian

        # Create the basic reading functions.
        self.u = lambda f, l: struct.unpack(
            '{}{}'.format(self._endian, f), self.read(l)
        )
        self.read_byte = lambda: self.u('B', 1)[0]
        self.read_bool = lambda: self.u('?', 1)[0]
        self.read_short = lambda: self.u('h', 2)[0]
        self.read_ushort = lambda: self.u('H', 2)[0]
        self.read_int = lambda: self.u('i', 4)[0]
        self.read_uint = lambda: self.u('I', 4)[0]
        self.read_long = lambda: self.u('q', 8)[0]
        self.read_ulong = lambda: self.u('Q', 8)[0]
        self.read_float = lambda: self.u('f', 4)[0]
        self.read_double = lambda: self.u('d', 8)[0]
        self.read_vector2 = lambda: self.u('BB', 2)[0]

        # Create the basic writing functions.
        self.p = lambda f, d: self.write(
            struct.pack('{}{}'.format(self._endian, f), d)
        )
        self.write_byte = lambda d: self.p('B', d)
        self.write_bool = lambda d: self.p('?', d)
        self.write_short = lambda d: self.p('h', d)
        self.write_ushort = lambda d: self.p('H', d)
        self.write_int = lambda d: self.p('i', d)
        self.write_uint = lambda d: self.p('I', d)
        self.write_long = lambda d: self.p('q', d)
        self.write_ulong = lambda d: self.p('Q', d)
        self.write_float = lambda d: self.p('f', d)
        self.write_double = lambda d: self.p('d', d)
        self.write_vector2 = lambda d: self.write(d)

    def read_7BitEncodedInt(self):
        """
            Reads a 7BitEncodedInt.
        """

        returnValue = bitIndex = 0
        while bitIndex != 0x23:
            currentByte = self.read_byte()
            returnValue |= ((currentByte & 0x7F) << bitIndex) & 0xFFFFFFFF
            bitIndex += 7
            if currentByte & 0x80 == 0:
                return returnValue
        raise ValueError('Invalid 7BitEncodedInt.')

    def write_7BitEncodedInt(self, value):
        """
            Writes a 7BitEncodedInt.
        """

        num = value  
        while num >= 0x80:
            self.write_byte(num | 0x80)
            num = (num >> 7) & 0xFFFFFFFF
        self.write_byte(num)

    def read_color(self):
        """
            Loads a color from the stream.
        """

        color = self.read(4)
        return [color[2], color[1], color[0], color[3]]

    def write_color(self, color):
        """
            Writes a color from a list.
        """

        self.write((color[2], color[1], color[0], color[3]))

    def read_cstring(self):
        """
            Reads a null-terminated string.
        """

        cstring = ''
        while True:
            c = self.read_byte()
            if c == 0:
                break
            cstring += chr(c)
        return cstring

    def write_cstring(self, cstring):
        """
            Writes a null-terminated string.
        """

        self.write(cstring.encode('ascii'))
        self.write_byte(0)

    def read_string(self, len_size=1):
        """
            Reads a string whose length is specified in the first bytes.
        """

        if len_size is 1:
            l = self.read_7BitEncodedInt()
        elif len_size is 2:
            l = self.read_ushort()
        elif len_size is 4:
            l = self.read_uint()
        elif len_size is 8:
            l = self.read_ulong()
        else:
            raise ValueError('Invalid string length size.')
        return self.read(l).decode('ascii')

    def write_string(self, string, len_size=1):
        """
            Writes a string with its length specified at the beginning.
        """

        l = len(string)
        if len_size is 1:
            self.write_7BitEncodedInt(l)
        elif len_size is 2:
            self.write_ushort(l)
        elif len_size is 4:
            self.write_uint(l)
        elif len_size is 8:
            self.write_ulong(l)
        else:
            raise ValueError('Invalid string length size.')
        self.write(string.encode('ascii'))

    def read_string_list(self, len_size=1):
        """
            Reads a list of strings.
        """

        l = self.read_int()
        strings = []
        for i in range(l):
            strings.append(self.read_string(len_size))
        return strings

    def write_string_list(self, strings, len_size=1):
        """
            Writes an ordered list of strings.
        """

        self.write_int(len(strings))
        for string in strings:
            self.write_string(string, len_size)

    def read_int_list(self):
        """
            Reads a list of integers.
        """

        l = self.read_int()
        ints = []
        for i in range(l):
            ints.append(self.read_int())
        return ints

    def write_int_list(self, ints):
        """
            Writes an ordered list of integers.
        """

        self.write_int(len(ints))
        for integer in ints:
            self.write_int(integer)

    def save(self, file_path):
        """
            Saves the data to the specified file.
        """

        with open(file_path, 'wb') as f:
            f.write(self.getvalue())

    def from_file(file_path, endian=None):
        """
            Returns a new binary stream instance loaded from a file.
        """

        if not endian:
            endian = BinaryStream.DEFAULT_ENDIAN
        try:
            with open(file_path, 'rb') as f:
                name = os.path.splitext(os.path.basename(file_path))[0]
                return BinaryStream(f.read(), endian)
        except (OSError, IOError):
            return None
