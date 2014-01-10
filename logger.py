# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import time


class Logger:

    INSTANCE = None

    # Output levels.
    ERROR_LEVEL = 0
    INFO_LEVEL = 1
    DEBUG_LEVEL = 2

    FORMAT = '[%H:%M:%S] {}'

    def __init__(self):
        """Initializes the logger to use an output source.

        Output should be a function accepting one message parameter."""

        self.level = Logger.INFO_LEVEL
        self.output = print

    def get():
        """Returns the singleton's instance."""

        if not Logger.INSTANCE:
            Logger.INSTANCE = Logger()
        return Logger.INSTANCE

    def write(msg):
        """Writes a formatted message."""

        Logger.get().output(time.strftime(Logger.FORMAT.format(msg)))

    def set_level(lvl):
        """Sets the logger's output level."""

        Logger.get().level = lvl

    def set_output(output):
        """Sets the logger's output function."""

        Logger.get().output = output

    def debug(msg):
        """Writes a debug message to the output device."""

        if Logger.get().level >= Logger.DEBUG_LEVEL:
            Logger.write(msg)

    def info(msg):
        """Writes an info message to the output device."""

        if Logger.get().level >= Logger.INFO_LEVEL:
            Logger.write(msg)

    def error(msg):
        """Writes an error message to the output device."""

        if Logger.get().level >= Logger.ERROR_LEVEL:
            Logger.write('ERROR: {}'.format(msg))
