# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

from BastionLib.audio.wave_bank import WaveBank

INPUT1 = '/home/marc/Documents/Bastion/Bastion_Linux/Linux/Content/Audio/BastionWaveBank.xwb'
OUTPUT1 = 'tests/temp/BastionWaveBank.xwb'
INPUT2_1 = '/home/marc/Documents/Bastion/Bastion_Linux/Linux/Content/Audio/StreamingWaveBank.xwb'
INPUT2_2 = '/home/marc/Documents/Bastion/Bastion_Linux/Linux/Content/Audio/Streaming/'
OUTPUT2_1 = 'tests/temp/StreamingWaveBank.xwb'
OUTPUT2_2 = 'tests/temp/Streaming/'

w1 = WaveBank.from_file(INPUT1)
w1.save(OUTPUT1)

w2 = WaveBank.from_file(INPUT2_1, INPUT2_2)
w2.save(OUTPUT2_1, OUTPUT2_2)

os.execlp('vbindiff', '', INPUT1, OUTPUT1)
