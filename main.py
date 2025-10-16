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
"""
from __future__ import annotations

import sys
from typing import Optional

import qpageview
import qpageview.pdf
from PyQt6 import QtCore, QtGui, QtWidgets

from notes import Notes
from projector_view import ProjectorView
from slide_organizer import SlideOrganizer
from timer import PauseableTimer


class QtPDFViewer(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.pdfImages: dict[int, QtGui.QImage] = {}
        self.thumbnails: dict[int, QtGui.QImage] = {}
        self.slideOrder: list[int] = []  # Order of slides for presentation
        self.currentPage: int = 0
        self.verticalOffset: float = 0.0
        self.doc: Optional[qpageview.pdf.PdfDocument] = None
        self.pages: list[qpageview.pdf.PdfPage] = []
        self.initUI()

        self.presenterWindow = ProjectorView(self)
        self.presenterWindow.show()

    def updateUhr(self, time: str) -> None:
        self.uhr.display(time)

    def initUI(self) -> None:

        # Replace the two-panel view with a slide organizer
        self.slideOrganizer = SlideOrganizer(self)

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
        mainbox.addWidget(self.slideOrganizer, 1)
        mainbox.addLayout(bottombox, 0)
        self.setLayout(mainbox)
        self.ptimer = PauseableTimer(self.updateUhr)

    def startButton(self) -> None:
        self.ptimer.start()

    def stopButton(self) -> None:
        self.ptimer.stop()

    def renderImages(self) -> None:
        """Render PDF pages to images for display at full width."""
        self.pdfImages = {}
        self.thumbnails = {}
        if self.doc is None or not self.pages:
            return

        num_pages = len(self.pages)

        # Get the window width - we'll render at full width
        target_width = self.presenterWindow.width()

        # Render at high DPI for quality
        render_dpi = 200.0

        # Thumbnail size for organizer
        thumb_width = 200

        print(f"Rendering at {render_dpi} DPI for width: {target_width}")

        for i in range(num_pages):
            print(f"Rendering Page {i+1}/{num_pages}")
            page = self.pages[i]

            # Get page size in points (72 DPI)
            page_size = page.pageSize()

            # Calculate the size at our high DPI
            render_width = int(page_size.width() / 72.0 * render_dpi)
            render_height = int(page_size.height() / 72.0 * render_dpi)

            # Render at high resolution
            image = page.renderer._render_image(
                page.document, page.pageNumber, render_dpi, render_dpi, render_width, render_height
            )

            # Scale to fit the target width (maintain aspect ratio)
            scale = target_width / render_width
            scaled_width = target_width
            scaled_height = int(render_height * scale)

            scaled_image = image.scaled(
                scaled_width,
                scaled_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )

            self.pdfImages[i] = scaled_image

            # Create thumbnail
            thumb_scale = thumb_width / render_width
            thumb_height = int(render_height * thumb_scale)
            thumbnail = image.scaled(
                thumb_width,
                thumb_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnails[i] = thumbnail

        self.update()
        self.slideOrganizer.updateThumbnails()
        self.presenterWindow.update()

    def load(self, file: str) -> None:
        """Load a PDF document."""
        self.doc = qpageview.pdf.PdfDocument(file)
        self.pages = list(self.doc.pages())
        self.slideOrder = list(range(len(self.pages)))  # Initialize with all pages in order
        self.renderImages()

    def showFileDialog(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf)"
        )
        if filename != "":
            self.load(filename)
            self.notes.read(filename)
            self.notes.show(self.currentPage)

    def getCurrentSlideIndex(self) -> int:
        """Get the actual page number for the current presentation position."""
        if 0 <= self.currentPage < len(self.slideOrder):
            return self.slideOrder[self.currentPage]
        return 0

    def prevPage(self) -> None:
        """Navigate to previous page or scroll up if at top of tall page."""
        if self.verticalOffset > 0.0:
            self.verticalOffset = 0.0
            self.update()
            self.presenterWindow.update()
        elif self.currentPage > 0:
            self.currentPage -= 1
            if self._isPageTall(self.getCurrentSlideIndex()):
                self.verticalOffset = 1.0
            else:
                self.verticalOffset = 0.0
            self.update()
            self.notes.show(self.getCurrentSlideIndex())
            self.presenterWindow.update()
            self.slideOrganizer.setCurrentSlide(self.currentPage)

    def nextPage(self) -> None:
        """Navigate to next page or scroll down if not at bottom of tall page."""
        currentIdx = self.getCurrentSlideIndex()
        if self._isPageTall(currentIdx) and self.verticalOffset < 1.0:
            self.verticalOffset = 1.0
            self.update()
            self.presenterWindow.update()
        elif self.currentPage + 1 < len(self.slideOrder):
            self.currentPage += 1
            self.verticalOffset = 0.0
            self.update()
            self.notes.show(self.getCurrentSlideIndex())
            self.presenterWindow.update()
            self.slideOrganizer.setCurrentSlide(self.currentPage)

    def _isPageTall(self, pageNum: int) -> bool:
        """Check if a page is taller than the presentation window."""
        if pageNum not in self.pdfImages:
            return False
        image = self.pdfImages[pageNum]
        return image.height() > self.presenterWindow.height()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_S and (
            event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        ):
            self.notes.save()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    viewer = QtPDFViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
