# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

def format_hex(data):
    """
        Formats the binary data as readable hex data.
    """

    return " ".join([hex(b)[2:].upper().zfill(2) for b in data])

def deformat_hex(data):
    """
        Converts the formatted hex data to a list of integers.
    """

    return [int(b, 16) for b in data.split()]
