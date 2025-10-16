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

import os
from pathlib import Path
from typing import Any

from PySide6 import QtCore, QtGui, QtQml, QtQuick
from PySide6.QtCore import Property, Signal, Slot
from PySide6.QtPdf import QPdfDocument

from timer import PauseableTimer


QML_IMPORT_NAME = "PdfPresenter"
QML_IMPORT_MAJOR_VERSION = 1


class SlideImageProvider(QtQuick.QQuickImageProvider):
    """Image provider for slide thumbnails."""

    def __init__(self, backend):
        super().__init__(QtQuick.QQuickImageProvider.ImageType.Image)
        self.backend = backend

    def requestImage(self, id, size, requestedSize):
        """Provide image for the given ID."""
        try:
            position = int(id)
            if 0 <= position < len(self.backend._slideOrder):
                page_num = self.backend._slideOrder[position]
                if page_num in self.backend._thumbnails:
                    return self.backend._thumbnails[page_num], self.backend._thumbnails[page_num].size()
        except (ValueError, IndexError):
            pass
        
        # Return empty image if not found
        return QtGui.QImage(), QtCore.QSize()


class ProjectionImageProvider(QtQuick.QQuickImageProvider):
    """Image provider for projection images."""

    def __init__(self, backend):
        super().__init__(QtQuick.QQuickImageProvider.ImageType.Image)
        self.backend = backend

    def requestImage(self, id, size, requestedSize):
        """Provide full-size image for the given ID."""
        try:
            position = int(id)
            if 0 <= position < len(self.backend._slideOrder):
                page_num = self.backend._slideOrder[position]
                if page_num in self.backend._fullImages:
                    return self.backend._fullImages[page_num], self.backend._fullImages[page_num].size()
        except (ValueError, IndexError):
            pass
        
        # Return empty image if not found
        return QtGui.QImage(), QtCore.QSize()


@QtQml.QmlElement
class SlideModel(QtCore.QAbstractListModel):
    """Model for the slide list."""

    ImageRole = QtCore.Qt.ItemDataRole.UserRole + 1
    PageNumberRole = QtCore.Qt.ItemDataRole.UserRole + 2
    PositionRole = QtCore.Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slides: list[tuple[int, QtGui.QImage]] = []

    def roleNames(self) -> dict[int, bytes]:
        return {
            self.ImageRole: b"slideImage",
            self.PageNumberRole: b"pageNumber",
            self.PositionRole: b"position",
        }

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._slides)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._slides):
            return None

        page_num, image = self._slides[index.row()]

        if role == self.ImageRole:
            return image
        elif role == self.PageNumberRole:
            return page_num
        elif role == self.PositionRole:
            return index.row()

        return None

    def setSlides(self, slides: list[tuple[int, QtGui.QImage]]) -> None:
        """Update the slide list."""
        self.beginResetModel()
        self._slides = slides
        self.endResetModel()

    def moveSlide(self, fromPos: int, toPos: int) -> None:
        """Move a slide from one position to another."""
        if 0 <= fromPos < len(self._slides) and 0 <= toPos < len(self._slides):
            slide = self._slides.pop(fromPos)
            self._slides.insert(toPos, slide)
            self.beginResetModel()
            self.endResetModel()

    def removeSlide(self, position: int) -> None:
        """Remove a slide at the given position."""
        if 0 <= position < len(self._slides) and len(self._slides) > 1:
            self.beginRemoveRows(QtCore.QModelIndex(), position, position)
            self._slides.pop(position)
            self.endRemoveRows()


@QtQml.QmlElement
class PdfBackend(QtCore.QObject):
    """Backend for PDF presentation logic."""

    slideOrderChanged = Signal()
    currentPageChanged = Signal()
    currentFileChanged = Signal()
    presentationModeChanged = Signal()
    timerTextChanged = Signal()
    currentNotesChanged = Signal()
    errorOccurred = Signal(str, str, arguments=["title", "message"])

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thumbnails: dict[int, QtGui.QImage] = {}
        self._fullImages: dict[int, QtGui.QImage] = {}
        self._slideOrder: list[int] = []
        self._currentPage: int = 0
        self._currentFile: str | None = None
        self._doc: QPdfDocument | None = None
        self._presentationMode: bool = False
        self._verticalOffset: float = 0.0

        # Track all loaded documents
        self._loadedDocs: dict[str, QPdfDocument] = {}
        self._pageToDoc: dict[int, tuple[str, int]] = {}

        # Notes management
        self._notes: dict[str, str] = {}
        self._notesFile: str | None = None
        self._currentNotes: str = ""

        # Timer
        self._timer = PauseableTimer(self._updateTimerDisplay)
        self._timerText = "00:00"

        # Slide model
        self._slideModel = SlideModel(self)

    # Properties
    @Property(int, notify=currentPageChanged)
    def currentPage(self) -> int:
        return self._currentPage

    @currentPage.setter
    def currentPage(self, value: int) -> None:
        if self._currentPage != value:
            self._currentPage = value
            self.currentPageChanged.emit()
            self._loadNotesForCurrentSlide()

    @Property(str, notify=currentFileChanged)
    def currentFile(self) -> str:
        return self._currentFile or ""

    @Property(bool, notify=presentationModeChanged)
    def presentationMode(self) -> bool:
        return self._presentationMode

    @presentationMode.setter
    def presentationMode(self, value: bool) -> None:
        if self._presentationMode != value:
            self._presentationMode = value
            self.presentationModeChanged.emit()
            if value:
                self._renderFullSizeImages()
                self._loadNotesForCurrentSlide()

    @Property(str, notify=timerTextChanged)
    def timerText(self) -> str:
        return self._timerText

    @Property(str, notify=currentNotesChanged)
    def currentNotes(self) -> str:
        return self._currentNotes

    @currentNotes.setter
    def currentNotes(self, value: str) -> None:
        if self._currentNotes != value:
            self._currentNotes = value
            self.currentNotesChanged.emit()
            self._saveNote()

    @Property(QtCore.QAbstractListModel, constant=True)
    def slideModel(self) -> QtCore.QAbstractListModel:
        return self._slideModel

    @Property(int, notify=slideOrderChanged)
    def slideCount(self) -> int:
        return len(self._slideOrder)

    # Slots
    @Slot(str)
    def importFile(self, filepath: str) -> None:
        """Import a PDF file."""
        self.importFiles([filepath])

    @Slot(list)
    def importFiles(self, filepaths: list[str]) -> None:
        """Import multiple PDF files."""
        for filepath in filepaths:
            # Convert file:// URLs to local paths
            if filepath.startswith("file://"):
                filepath = filepath[7:]  # Remove file:// prefix
                if os.name == "nt" and filepath.startswith("/"):
                    filepath = filepath[1:]  # Remove leading / on Windows

            if filepath in self._loadedDocs:
                doc = self._loadedDocs[filepath]
            else:
                doc = QPdfDocument()
                doc.load(filepath)

                if doc.status() != QPdfDocument.Status.Ready:
                    self.errorOccurred.emit("Error", f"Failed to load: {filepath}")
                    continue

                self._loadedDocs[filepath] = doc

                if not self._currentFile:
                    self._currentFile = filepath
                    self._doc = doc
                    self.currentFileChanged.emit()

            # Add pages from this document
            num_pages = doc.pageCount()
            start_global_page = len(self._thumbnails)

            for page_idx in range(num_pages):
                global_page = start_global_page + page_idx
                self._pageToDoc[global_page] = (filepath, page_idx)
                self._slideOrder.append(global_page)

                # Render thumbnail
                page_size = doc.pagePointSize(page_idx)
                thumb_width = 200
                scale = thumb_width / page_size.width()
                thumb_height = int(page_size.height() * scale)

                image = doc.render(page_idx, QtCore.QSize(thumb_width, thumb_height))
                self._thumbnails[global_page] = image.copy()

        self._updateSlideModel()
        self.slideOrderChanged.emit()

    @Slot(str)
    def browseFolder(self, folderPath: str) -> None:
        """Browse and load files from a folder."""
        # This will be handled by the FileBrowser QML component
        pass

    @Slot(str)
    def exportPDF(self, filename: str) -> None:
        """Export current slide order as a new PDF."""
        if not self._slideOrder:
            self.errorOccurred.emit("No Slides", "No slides to export.")
            return

        # Convert file:// URLs to local paths
        if filename.startswith("file://"):
            filename = filename[7:]
            if os.name == "nt" and filename.startswith("/"):
                filename = filename[1:]

        try:
            import fitz

            output_pdf = fitz.open()

            for global_page in self._slideOrder:
                if global_page not in self._pageToDoc:
                    continue

                filepath, page_idx = self._pageToDoc[global_page]
                src_pdf = fitz.open(filepath)
                output_pdf.insert_pdf(src_pdf, from_page=page_idx, to_page=page_idx)
                src_pdf.close()

            output_pdf.save(filename)
            output_pdf.close()

        except ImportError:
            self.errorOccurred.emit(
                "PyMuPDF Required",
                "PDF export requires PyMuPDF (fitz).\nInstall with: uv add pymupdf",
            )
        except Exception as e:
            self.errorOccurred.emit("Error", f"Failed to export PDF:\n{str(e)}")

    @Slot(int)
    def removeSlide(self, position: int) -> None:
        """Remove slide at the given position."""
        if len(self._slideOrder) > 1 and 0 <= position < len(self._slideOrder):
            self._slideOrder.pop(position)

            if self._currentPage >= len(self._slideOrder):
                self.currentPage = len(self._slideOrder) - 1
            elif self._currentPage > position:
                self.currentPage = self._currentPage - 1

            self._slideModel.removeSlide(position)
            self.slideOrderChanged.emit()

    @Slot(int, int)
    def moveSlide(self, fromPos: int, toPos: int) -> None:
        """Move slide from one position to another."""
        if 0 <= fromPos < len(self._slideOrder) and 0 <= toPos < len(self._slideOrder):
            page_num = self._slideOrder.pop(fromPos)
            self._slideOrder.insert(toPos, page_num)

            if self._currentPage == fromPos:
                self.currentPage = toPos
            elif fromPos < self._currentPage <= toPos:
                self.currentPage = self._currentPage - 1
            elif toPos <= self._currentPage < fromPos:
                self.currentPage = self._currentPage + 1

            self._slideModel.moveSlide(fromPos, toPos)
            self.slideOrderChanged.emit()

    @Slot(int)
    def jumpToSlide(self, position: int) -> None:
        """Jump to a specific slide."""
        if 0 <= position < len(self._slideOrder):
            self.currentPage = position
            self._verticalOffset = 0.0

    @Slot()
    def nextSlide(self) -> None:
        """Go to next slide."""
        if self._currentPage + 1 < len(self._slideOrder):
            self.currentPage = self._currentPage + 1
            self._verticalOffset = 0.0

    @Slot()
    def prevSlide(self) -> None:
        """Go to previous slide."""
        if self._currentPage > 0:
            self.currentPage = self._currentPage - 1
            self._verticalOffset = 0.0

    @Slot()
    def startTimer(self) -> None:
        """Start the presentation timer."""
        self._timer.start()

    @Slot()
    def stopTimer(self) -> None:
        """Stop the presentation timer."""
        self._timer.stop()

    @Slot()
    def saveNotes(self) -> None:
        """Save notes to file."""
        if len(self._notes) > 0 and self._notesFile:
            import codecs

            with codecs.open(self._notesFile, encoding="utf-8", mode="w") as f:
                for slide_id in self._notes.keys():
                    f.write(slide_id)
                    f.write("\n")
                    f.write(self._notes[slide_id])
                    f.write("\n")

    @Slot(result=QtGui.QImage)
    def getCurrentSlideImage(self) -> QtGui.QImage:
        """Get the current slide image for projection."""
        if 0 <= self._currentPage < len(self._slideOrder):
            page_num = self._slideOrder[self._currentPage]
            if page_num in self._fullImages:
                return self._fullImages[page_num]
        return QtGui.QImage()

    @Slot(result=QtGui.QImage)
    def getCurrentThumbnail(self) -> QtGui.QImage:
        """Get the current slide thumbnail."""
        if 0 <= self._currentPage < len(self._slideOrder):
            page_num = self._slideOrder[self._currentPage]
            if page_num in self._thumbnails:
                return self._thumbnails[page_num]
        return QtGui.QImage()

    # Private methods
    def _updateSlideModel(self) -> None:
        """Update the slide model with current slides."""
        slides = [(page_num, self._thumbnails[page_num]) for page_num in self._slideOrder]
        self._slideModel.setSlides(slides)

    def _renderFullSizeImages(self) -> None:
        """Render PDF pages at full resolution for projection."""
        self._fullImages = {}
        if not self._doc:
            return

        # Use a reasonable target size for full-screen display
        target_width = 1920
        target_height = 1080

        num_pages = self._doc.pageCount()

        for i in range(num_pages):
            page_size = self._doc.pagePointSize(i)

            # Calculate scale to fit screen
            scale_x = target_width / page_size.width()
            scale_y = target_height / page_size.height()
            scale = min(scale_x, scale_y)

            # Calculate render size
            render_width = int(page_size.width() * scale)
            render_height = int(page_size.height() * scale)

            # Render page at target size
            image = self._doc.render(i, QtCore.QSize(render_width, render_height))

            self._fullImages[i] = image.copy()

    def _loadNotesForCurrentSlide(self) -> None:
        """Load notes for the current slide."""
        if 0 <= self._currentPage < len(self._slideOrder):
            page_num = self._slideOrder[self._currentPage]
            slide_id = f"==XXslide{page_num}"

            if slide_id in self._notes:
                self._currentNotes = self._notes[slide_id]
            else:
                self._currentNotes = ""

            self.currentNotesChanged.emit()

    def _saveNote(self) -> None:
        """Save the current note."""
        if 0 <= self._currentPage < len(self._slideOrder):
            page_num = self._slideOrder[self._currentPage]
            slide_id = f"==XXslide{page_num}"
            self._notes[slide_id] = self._currentNotes

    def _updateTimerDisplay(self, time: str) -> None:
        """Update the timer display."""
        self._timerText = time
        self.timerTextChanged.emit()

    def _readNotes(self, filename: str) -> None:
        """Read notes from file."""
        self._notesFile = str(filename) + ".notes"
        if os.path.isfile(self._notesFile):
            import codecs

            with codecs.open(self._notesFile, encoding="utf-8", mode="r") as f:
                slide = None
                for line in f:
                    if "==XXslide" in line:
                        slide = line.strip()
                        self._notes[slide] = ""
                    elif slide is not None:
                        self._notes[slide] += line
