# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import imp
import importlib as implib
import os
import sys

from logger import *

MODULE_LIST_FILE = os.path.join('..', 'resources', 'module_list.txt')

def load_modules(bastion_folder, window):
    """Imports all requested modules."""

    modules = []
    cur_path = os.path.dirname(os.path.realpath(__file__))
    f_path = os.path.join(cur_path, MODULE_LIST_FILE)
    try:
        with open(f_path) as f:
            for line in f.readlines():
                name = line.rstrip()
                if name.startswith('#') or not name:
                    continue
                Logger.info('Loading module {}...'.format(name))
                full_name = '.'.join((__name__, name))
                try:
                    if full_name in sys.modules:
                        module = implib.import_module(full_name)
                    else:
                        module = implib.import_module(full_name)
                        imp.reload(module)
                except ImportError:
                    Logger.error(
                        'Failed to find module {}. Not loading.'.format(name)
                    )
                else:
                    bastion_module = getattr(module, name)
                    m = bastion_module(bastion_folder, window)
                    modules.append(m)
                    Logger.info('Loaded module {}.'.format(name))
    except (OSError, IOError):
        Logger.error('Failed to find module list. Not loading any modules.')
    return modules
