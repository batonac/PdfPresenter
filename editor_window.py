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

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtPdf import QPdfDocument
from qfluentwidgets import (
    FluentIcon,
    MessageBox,
    NavigationItemPosition,
    PushButton,
    SplitFluentWindow,
)

from file_browser import FileBrowserTree
from slide_organizer import SlideOrganizer

if TYPE_CHECKING:
    from presentation_window import PresentationWindow


class SlideOrganizerInterface(QtWidgets.QWidget):
    """Slide organizer interface widget."""

    filesDropped = QtCore.Signal(list)

    def __init__(self, viewer: EditorWindow, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("slide-organizer")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.slideOrganizer = SlideOrganizer(viewer)
        self.slideOrganizer.filesDropped.connect(self.filesDropped)
        layout.addWidget(self.slideOrganizer, 1)

        # Add size control
        sizeControl = self.slideOrganizer.createSizeControl()
        layout.addWidget(sizeControl)


class EditorWindow(SplitFluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.pdfImages: dict[int, QtGui.QImage] = {}
        self.thumbnails: dict[int, QtGui.QImage] = {}
        self.slideOrder: list[int] = []
        self.currentPage: int = 0
        self.currentFile: str | None = None
        self.doc: QPdfDocument | None = None
        self.presentationWindow: PresentationWindow | None = None

        # Track all loaded documents and their page mappings
        self.loadedDocs: dict[str, QPdfDocument] = {}
        self.pageToDoc: dict[int, tuple[str, int]] = {}

        # Declare interfaces
        self.fileBrowserTree: FileBrowserTree
        self.slideOrganizerInterface: SlideOrganizerInterface

        self.initInterfaces()
        self.initNavigation()
        self.initWindow()

    def initInterfaces(self) -> None:
        """Create sub-interfaces."""
        # Slide organizer interface
        self.slideOrganizerInterface = SlideOrganizerInterface(self, self)
        self.slideOrganizerInterface.filesDropped.connect(self.importFiles)

    def initNavigation(self) -> None:
        """Initialize navigation items."""
        # Add slide organizer as main interface
        self.addSubInterface(
            self.slideOrganizerInterface,
            FluentIcon.ALBUM,
            "Slides",
            position=NavigationItemPosition.TOP,
        )

        self.navigationInterface.addSeparator(NavigationItemPosition.TOP)

        # Add browse folder button in navigation
        self.navigationInterface.addItem(
            routeKey="browse-folder",
            icon=FluentIcon.FOLDER,
            text="Browse Folder",
            onClick=self.browseFolder,
            selectable=False,
            position=NavigationItemPosition.TOP,
        )

        # Create container widget for file browser tree
        fileBrowserContainer = QtWidgets.QWidget()
        fileBrowserLayout = QtWidgets.QVBoxLayout(fileBrowserContainer)
        fileBrowserLayout.setContentsMargins(4, 4, 4, 4)
        fileBrowserLayout.setSpacing(0)

        self.fileBrowserTree = FileBrowserTree()
        self.fileBrowserTree.setMaximumHeight(300)
        self.fileBrowserTree.fileDoubleClicked.connect(self.importFile)
        fileBrowserLayout.addWidget(self.fileBrowserTree)

        # Add the container to scroll area of navigation
        scrollWidget = self.navigationInterface.panel.scrollWidget
        scrollLayout = scrollWidget.layout()
        if scrollLayout is not None:
            scrollLayout.addWidget(fileBrowserContainer)

        self.navigationInterface.addSeparator(NavigationItemPosition.SCROLL)

        # Add action items
        self.navigationInterface.addItem(
            routeKey="import",
            icon=FluentIcon.ADD,
            text="Import PDF",
            onClick=self.showFileDialog,
            selectable=False,
            position=NavigationItemPosition.SCROLL,
        )

        self.navigationInterface.addItem(
            routeKey="export",
            icon=FluentIcon.SAVE,
            text="Export PDF",
            onClick=self.exportPDF,
            selectable=False,
            position=NavigationItemPosition.SCROLL,
        )

        self.navigationInterface.addItem(
            routeKey="remove",
            icon=FluentIcon.DELETE,
            text="Remove Page",
            onClick=self.removeSelectedPage,
            selectable=False,
            position=NavigationItemPosition.SCROLL,
        )

        self.navigationInterface.addSeparator(NavigationItemPosition.BOTTOM)

        # Present button at bottom
        self.navigationInterface.addItem(
            routeKey="present",
            icon=FluentIcon.PLAY,
            text="Present",
            onClick=self.startPresentation,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        # Set default interface
        self.switchTo(self.slideOrganizerInterface)

    def initWindow(self) -> None:
        """Initialize window properties."""
        self.resize(1200, 700)
        self.setWindowTitle("PDF Presenter")

        # Set navigation panel width
        self.navigationInterface.setExpandWidth(320)
        self.navigationInterface.setMinimumExpandWidth(1008)

    def browseFolder(self) -> None:
        """Open folder browser dialog."""
        try:
            print("Opening folder browser dialog...")
            current_path = (
                str(self.fileBrowserTree.currentPath) if self.fileBrowserTree.currentPath else ""
            )
            print(f"Current path: {current_path}")

            folder = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Folder",
                current_path,
            )

            print(f"Selected folder: {folder}")

            if folder:
                print(f"Calling loadFolder with: {folder}")
                self.fileBrowserTree.loadFolder(Path(folder))
                print("loadFolder completed")
        except Exception as e:
            print(f"Error in browseFolder: {e}")
            import traceback

            traceback.print_exc()
            MessageBox("Error", f"Failed to load folder:\n{str(e)}", self).exec()

    def showFileDialog(self) -> None:
        """Import single PDF file."""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", "", "PDF Files (*.pdf)"
        )
        if filename:
            self.importFile(filename)

    def importFile(self, filepath: str) -> None:
        """Import a single PDF file and add all its pages."""
        self.importFiles([filepath])
        # Switch to slide organizer after import
        self.switchTo(self.slideOrganizerInterface)

    def importFiles(self, filepaths: list[str]) -> None:
        """Import multiple PDF files and add all their pages."""
        for filepath in filepaths:
            if filepath in self.loadedDocs:
                doc = self.loadedDocs[filepath]
            else:
                doc = QPdfDocument()
                doc.load(filepath)

                if doc.status() != QPdfDocument.Status.Ready:
                    MessageBox("Error", f"Failed to load: {filepath}", self).exec()
                    continue

                self.loadedDocs[filepath] = doc

                if not self.currentFile:
                    self.currentFile = filepath
                    self.doc = doc

            # Add pages from this document
            num_pages = doc.pageCount()
            start_global_page = len(self.thumbnails)

            for page_idx in range(num_pages):
                global_page = start_global_page + page_idx
                self.pageToDoc[global_page] = (filepath, page_idx)
                self.slideOrder.append(global_page)

                # Render thumbnail
                page_size = doc.pagePointSize(page_idx)
                thumb_width = 200
                scale = thumb_width / page_size.width()
                thumb_height = int(page_size.height() * scale)

                image = doc.render(page_idx, QtCore.QSize(thumb_width, thumb_height))
                self.thumbnails[global_page] = image.copy()

        self.slideOrganizerInterface.slideOrganizer.updateThumbnails()

    def exportPDF(self) -> None:
        """Export current slide order as a new PDF."""
        if not self.slideOrder:
            MessageBox("No Slides", "No slides to export.", self).exec()
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf)"
        )

        if not filename:
            return

        try:
            import fitz

            output_pdf = fitz.open()

            for global_page in self.slideOrder:
                if global_page not in self.pageToDoc:
                    continue

                filepath, page_idx = self.pageToDoc[global_page]
                src_pdf = fitz.open(filepath)
                output_pdf.insert_pdf(src_pdf, from_page=page_idx, to_page=page_idx)
                src_pdf.close()

            output_pdf.save(filename)
            output_pdf.close()

            MessageBox("Success", f"PDF exported to:\n{filename}", self).exec()

        except ImportError:
            MessageBox(
                "PyMuPDF Required",
                "PDF export requires PyMuPDF (fitz).\nInstall with: uv add pymupdf",
                self,
            ).exec()
        except Exception as e:
            MessageBox("Error", f"Failed to export PDF:\n{str(e)}", self).exec()

    def removeSelectedPage(self) -> None:
        """Remove currently selected page from slide order."""
        selected = self.slideOrganizerInterface.slideOrganizer.getSelectedPosition()
        if selected is not None:
            self.slideOrganizerInterface.slideOrganizer.onDeleteSlide(selected)

    def startPresentation(self) -> None:
        """Launch the presentation window."""
        if not self.currentFile or not self.doc:
            MessageBox("No PDF Loaded", "Please import a PDF file first.", self).exec()
            return

        from presentation_window import PresentationWindow

        self.presentationWindow = PresentationWindow(self)
        self.presentationWindow.show()

    def load(self, file: str) -> None:
        """Load a PDF document (legacy single-file method)."""
        self.importFile(file)

    def renderImages(self) -> None:
        """Render images - now handled by importFiles."""
        pass
