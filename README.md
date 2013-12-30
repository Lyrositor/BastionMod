BastionMod
==========

Tool for modding [Supergiant Games'](http://supergiantgames.com/) video game *Bastion*. BastionMod lets you extract game data, edit it, and insert it back in.

Features:
  - Audio extraction (includes video game music and narration)
  - Graphics extraction (tilesets, character animations...)

License: [WTFPL](http://www.wtfpl.net/)

## Usage ##
**Note:** Before running BastionMod.py, make sure you've read the section entitled "C++ Modules".

Make sure you have installed [Python 3](http://python.org/) and [Pillow](http://python-imaging.github.io/) (or the Python Imaging Library for Python 3).

Run `BastionMod.py` from the terminal to start the program, with either the `-e` (extract) or `-c` (compile) argument, followed by the path to Bastion's folder and the path to the content to be extracted/extracted content.

### C++ Modules ###
BastionMod uses several Python modules written in C++ using Python's C API; these must be compiled before running BastionMod. The reason for this choice is speed: Python can be quite slow sometimes, and for speed-critical operations (such as decoding and encoding large amounts of binary data), C++ is more suited to the task.

To compile the CModules, run `build_CModules.py`. You'll need the latest development version of the [libsquish](https://code.google.com/p/libsquish/) library first:

    svn checkout http://libsquish.googlecode.com/svn/trunk/ libsquish-read-only

## Acknowledgements ##
Many thanks to Ali Scissons for his work on Bastion modding. His code has been invaluable. You can view it here: https://bitbucket.org/alisci01.
