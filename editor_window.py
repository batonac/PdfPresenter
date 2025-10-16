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

from typing import TYPE_CHECKING

import fitz  # PyMuPDF
from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import Action, FluentIcon, MessageBox

from slide_organizer import SlideOrganizer

if TYPE_CHECKING:
    from presentation_window import PresentationWindow


class EditorWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pdfImages: dict[int, QtGui.QImage] = {}
        self.thumbnails: dict[int, QtGui.QImage] = {}
        self.slideOrder: list[int] = []
        self.currentPage: int = 0  # Track current page for protocol compatibility
        self.currentFile: str | None = None
        self.doc: fitz.Document | None = None
        self.presentationWindow: PresentationWindow | None = None
        self.slideOrganizer: SlideOrganizer

        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("PDF Presenter - Editor")
        self.resize(800, 600)

        # Create toolbar with Fluent-styled actions
        toolbar = QtWidgets.QToolBar(self)
        toolbar.setIconSize(QtCore.QSize(32, 32))
        toolbar.setMovable(False)
        toolbar.setStyleSheet(
            """
            QToolBar {
                background-color: #F3F3F3;
                border-bottom: 1px solid #E0E0E0;
                padding: 4px;
                spacing: 8px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QToolButton:hover {
                background-color: #E8E8E8;
            }
            QToolButton:pressed {
                background-color: #D0D0D0;
            }
        """
        )
        self.addToolBar(toolbar)

        # Import file action
        importAction = Action(FluentIcon.FOLDER, "Import File", self)
        importAction.triggered.connect(self.showFileDialog)
        toolbar.addAction(importAction)

        # Remove page action
        removeAction = Action(FluentIcon.DELETE, "Remove Page", self)
        removeAction.triggered.connect(self.removeSelectedPage)
        toolbar.addAction(removeAction)

        toolbar.addSeparator()

        # Present action
        presentAction = Action(FluentIcon.PLAY, "Present", self)
        presentAction.triggered.connect(self.startPresentation)
        toolbar.addAction(presentAction)

        # Main widget container
        centralWidget = QtWidgets.QWidget()
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Slide organizer
        self.slideOrganizer = SlideOrganizer(self)
        mainLayout.addWidget(self.slideOrganizer, 1)

        # Add size control at bottom
        sizeControl = self.slideOrganizer.createSizeControl()
        mainLayout.addWidget(sizeControl)

        self.setCentralWidget(centralWidget)

    def showFileDialog(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.load(filename)

    def load(self, file: str) -> None:
        """Load a PDF document."""
        self.currentFile = file
        self.doc = fitz.open(file)
        if self.doc is not None:
            self.slideOrder = list(range(len(self.doc)))
        self.renderImages()

    def renderImages(self) -> None:
        """Render PDF pages to images for thumbnails."""
        self.pdfImages = {}
        self.thumbnails = {}
        if self.doc is None:
            return

        num_pages = len(self.doc)
        thumb_width = 200

        # Calculate DPI for thumbnail rendering
        # PyMuPDF uses a matrix for scaling instead of DPI
        # Standard PDF is 72 DPI, we want ~150 DPI for thumbnails
        zoom = 150.0 / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for i in range(num_pages):
            page = self.doc[i]

            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat)

            # Convert PyMuPDF pixmap to QImage
            img_data = pix.samples
            qimage = QtGui.QImage(
                img_data,
                pix.width,
                pix.height,
                pix.stride,
                QtGui.QImage.Format.Format_RGB888,
            )

            # Create thumbnail by scaling down
            thumbnail = qimage.scaled(
                thumb_width,
                int(thumb_width * pix.height / pix.width),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnails[i] = thumbnail.copy()

        self.slideOrganizer.updateThumbnails()

    def removeSelectedPage(self) -> None:
        """Remove currently selected page from slide order."""
        selected = self.slideOrganizer.getSelectedPosition()
        if selected is not None:
            self.slideOrganizer.onDeleteSlide(selected)

    def startPresentation(self) -> None:
        """Launch the presentation window."""
        if not self.currentFile or not self.doc:
            MessageBox("No PDF Loaded", "Please import a PDF file first.", self).exec()
            return

        from presentation_window import PresentationWindow

        self.presentationWindow = PresentationWindow(self)
        self.presentationWindow.show()
