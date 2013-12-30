# BastionMod - Bastion Module
# Base class for BastionMod modules.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

MODULES = []


class BastionModule:
    """Base class for BastionMod modules."""

    DATA_TYPE = 'unknown'

    CONTENT_DIR = ''
    EXTRACT_DIR = ''

    def __init__(self, debug=False):
        """Initializes the module."""

        self.debug = debug

    def extract(self, content_dir, extract_dir):
        """To be extended by sub-classes."""

        # Create the extract dir.
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)

    def compile(self, extract_dir, content_dir):
        """To be extended by sub-classes."""
