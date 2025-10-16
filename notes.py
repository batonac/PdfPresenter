"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import codecs
import os.path

from PySide6 import QtWidgets


class Notes(QtWidgets.QTextEdit):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.notes: dict[str, str] = {}
        self.notesfile: str | None = None
        self.current: str | None = None
        self.setReadOnly(True)
        self.setFontPointSize(16)
        self.textChanged.connect(self.textEdited)

    def read(self, filename: str) -> None:
        self.notesfile = str(filename) + ".notes"
        self.setReadOnly(False)
        if os.path.isfile(self.notesfile):
            with codecs.open(self.notesfile, encoding="utf-8", mode="r") as f:
                print("Reading notes...")
                slide = None
                for line in f:
                    if "==XXslide" in line:
                        slide = line.strip()
                        self.notes[slide] = ""
                    elif slide is not None:
                        self.notes[slide] += line

    def save(self) -> None:
        if len(self.notes) > 0 and self.notesfile:
            print("Saving notes")
            with codecs.open(self.notesfile, encoding="utf-8", mode="w") as f:
                for slide_id in self.notes.keys():
                    f.write(slide_id)
                    f.write("\n")
                    f.write(self.notes[slide_id])
                    f.write("\n")
        else:
            print("No notes to save!")

    def show(self, slide: int) -> None:
        self.current = "==XXslide" + str(slide)
        if self.current in self.notes:
            self.setPlainText(self.notes[self.current])
        else:
            self.setPlainText("")

    def textEdited(self) -> None:
        if self.current is not None:
            self.notes[self.current] = str(self.toPlainText())
