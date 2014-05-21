# BastionMod
#
# Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
# This work is free. You can redistribute it and/or modify it under the terms
# of the Do What The Fuck You Want To Public License, Version 2, as published
# by Sam Hocevar. See the COPYING file for more details.

import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from BastionLib.maps.map_file import MapFile
from document import Document
from logger import Logger


class MapFileDocument(Document):
    """
        Allows for the modification of a map file's properties.
    """

    UI_FILE = 'ui/map_file_document.ui'

    def __init__(self, module, f_path):
        """
            Creates a new document.
        """

        super().__init__(self.UI_FILE)
        self.module = module
        self.name = os.path.basename(f_path)[:-4]
        self.map_file = MapFile.from_file(f_path)

        # Set up the script editor.
        self.highlighter = ScriptHighlighter(
            self.script_editor.document())
        self.script_editor.textChanged.connect(self.script_changed)

        self.reset()
        Logger.info('Loaded map {}.'.format(self.name))

    def reset(self):
        """
            Sets the document to its default state.
        """

        script = ''.join(self.map_file.script).replace('\r', '\\r').strip()
        self.script_editor.setPlainText(script)

    def save(self):
        """
            Saves the document back to the file.
        """

        if not self.is_saved:
            text = self.script_editor.toPlainText()
            self.map_file.script = [s + '\n' for s in text.replace('\\r', '\r').split('\n')]
            self.map_file.save(self.module.bastion_folder.maps_files[self.name])
        super().save()

    def script_changed(self):
        """
            Called when the script text has been modified.
        """

        if self.parent():
            self.modify()

class ScriptHighlighter(QSyntaxHighlighter):
    """
        Highlights script code.
    """

    COMMENT_PATTERN = QRegExp("//.+")
    ACTION_PATTERN = QRegExp("^(\s+|\w*\s)\w+\s*")
    TRIGGER_PATTERN = QRegExp("^\w+(\s)*")

    def __init__(self, parent=None):
        """Sets the highlighter's properties."""

        super().__init__(parent)

        self.rules = []

        # Create the comment highlighter.
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.blue)
        comment_rule = (self.COMMENT_PATTERN, comment_format)
        self.rules.append(comment_rule)

        # Create the action highlighter.
        action_format = QTextCharFormat()
        action_format.setForeground(Qt.darkRed)
        action_rule = (self.ACTION_PATTERN, action_format)
        self.rules.append(action_rule)

        # Create the trigger highlighter.
        trigger_format = QTextCharFormat()
        trigger_format.setForeground(Qt.darkGreen)
        trigger_rule = (self.TRIGGER_PATTERN, trigger_format)
        self.rules.append(trigger_rule)

    def highlightBlock(self, text):
        """Highlights a comment block."""

        for rule in self.rules:
            expression = QRegExp(rule[0])
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule[1])
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)