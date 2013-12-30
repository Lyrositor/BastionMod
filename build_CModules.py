#!/usr/bin/env python3
# BastionMod - Build CModules
# Builds the C++ Python modules required for expensive operations.
#
# Copyright © 2013 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

from distutils.core import setup, Extension


bm_dxt = Extension(
    'bm_dxt',
    sources=['CModules/BM_Dxt.cpp'],
    libraries=['squish']
)

bm_lzx = Extension(
    'bm_lzx',
    sources=['CModules/BM_Lzx.cpp']
)

setup(
    name='BastionMod CModules',
    version='1.0',
    description='C++ Python modules for BastionMod.',
    ext_modules=[bm_dxt, bm_lzx]
)
