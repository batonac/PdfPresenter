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

from typing import TYPE_CHECKING, Protocol

from PySide6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    pass


class ViewerProtocol(Protocol):
    """Protocol for objects that can be viewed by PDFView."""

    currentPage: int
    pdfImages: dict[int, QtGui.QImage]


class PDFView(QtWidgets.QWidget):
    def __init__(self, offset: int, viewer: ViewerProtocol) -> None:
        super().__init__()
        self.offset: int = offset
        self.viewer: ViewerProtocol = viewer

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
