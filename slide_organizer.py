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

from PyQt6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
    from editor_window import EditorWindow
    from presentation_window import PresentationWindow


class ViewerProtocol(Protocol):
    """Protocol for objects that can be viewed by SlideOrganizer."""

    slideOrder: list[int]
    thumbnails: dict[int, QtGui.QImage]
    presentationWindow: PresentationWindow | None
    currentPage: int

    def update(self) -> None: ...


class SlideOrganizer(QtWidgets.QScrollArea):
    """Grid view of slides with drag-and-drop reordering."""

    def __init__(self, viewer: ViewerProtocol) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.selectedPosition: int | None = None
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget with flow layout
        self.container: QtWidgets.QWidget = QtWidgets.QWidget()
        self.gridLayout: QtWidgets.QGridLayout = QtWidgets.QGridLayout(self.container)
        self.gridLayout.setSpacing(10)
        self.setWidget(self.container)

        self.thumbnailWidgets: list[SlideThumbnail] = []

    def updateThumbnails(self) -> None:
        """Recreate all thumbnail widgets based on current slide order."""
        # Clear existing widgets
        for widget in self.thumbnailWidgets:
            widget.deleteLater()
        self.thumbnailWidgets.clear()

        # Clear layout
        while self.gridLayout.count():
            self.gridLayout.takeAt(0)

        # Create thumbnail widgets
        columns = max(1, self.width() // 220)  # 200px thumb + 20px spacing

        for position, pageNum in enumerate(self.viewer.slideOrder):
            thumb = SlideThumbnail(self.viewer, position, pageNum)
            thumb.clicked.connect(lambda pos=position: self.onSlideClicked(pos))
            thumb.moveRequested.connect(self.onMoveSlide)
            thumb.deleteRequested.connect(self.onDeleteSlide)

            row = position // columns
            col = position % columns
            self.gridLayout.addWidget(thumb, row, col)
            self.thumbnailWidgets.append(thumb)

        if self.selectedPosition is not None and self.selectedPosition < len(self.thumbnailWidgets):
            self.thumbnailWidgets[self.selectedPosition].setSelected(True)

    def setCurrentSlide(self, position: int) -> None:
        """Highlight the current slide."""
        self.selectedPosition = position
        for i, widget in enumerate(self.thumbnailWidgets):
            widget.setSelected(i == position)

    def getSelectedPosition(self) -> int | None:
        """Get the currently selected slide position."""
        return self.selectedPosition

    def onSlideClicked(self, position: int) -> None:
        """Jump to clicked slide."""
        self.selectedPosition = position
        self.setCurrentSlide(position)

        # If we're in a presentation, jump to this slide
        if hasattr(self.viewer, "presentationWindow") and self.viewer.presentationWindow:
            self.viewer.presentationWindow.jumpToSlide(position)

    def onMoveSlide(self, fromPos: int, toPos: int) -> None:
        """Move slide from one position to another."""
        if 0 <= fromPos < len(self.viewer.slideOrder) and 0 <= toPos < len(self.viewer.slideOrder):
            pageNum = self.viewer.slideOrder.pop(fromPos)
            self.viewer.slideOrder.insert(toPos, pageNum)

            # Adjust current page if needed
            if self.viewer.currentPage == fromPos:
                self.viewer.currentPage = toPos
            elif fromPos < self.viewer.currentPage <= toPos:
                self.viewer.currentPage -= 1
            elif toPos <= self.viewer.currentPage < fromPos:
                self.viewer.currentPage += 1

            self.updateThumbnails()

    def onDeleteSlide(self, position: int) -> None:
        """Remove slide from presentation order."""
        if len(self.viewer.slideOrder) > 1 and 0 <= position < len(self.viewer.slideOrder):
            self.viewer.slideOrder.pop(position)

            # Adjust current page
            if self.viewer.currentPage >= len(self.viewer.slideOrder):
                self.viewer.currentPage = len(self.viewer.slideOrder) - 1
            elif self.viewer.currentPage > position:
                self.viewer.currentPage -= 1

            self.updateThumbnails()
            # Only update if there's a presentation window
            if hasattr(self.viewer, "presentationWindow") and self.viewer.presentationWindow:
                self.viewer.presentationWindow.projectorWindow.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        # Reflow thumbnails on resize
        if self.viewer.thumbnails:
            self.updateThumbnails()


class SlideThumbnail(QtWidgets.QFrame):
    """Individual slide thumbnail with drag-and-drop support."""

    clicked = QtCore.pyqtSignal(int)  # position
    moveRequested = QtCore.pyqtSignal(int, int)  # from, to
    deleteRequested = QtCore.pyqtSignal(int)  # position

    def __init__(self, viewer: ViewerProtocol, position: int, pageNum: int) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.position: int = position
        self.pageNum: int = pageNum
        self.selected: bool = False
        self.dragStartPosition: QtCore.QPoint = QtCore.QPoint()

        self.setFrameStyle(QtWidgets.QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setMinimumSize(200, 150)
        self.setMaximumSize(200, 300)
        self.setAcceptDrops(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Thumbnail image
        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setScaledContents(False)
        layout.addWidget(self.imageLabel)

        # Slide number and controls
        controlLayout = QtWidgets.QHBoxLayout()
        self.numberLabel = QtWidgets.QLabel(f"#{position + 1} (Page {pageNum + 1})")
        self.numberLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.deleteBtn = QtWidgets.QPushButton("✕")
        self.deleteBtn.setMaximumWidth(30)
        self.deleteBtn.clicked.connect(lambda: self.deleteRequested.emit(self.position))

        controlLayout.addWidget(self.numberLabel, 1)
        controlLayout.addWidget(self.deleteBtn)
        layout.addLayout(controlLayout)

        self.updateImage()
        self.updateStyle()

    def updateImage(self) -> None:
        """Update the thumbnail image."""
        if self.pageNum in self.viewer.thumbnails:
            pixmap = QtGui.QPixmap.fromImage(self.viewer.thumbnails[self.pageNum])
            scaled = pixmap.scaled(
                180,
                200,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.imageLabel.setPixmap(scaled)

    def setSelected(self, selected: bool) -> None:
        """Highlight this thumbnail as selected."""
        self.selected = selected
        self.updateStyle()

    def updateStyle(self) -> None:
        """Update visual style based on selection state."""
        if self.selected:
            self.setStyleSheet("QFrame { border: 3px solid #4CAF50; background-color: #E8F5E9; }")
        else:
            self.setStyleSheet("QFrame { border: 1px solid #CCC; background-color: white; }")

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not (event.buttons() & QtCore.Qt.MouseButton.LeftButton):
            return
        if (
            event.pos() - self.dragStartPosition
        ).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        drag = QtGui.QDrag(self)
        mimeData = QtCore.QMimeData()
        mimeData.setText(str(self.position))
        drag.setMimeData(mimeData)
        drag.setPixmap(self.grab().scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        drag.exec(QtCore.Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self.position)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mimeData = event.mimeData()
        if mimeData is not None and mimeData.hasText():
            event.acceptProposedAction()
            self.setStyleSheet("QFrame { border: 3px dashed #2196F3; }")

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.updateStyle()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        mimeData = event.mimeData()
        if mimeData is not None:
            fromPos = int(mimeData.text())
            toPos = self.position
            self.moveRequested.emit(fromPos, toPos)
            event.acceptProposedAction()
        self.updateStyle()
