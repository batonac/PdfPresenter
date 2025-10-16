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

# DEPRECATED: This file is no longer used in the application.
# See presentation_window.py for the current implementation of ProjectorWindow.

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from PySide6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    pass


class ViewerProtocol(Protocol):
    """Protocol for legacy viewer interface."""

    pdfImages: dict[int, QtGui.QImage]
    verticalOffset: float

    def getCurrentSlideIndex(self) -> int: ...
    def renderImages(self) -> None: ...
    def showFileDialog(self) -> None: ...
    def prevPage(self) -> None: ...
    def nextPage(self) -> None: ...
    def close(self) -> None: ...


class ProjectorView(QtWidgets.QMainWindow):
    """DEPRECATED: Legacy projector view - use ProjectorWindow from presentation_window.py instead."""

    def __init__(self, viewer: ViewerProtocol):
        super().__init__()
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
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        currentIdx = self.viewer.getCurrentSlideIndex()
        if currentIdx in self.viewer.pdfImages:
            image = self.viewer.pdfImages[currentIdx]
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
                y_source = max_offset * self.viewer.verticalOffset

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
        elif event.key() == QtCore.Qt.Key.Key_Q:
            self.close()
            self.viewer.close()
        elif event.key() == QtCore.Qt.Key.Key_O:
            self.viewer.showFileDialog()
        elif event.key() == QtCore.Qt.Key.Key_Left:
            self.viewer.prevPage()
            self.update()
        elif event.key() == QtCore.Qt.Key.Key_Right:
            self.viewer.nextPage()
            self.update()
