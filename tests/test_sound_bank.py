# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

from BastionLib.audio.sound_bank import SoundBank

INPUT = '/home/marc/Documents/Bastion/Bastion_Linux/Linux/Content/Audio/' + SoundBank.NAME
OUTPUT = 'tests/temp/BastionSoundBank.xsb'

import time
t = time.time()
sb = SoundBank.from_file(INPUT)
sb.save(OUTPUT)
os.execlp('vbindiff', '', INPUT, OUTPUT)
