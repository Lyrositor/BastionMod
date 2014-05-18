# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import sys

from BastionMod import BastionModApp
from logger import Logger

app = BastionModApp(sys.argv)
Logger.set_level(Logger.INFO_LEVEL)
Logger.set_output(app.print)
app.open_bastion_folder('../Bastion_Linux')
app.main.file_browser.expandAll()
result = app.exec_()
sys.exit(result)
