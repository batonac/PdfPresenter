#!/usr/bin/env python
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

Created on Jul 18, 2011

@author: Alex Passfall
"""
from __future__ import annotations

import codecs
import os.path
import sys
import threading
import time
from typing import Optional

import qpageview
import qpageview.pdf
from PyQt6 import QtCore, QtGui, QtWidgets


class QtPDFViewer(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.pdfImages: dict[int, QtGui.QImage] = {}
        self.currentPage: int = 0
        self.doc: Optional[qpageview.pdf.PdfDocument] = None
        self.pages: list[qpageview.pdf.PdfPage] = []
        self.initUI()

        self.presenterWindow = ProjectorView(self)
        self.presenterWindow.show()

    def updateUhr(self, time: str) -> None:
        self.uhr.display(time)

    def initUI(self) -> None:

        self.current = PDFView(0, self)
        # self.current.resize(500,500)
        self.next = PDFView(1, self)

        viewbox = QtWidgets.QHBoxLayout()
        viewbox.addWidget(self.current, 1)
        viewbox.addWidget(self.next, 1)

        self.uhr = QtWidgets.QLCDNumber()
        self.uhr.display("00:00")
        bStart = QtWidgets.QPushButton("Start")
        bStop = QtWidgets.QPushButton("Stop")
        bStart.clicked.connect(self.startButton)
        bStop.clicked.connect(self.stopButton)

        clockbox = QtWidgets.QVBoxLayout()
        clockbox.addWidget(self.uhr)
        clockbuttonbox = QtWidgets.QHBoxLayout()
        clockbuttonbox.addWidget(bStart)
        clockbuttonbox.addWidget(bStop)
        clockbox.addLayout(clockbuttonbox)

        self.notes = Notes()
        bottombox = QtWidgets.QHBoxLayout()
        bottombox.addLayout(clockbox)
        bottombox.addWidget(self.notes)

        mainbox = QtWidgets.QVBoxLayout()
        mainbox.addLayout(viewbox)
        mainbox.addLayout(bottombox, 0)
        self.setLayout(mainbox)
        self.ptimer = PauseableTimer(self.updateUhr)

    def startButton(self) -> None:
        self.ptimer.start()

    def stopButton(self) -> None:
        self.ptimer.stop()

    def renderImages(self) -> None:
        """Render PDF pages to images for display."""
        self.pdfImages = {}
        if self.doc is None or not self.pages:
            return

        num_pages = len(self.pages)
        target_width = self.presenterWindow.width()
        target_height = self.presenterWindow.height()

        for i in range(num_pages):
            print(f"Rendering Page {i+1}/{num_pages}")
            page = self.pages[i]

            # Get page size in points
            page_size = page.pageSize()

            # Calculate scale to fit in presenter window
            scale_w = target_width / page_size.width()
            scale_h = target_height / page_size.height()
            scale = min(scale_w, scale_h)

            # Render at appropriate DPI
            dpi = 72 * scale

            # Use the page's render method to get a QImage
            width = int(page_size.width() * scale)
            height = int(page_size.height() * scale)

            image = page.renderer._render_image(
                page.document, page.pageNumber, dpi, dpi, width, height
            )
            self.pdfImages[i] = image

        self.update()
        self.presenterWindow.update()

    def load(self, file: str) -> None:
        """Load a PDF document."""
        self.doc = qpageview.pdf.PdfDocument(file)
        self.pages = list(self.doc.pages())
        self.renderImages()

    def showFileDialog(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf)"
        )
        if filename != "":
            self.load(filename)
            self.notes.read(filename)
            self.notes.show(self.currentPage)

    def prevPage(self) -> None:
        if self.currentPage > 0:
            self.currentPage -= 1
            self.update()
            self.notes.show(self.currentPage)

    def nextPage(self) -> None:
        if self.pages and self.currentPage + 1 < len(self.pages):
            self.currentPage += 1
            self.update()
            self.notes.show(self.currentPage)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_S and (
            event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        ):
            self.notes.save()


class PDFView(QtWidgets.QWidget):
    def __init__(self, offset: int, viewer: QtPDFViewer):
        super().__init__(viewer)
        self.offset = offset
        self.viewer = viewer

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(600, 600)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        page_num = self.viewer.currentPage + self.offset
        if page_num in self.viewer.pdfImages:
            image = self.viewer.pdfImages[page_num]
            # Scale image to fit widget while maintaining aspect ratio
            target = QtCore.QRectF(0, 0, self.width(), self.height())
            source = QtCore.QRectF(0, 0, image.width(), image.height())

            # Calculate scaling to fit
            scale_w = target.width() / source.width()
            scale_h = target.height() / source.height()
            scale = min(scale_w, scale_h)

            # Center the image
            scaled_w = source.width() * scale
            scaled_h = source.height() * scale
            x = (target.width() - scaled_w) / 2
            y = (target.height() - scaled_h) / 2

            dest_rect = QtCore.QRectF(x, y, scaled_w, scaled_h)
            painter.drawImage(dest_rect, image)
        else:
            # Draw placeholder
            painter.fillRect(self.rect(), QtCore.Qt.GlobalColor.lightGray)


class ProjectorView(QtWidgets.QMainWindow):
    def __init__(self, viewer: QtPDFViewer):
        super().__init__(viewer)
        self.viewer = viewer
        self.initUI()

    def initUI(self) -> None:
        self.resize(640, 480)

        self.setWindowTitle("QtPDFPresenter - Presentation Window")

        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.ColorRole.Window, QtCore.Qt.GlobalColor.black)
        self.setPalette(p)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.viewer.renderImages()
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        if self.viewer.currentPage in self.viewer.pdfImages:
            image = self.viewer.pdfImages[self.viewer.currentPage]
            # Center the image in the window
            x = int((self.width() - image.width()) / 2)
            y = int((self.height() - image.height()) / 2)
            painter.drawImage(x, y, image)

    def toggleFullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_F11 or event.key() == QtCore.Qt.Key.Key_F:
            self.toggleFullscreen()
        elif event.key() == QtCore.Qt.Key.Key_Q:
            self.close()
            self.viewer.close()
            self.viewer.ptimer.stop()
        elif event.key() == QtCore.Qt.Key.Key_O:
            self.viewer.showFileDialog()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.viewer.prevPage()
            self.update()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.viewer.nextPage()
            self.update()


class Notes(QtWidgets.QTextEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.notes: dict[str, str] = {}
        self.notesfile: Optional[str] = None
        self.setReadOnly(True)
        self.setFontPointSize(16)
        self.current: Optional[str] = None
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


class PauseableTimer:
    def __init__(self, updatefunc):
        self.old_seconds: float = 0.0
        self.reference: float = 0.0
        self.enable: bool = False
        self.updatefunc = updatefunc

    def incrementer(self) -> None:
        self.updatefunc(self.formatTime(time.time() - self.reference + self.old_seconds))
        if self.enable:
            threading.Timer(0.5, self.incrementer).start()
        else:
            self.old_seconds += time.time() - self.reference

    def start(self) -> None:
        self.reference = time.time()
        self.enable = True
        self.incrementer()

    def stop(self) -> None:
        self.enable = False

    def formatTime(self, seconds: float) -> str:
        return "{0:02d}:{1:02d}".format(int(seconds / 60), int(seconds % 60))


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    viewer = QtPDFViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
