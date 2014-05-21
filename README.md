BastionMod
==========

<img src="http://lyros.net/bastion/BastionMod.png" alt="BastionMod" width="450" height="244" align="right" />Tool for modding [Supergiant Games'](http://supergiantgames.com/) video game *Bastion*. BastionMod lets you extract game data from Bastion, edit it, and insert it back in.

Features:
  - Audio extraction, modification and insertion,
  - Map editing.

License: [WTFPL](http://www.wtfpl.net/)

**WARNING:** BastionMod works mostly with the Linux version of Bastion's `Content` folder. It has limited modification capabilities on Windows: currently, only map editing is supported.

## Usage ##
**Note:** Before running BastionMod.py, make sure you've read the section entitled "C++ Modules".

Make sure you have installed [Python 3.3](http://python.org/) or higher, [PyQt 5](http://www.riverbankcomputing.co.uk/software/pyqt/download5) and [Pillow](http://python-imaging.github.io/) (or the Python Imaging Library for Python 3).

Run `BastionMod.py` to start the program.

### C++ Modules ###
BastionMod uses several Python modules written in C++ using Python's C API; these must be compiled before running BastionMod. The reason for this choice is speed: Python can be quite slow sometimes, and for speed-critical operations (such as decoding and encoding large amounts of binary data), C++ is more suited to the task.

To compile the CModules, run `build_CModules.py`. You'll need the latest development version of the [libsquish](https://code.google.com/p/libsquish/) library first:

    svn checkout http://libsquish.googlecode.com/svn/trunk/ libsquish-read-only

## Acknowledgements ##
Many thanks to Ali Scissons for his work on Bastion modding. His code has been invaluable. You can view it here: https://bitbucket.org/alisci01.