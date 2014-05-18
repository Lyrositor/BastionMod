# BastionLib
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from .binary_stream import BinaryStream


class Types:

    BYTE = 'byte'
    SHORT = 'short'
    USHORT = 'ushort'
    INT = 'int'
    UINT = 'uint'
    LONG = 'long'
    ULONG = 'ulong'
    _7BitEncodedInt = '7BitEncodedInt'

    FLOAT = 'float'
    DOUBLE = 'double'

    BOOL = 'bool'

    VECTOR2 = 'vector2'
    COLOR = 'color'

    CSTRING = 'cstring'
    STRING = 'string'

    INT_LIST = 'int-list'
    STRING_LIST = 'string-list'

    INTEGERS = (BYTE, SHORT, USHORT, INT, UINT, LONG, ULONG, _7BitEncodedInt)
    FLOATING_POINTS = (FLOAT, DOUBLE)
    VECTORS = (VECTOR2, COLOR)
    STRINGS = (STRING, CSTRING)
    LISTS = (INT_LIST, STRING_LIST)


class BaseBinaryRepresentation:
    """
        A base representation of a binary structure, to be subclassed.
    """

    ENDIAN = BinaryStream.DEFAULT_ENDIAN

    def __init__(self):
        """
            Prepares the binary representation.
        """

        self._values = {}
        for prop in self._properties:
            self._values[prop.name] = prop.default

    def __getattr__(self, name):
        """
            Returns normal values and current properties' values.
        """

        if name != '_values':
            values = self.__dict__['_values']
            if name in values:
                return values[name]
        return self.__dict__[name]

    def __setattr__(self, name, value):
        """
            Updates properties' current values and normal values.
        """

        if name != '_values':
            values = self.__dict__['_values']
            if name in values:
                values[name] = value
                return
        self.__dict__[name] = value

    def read(self, stream):
        """
            Reads the data from the stream into the representation.
        """

        for prop in self._properties:
            if prop.require:
                self._values[prop.name] = prop.read(stream, self._values[prop.require])
            else:
                self._values[prop.name] = prop.read(stream)
        return self

    def write(self, stream):
        """
            Writes the data from the representation to a stream.
        """

        for prop in self._properties:
            if prop.require:
                prop.write(self._values[prop.name], stream, self._values[prop.require])
            else:
                prop.write(self._values[prop.name], stream)

    def save(self, file_path, endian=None):
        """
            Saves the representation's data to a file.
        """

        if not endian:
            endian = self.ENDIAN
        stream = BinaryStream(None, endian)
        self.write(stream)
        stream.save(file_path)

    @classmethod
    def from_file(cls, file_path, endian=None):
        """
            Reads a new binary representation from the file.
        """

        if not endian:
            endian = cls.ENDIAN
        stream = BinaryStream.from_file(file_path, endian)
        if not stream:
            return None
        rep = cls()
        rep.read(stream)
        return rep


class BinaryProperty:
    """
        Represents a binary-stored property.

        Properties provide a convenient way to read and write to a stream.
        While they do not hold any values, they describe the way a value
        should be read or written to a binary stream.
    """

    r = {
        Types.BYTE: lambda s: s.read_byte(),
        Types.SHORT: lambda s: s.read_short(),
        Types.USHORT: lambda s: s.read_ushort(),
        Types.INT: lambda s: s.read_int(),
        Types.UINT: lambda s: s.read_uint(),
        Types.LONG: lambda s: s.read_long(),
        Types.ULONG: lambda s: s.read_ulong(),
        Types._7BitEncodedInt: lambda s: s.read_7BitEncodedInt(),
        Types.FLOAT: lambda s: s.read_float(),
        Types.DOUBLE: lambda s: s.read_double(),
        Types.BOOL: lambda s: s.read_bool(),
        Types.VECTOR2: lambda s: s.read_vector2(),
        Types.COLOR: lambda s: s.read_color(),
        Types.CSTRING: lambda s: s.read_cstring(),
        Types.INT_LIST: lambda s: s.read_int_list()
    }
    w = {
        Types.BYTE: lambda v, s: s.write_byte(v),
        Types.SHORT: lambda v, s: s.write_short(v),
        Types.USHORT: lambda v, s: s.write_ushort(v),
        Types.INT: lambda v, s: s.write_int(v),
        Types.UINT: lambda v, s: s.write_uint(v),
        Types.LONG: lambda v, s: s.write_long(v),
        Types.ULONG: lambda v, s: s.write_ulong(v),
        Types._7BitEncodedInt: lambda v, s: s.write_7BitEncodedInt(v),
        Types.FLOAT: lambda v, s: s.write_float(v),
        Types.DOUBLE: lambda v, s: s.write_double(v),
        Types.BOOL: lambda v, s: s.write_bool(v),
        Types.VECTOR2: lambda v, s: s.write_vector2(v),
        Types.COLOR: lambda v, s: s.write_color(v),
        Types.CSTRING: lambda v, s: s.write_cstring(v),
        Types.INT_LIST: lambda v, s: s.write_int_list(v)
    }

    def __init__(self,
        name,
        data_type,
        default=None,
        equals=None,
        repeat=None,
        param=None,
        require=None):
        """
            Creates a new property with the specified values.
        """

        self.name = name
        self.data_type = data_type
        self.repeat = repeat
        if default is not None:
            self.default = default
        else:
            self.default = self.get_default(data_type, self.repeat)
        self.equals = equals
        self.param = param
        self.require = require
        self.read_one = self.get_read_method()
        self.write_one = self.get_write_method()

    def get_default(self, data_type, repeat=None):
        """
            Returns the standard default value for a primitive data-type.
        """

        if repeat is not None:
            if isinstance(repeat, int):
                return [self.get_default(data_type)] * repeat
            return []
        if isinstance(data_type, type):
            return data_type()
        elif data_type in Types.INTEGERS:
            return 0
        elif data_type in Types.FLOATING_POINTS:
            return 0.0
        elif data_type == Types.BOOL:
            return False
        elif data_type == Types.VECTOR2:
            return [0] * 2
        elif data_type == Types.COLOR:
            return [0] * 4
        elif data_type in Types.STRINGS:
            return ''
        elif data_type in Types.LISTS:
            return []
        else:
            return None

    def get_read_method(self):
        """
            Determines the correct method to read the value from a stream.
        """

        if self.data_type in self.r:
            return lambda s: self.r[self.data_type](s)

        elif self.data_type == Types.STRING:
            return lambda s: s.read_string(self.param)

        elif self.data_type == Types.STRING_LIST:
            return lambda s: s.read_string_list(self.param)

        elif isinstance(self.data_type, type):
            return lambda s: self.data_type().read(s)

        return lambda s: self.default

    def get_write_method(self):
        """
            Determines the correct method to write a value to a stream.
        """

        if self.data_type in self.w:
            return lambda v, s: self.w[self.data_type](v, s)

        elif self.data_type == Types.STRING:
            return lambda v, s: s.write_string(v, self.param)

        elif self.data_type == Types.STRING_LIST:
            return lambda v, s: s.write_string_list(v, self.param)

        elif isinstance(self.data_type, type):
            return lambda v, s: v.write(s)

        return lambda v, s: None

    def read(self, s, require=None):
        """
            Reads a new value from a stream and returns it.
        """

        # Check to see if the required value evaluates to True.
        value = self.default
        if self.require and not require:
            return value

        # Check to see if the value is repeated, or if only one should be
        # read.
        if isinstance(self.repeat, str):
            if self.repeat == 'eof':
                value = []
                while s.read(1):
                    s.seek(-1, 1)
                    value.append(self.read_one(s))

            elif self.repeat in Types.INTEGERS:
                value = [self.read_one(s) for n in range(self.r[self.repeat](s))]

        elif isinstance(self.repeat, int):
            value = [self.read_one(s) for n in range(self.repeat)]

        else:
            value = self.read_one(s)

        # Check to see if the value should be equal to a value.
        if self.equals is not None and value != self.equals:
            raise ValueError('Invalid {} value: {}'.format(self.name, value))

        return value

    def write(self, value, s, require=None):
        """
            Writes the current value to the stream.
        """

        # Check to see if the required value evaluates to True.
        if self.require and not require:
            return

        # Check to see if the value is repeated, or if only one should be
        # written (and how).
        if isinstance(self.repeat, str):
            if self.repeat == 'eof':
                for v in value:
                    self.write_one(v, s)

            elif self.repeat in Types.INTEGERS:
                self.w[self.repeat](len(value), s)  # Write the counter.
                for v in value:
                    self.write_one(v, s)

        elif isinstance(self.repeat, int):
            for n in range(self.repeat):
                self.write_one(value[n], s)

        else:
            self.write_one(value, s)
