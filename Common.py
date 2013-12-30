# BastionMod - Common
# Commons definitions used throughout BastionMod.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import struct

from BastionModule import *

def read_7BitEncodedInt(data):
    """Reads a 7BitEncodedInt to a numeric value."""

    returnValue = 0
    bitIndex = 0
    byteIndex = 0

    while (bitIndex != 0x23):
        currentByte = data[byteIndex]
        returnValue |= (currentByte & 0x7F) << bitIndex;
        byteIndex += 1
        bitIndex += 7

        if currentByte & 0x80 == 0:
            return returnValue, byteIndex

    return None, None

def read_string(stream, s_len_size=1):
    """Reads a string from a stream the first bytes to know its length."""

    s_len = struct.unpack('<H' if s_len_size is 2 else '<B',
        stream.read(s_len_size)
    )[0]
    if s_len:
        return stream.read(s_len).decode('ascii')
    else:
        return None

def F(b):
    """Formats a binary string to a hexadecimal representation."""

    return "".join([hex(x).upper()[2:].zfill(2) for x in tuple(b)])

# TODO: Remove this.
def D(i):
    if i is None:
        i = 0
    s = hex(i)[2:].upper().zfill(8)
    return "".join(reversed([s[i:i + 2].zfill(2) for i in range(0, len(s), 2)]))


class BastionModError(Exception):
    """Default error for BastionMod."""

    def __init__(self, msg='Unknown error.'):

        self.msg = msg


class AudioError(BastionModError):
    """Audio-specific error."""


class GraphicsError(BastionModError):
    """Graphics-specific error."""
