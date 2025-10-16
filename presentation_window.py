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

from PyQt6 import QtCore, QtGui, QtWidgets

from notes import Notes
from timer import PauseableTimer

if TYPE_CHECKING:
    from editor_window import EditorWindow


class PresentationWindow(QtWidgets.QWidget):
    """Presenter view with notes, timer, and preview."""

    def __init__(self, editor: EditorWindow) -> None:
        super().__init__()
        self.editor: EditorWindow = editor
        self.currentPage: int = 0
        self.verticalOffset: float = 0.0
        self.pdfImages: dict[int, QtGui.QImage] = {}
        self.projectorWindow: ProjectorWindow
        self.uhr: QtWidgets.QLCDNumber
        self.notes: Notes
        self.previewLabel: QtWidgets.QLabel
        self.ptimer: PauseableTimer

        self.initUI()
        self.renderFullSizeImages()

        # Create projector window
        self.projectorWindow = ProjectorWindow(self)
        self.projectorWindow.show()

    def initUI(self) -> None:
        self.setWindowTitle("PDF Presenter - Presenter View")
        self.resize(800, 600)

        # Timer and controls
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

        # Notes
        self.notes = Notes()
        if self.editor.currentFile:
            self.notes.read(self.editor.currentFile)
            self.notes.show(self.getCurrentSlideIndex())

        # Preview of current slide
        self.previewLabel = QtWidgets.QLabel()
        self.previewLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.previewLabel.setMinimumSize(400, 300)

        previewBox = QtWidgets.QVBoxLayout()
        previewBox.addWidget(QtWidgets.QLabel("Current Slide Preview:"))
        previewBox.addWidget(self.previewLabel, 1)

        # Layout
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addLayout(previewBox, 1)
        topLayout.addLayout(clockbox, 0)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(topLayout, 1)
        mainLayout.addWidget(QtWidgets.QLabel("Speaker Notes:"))
        mainLayout.addWidget(self.notes, 1)

        self.setLayout(mainLayout)

        self.ptimer = PauseableTimer(self.updateUhr)
        self.updatePreview()

    def updateUhr(self, time: str) -> None:
        self.uhr.display(time)

    def startButton(self) -> None:
        self.ptimer.start()

    def stopButton(self) -> None:
        self.ptimer.stop()

    def renderFullSizeImages(self) -> None:
        """Render PDF pages at full resolution for projection."""
        self.pdfImages = {}
        if not self.editor.pages:
            return

        # Use primary screen size as target
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            target_width = screen.size().width()
        else:
            target_width = 1920

        render_dpi = 200.0
        num_pages = len(self.editor.pages)

        for i in range(num_pages):
            page = self.editor.pages[i]
            page_size = page.pageSize()

            render_width = int(page_size.width() / 72.0 * render_dpi)
            render_height = int(page_size.height() / 72.0 * render_dpi)

            image = page.renderer._render_image(
                page.document, page.pageNumber, render_dpi, render_dpi, render_width, render_height
            )

            # Scale to target width
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

    def getCurrentSlideIndex(self) -> int:
        """Get the actual page number for the current presentation position."""
        if 0 <= self.currentPage < len(self.editor.slideOrder):
            return self.editor.slideOrder[self.currentPage]
        return 0

    def jumpToSlide(self, position: int) -> None:
        """Jump to a specific slide position."""
        if 0 <= position < len(self.editor.slideOrder):
            self.currentPage = position
            self.verticalOffset = 0.0
            self.notes.show(self.getCurrentSlideIndex())
            self.updatePreview()
            self.projectorWindow.update()

    def updatePreview(self) -> None:
        """Update the preview of the current slide."""
        currentIdx = self.getCurrentSlideIndex()
        if currentIdx in self.editor.thumbnails:
            pixmap = QtGui.QPixmap.fromImage(self.editor.thumbnails[currentIdx])
            scaled = pixmap.scaled(
                400,
                300,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.previewLabel.setPixmap(scaled)

    def prevPage(self) -> None:
        """Navigate to previous page or scroll up if at top of tall page."""
        if self.verticalOffset > 0.0:
            self.verticalOffset = 0.0
            self.projectorWindow.update()
        elif self.currentPage > 0:
            self.currentPage -= 1
            if self._isPageTall(self.getCurrentSlideIndex()):
                self.verticalOffset = 1.0
            else:
                self.verticalOffset = 0.0
            self.notes.show(self.getCurrentSlideIndex())
            self.updatePreview()
            self.projectorWindow.update()

    def nextPage(self) -> None:
        """Navigate to next page or scroll down if not at bottom of tall page."""
        currentIdx = self.getCurrentSlideIndex()
        if self._isPageTall(currentIdx) and self.verticalOffset < 1.0:
            self.verticalOffset = 1.0
            self.projectorWindow.update()
        elif self.currentPage + 1 < len(self.editor.slideOrder):
            self.currentPage += 1
            self.verticalOffset = 0.0
            self.notes.show(self.getCurrentSlideIndex())
            self.updatePreview()
            self.projectorWindow.update()

    def _isPageTall(self, pageNum: int) -> bool:
        """Check if a page is taller than the projector window."""
        if pageNum not in self.pdfImages:
            return False
        image = self.pdfImages[pageNum]
        return image.height() > self.projectorWindow.height()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_S and (
            event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        ):
            self.notes.save()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.prevPage()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.nextPage()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Clean up when presentation window closes."""
        self.ptimer.stop()
        if self.projectorWindow:
            self.projectorWindow.close()
        event.accept()


class ProjectorWindow(QtWidgets.QMainWindow):
    """Full-screen projection window."""

    def __init__(self, presenter: PresentationWindow) -> None:
        super().__init__()
        self.presenter: PresentationWindow = presenter
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("PDF Presenter - Projection")
        self.resize(640, 480)

        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.ColorRole.Window, QtCore.Qt.GlobalColor.black)
        self.setPalette(p)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        currentIdx = self.presenter.getCurrentSlideIndex()
        if currentIdx in self.presenter.pdfImages:
            image = self.presenter.pdfImages[currentIdx]
            window_width = self.width()
            window_height = self.height()
            image_width = image.width()
            image_height = image.height()

            if image_height <= window_height:
                y_offset = (window_height - image_height) / 2
                source_rect = QtCore.QRectF(0, 0, image_width, image_height)
                dest_rect = QtCore.QRectF(0, y_offset, image_width, image_height)
            else:
                visible_height = window_height
                max_offset = image_height - window_height
                y_source = max_offset * self.presenter.verticalOffset

                source_rect = QtCore.QRectF(0, y_source, image_width, visible_height)
                dest_rect = QtCore.QRectF(0, 0, image_width, visible_height)

            painter.drawImage(dest_rect, image, source_rect)

    def toggleFullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_F11 or event.key() == QtCore.Qt.Key.Key_F:
            self.toggleFullscreen()
        elif event.key() == QtCore.Qt.Key.Key_Q or event.key() == QtCore.Qt.Key.Key_Escape:
            self.presenter.close()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.presenter.prevPage()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.presenter.nextPage()
