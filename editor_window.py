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

import qpageview.pdf
from PyQt6 import QtCore, QtGui, QtWidgets

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
        self.doc: qpageview.pdf.PdfDocument | None = None
        self.pages: list[qpageview.pdf.PdfPage] = []
        self.presentationWindow: PresentationWindow | None = None
        self.slideOrganizer: SlideOrganizer

        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("PDF Presenter - Editor")
        self.resize(800, 600)

        # Create toolbar
        toolbar: QtWidgets.QToolBar = self.addToolBar("Main") or QtWidgets.QToolBar("Main")
        toolbar.setIconSize(QtCore.QSize(32, 32))

        # Import file action
        importAction = QtGui.QAction("Import File", self)
        importAction.triggered.connect(self.showFileDialog)
        toolbar.addAction(importAction)

        # Remove page action
        removeAction = QtGui.QAction("Remove Page", self)
        removeAction.triggered.connect(self.removeSelectedPage)
        toolbar.addAction(removeAction)

        toolbar.addSeparator()

        # Present action
        presentAction = QtGui.QAction("Present", self)
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
        self.doc = qpageview.pdf.PdfDocument(file)
        self.pages = list(self.doc.pages())
        self.slideOrder = list(range(len(self.pages)))
        self.renderImages()

    def renderImages(self) -> None:
        """Render PDF pages to images for thumbnails."""
        self.pdfImages = {}
        self.thumbnails = {}
        if self.doc is None or not self.pages:
            return

        num_pages = len(self.pages)
        render_dpi = 150.0
        thumb_width = 200

        for i in range(num_pages):
            page = self.pages[i]
            page_size = page.pageSize()

            render_width = int(page_size.width() / 72.0 * render_dpi)
            render_height = int(page_size.height() / 72.0 * render_dpi)

            image = page.renderer._render_image(
                page.document, page.pageNumber, render_dpi, render_dpi, render_width, render_height
            )

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

        self.slideOrganizer.updateThumbnails()

    def removeSelectedPage(self) -> None:
        """Remove currently selected page from slide order."""
        selected = self.slideOrganizer.getSelectedPosition()
        if selected is not None:
            self.slideOrganizer.onDeleteSlide(selected)

    def startPresentation(self) -> None:
        """Launch the presentation window."""
        if not self.currentFile or not self.pages:
            QtWidgets.QMessageBox.warning(self, "No PDF Loaded", "Please import a PDF file first.")
            return

        from presentation_window import PresentationWindow

        self.presentationWindow = PresentationWindow(self)
        self.presentationWindow.show()
