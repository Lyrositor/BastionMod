#!/usr/bin/env python3
# BastionMod
# Allows for the modding of Bastion, by Supergiant games.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from argparse import *
import os
from time import time

from Audio import *
from Common import *
from Graphics import *

def extract_data(content_dir, extract_dir, debug):
    """Extracts Bastion game data from its 'Content' directory."""

    # Run all the modules' extraction procedures.
    for m in MODULES:
        print('Extracting {}.'.format(m.DATA_TYPE))
        m_content_dir = os.path.join(content_dir, m.CONTENT_DIR)
        m_extract_dir = os.path.join(extract_dir, m.EXTRACT_DIR)
        module = m(debug)
        try:
            module.extract(m_content_dir, m_extract_dir)
        except BastionModError as e:
            raise BastionModError('Failed to extract {}: {}'.format(
                m.DATA_TYPE, e))
        else:
            print('Extracted {}.'.format(m.DATA_TYPE))

def compile_data(extract_dir, content_dir, debug):
    """Compiles the extracted data back into the 'Content' directory."""

if __name__ == '__main__':

    # Get the arguments which were passed.
    parser = ArgumentParser(description='BastionMod')
    parser.add_argument('content', metavar='CONTENT',
        help="The path to Bastion's 'Content' directory."
    )
    parser.add_argument('extracted', metavar='EXTRACTED',
        help='The path to the directory containing the extracted files.'
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('-e', action='store_const', const=True, default=False,
        help='Extract data from Bastion.')
    mode.add_argument('-c', action='store_const', const=True, default=False,
        help='Compile data back to Bastion.')
    parser.add_argument('-d', action='store_const', const=True, default=False,
        help='Enable debugging output.')
    args = parser.parse_args()

    try:
        start_time = time()
        if args.e:
            print("Extracting from '{}'.".format(args.content))
            extract_data(args.content, args.extracted, args.d)
            print('Extraction complete.')
        else:
            print("Compiling to '{}'.".format(args.content))
            compile_data(args.extracted, args.content, args.d)
            print('Compilation complete.')
        print('Time: {}s'.format(int(time() - start_time)))
    except KeyboardInterrupt:
        print("\rBastionMod interrupted.")
    except BastionModError as e:
        print('Error: {}'.format(e.msg))
