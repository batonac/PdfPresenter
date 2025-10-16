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
from qfluentwidgets import BodyLabel, PushButton, Slider

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


class FlowLayout(QtWidgets.QLayout):
    """A flow layout that wraps items left-to-right, top-to-bottom."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.itemList: list[QtWidgets.QLayoutItem] = []
        self.spacing_h: int = 20
        self.spacing_v: int = 20

    def addItem(self, item: QtWidgets.QLayoutItem) -> None:
        self.itemList.append(item)
        self.invalidate()

    def count(self) -> int:
        return len(self.itemList)

    def itemAt(self, index: int) -> QtWidgets.QLayoutItem | None:
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index: int) -> QtWidgets.QLayoutItem | None:
        if 0 <= index < len(self.itemList):
            item = self.itemList.pop(index)
            self.invalidate()
            return item
        return None

    def expandingDirections(self) -> QtCore.Qt.Orientation:
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QtCore.QRect) -> None:
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        # Add margins
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _doLayout(self, rect: QtCore.QRect, testOnly: bool) -> int:
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            widget = item.widget()
            if widget is None:
                continue

            spaceX = self.spacing_h
            spaceY = self.spacing_v
            nextX = x + item.sizeHint().width() + spaceX

            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class SlideOrganizer(QtWidgets.QScrollArea):
    """Grid view of slides with drag-and-drop reordering."""

    def __init__(self, viewer: ViewerProtocol) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.selectedPosition: int | None = None
        self.thumbnailSize: int = 200  # Default thumbnail width

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Set light background like PowerPoint
        self.setStyleSheet("QScrollArea { background-color: #F3F3F3; border: none; }")

        # Container widget with flow layout
        self.container: QtWidgets.QWidget = QtWidgets.QWidget()
        self.container.setStyleSheet("background-color: #F3F3F3;")
        self.flowLayout: FlowLayout = FlowLayout(self.container)
        self.flowLayout.spacing_h = 20
        self.flowLayout.spacing_v = 20
        self.container.setLayout(self.flowLayout)
        self.setWidget(self.container)

        self.thumbnailWidgets: list[SlideThumbnail] = []

    def createSizeControl(self) -> QtWidgets.QWidget:
        """Create the thumbnail size slider control as a separate widget."""
        controlWidget = QtWidgets.QWidget()
        controlWidget.setStyleSheet("background-color: #E8E8E8; border-top: 1px solid #CCC;")
        controlLayout = QtWidgets.QHBoxLayout(controlWidget)
        controlLayout.setContentsMargins(10, 8, 10, 8)

        # Add stretch to push controls to the right
        controlLayout.addStretch()

        label = BodyLabel("Thumbnail Size:")
        controlLayout.addWidget(label)

        self.sizeSlider = Slider(QtCore.Qt.Orientation.Horizontal, self)
        self.sizeSlider.setMinimum(100)
        self.sizeSlider.setMaximum(400)
        self.sizeSlider.setValue(200)
        self.sizeSlider.valueChanged.connect(self.onSizeChanged)
        self.sizeSlider.setMaximumWidth(200)
        controlLayout.addWidget(self.sizeSlider)

        self.sizeLabel = BodyLabel(f"{self.thumbnailSize}px")
        self.sizeLabel.setMinimumWidth(50)
        controlLayout.addWidget(self.sizeLabel)

        return controlWidget

    def onSizeChanged(self, value: int) -> None:
        """Handle thumbnail size slider change."""
        self.thumbnailSize = value
        self.sizeLabel.setText(f"{value}px")
        if self.viewer.thumbnails:
            self.updateThumbnails()

    def updateThumbnails(self) -> None:
        """Recreate all thumbnail widgets based on current slide order."""
        # Clear existing widgets
        for widget in self.thumbnailWidgets:
            widget.deleteLater()
        self.thumbnailWidgets.clear()

        # Clear layout
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # Create thumbnail widgets
        for position, pageNum in enumerate(self.viewer.slideOrder):
            thumb = SlideThumbnail(self.viewer, position, pageNum, self.thumbnailSize)
            thumb.clicked.connect(lambda pos=position: self.onSlideClicked(pos))
            thumb.moveRequested.connect(self.onMoveSlide)
            thumb.deleteRequested.connect(self.onDeleteSlide)

            self.flowLayout.addWidget(thumb)
            self.thumbnailWidgets.append(thumb)

        if self.selectedPosition is not None and self.selectedPosition < len(self.thumbnailWidgets):
            self.thumbnailWidgets[self.selectedPosition].setSelected(True)

        # Force layout update and geometry recalculation
        self.container.updateGeometry()
        QtCore.QTimer.singleShot(0, self._updateScrollArea)

    def _updateScrollArea(self) -> None:
        """Update scroll area to reflect new content size."""
        # Calculate the required height for all thumbnails
        width = self.viewport().width()
        height = self.flowLayout.heightForWidth(width)

        # Set minimum size for container to enable scrolling
        self.container.setMinimumSize(width, height)

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
        # Update container size when scroll area is resized
        if self.viewer.thumbnails and self.thumbnailWidgets:
            self._updateScrollArea()


class SlideThumbnail(QtWidgets.QWidget):
    """Individual slide thumbnail with drag-and-drop support."""

    clicked = QtCore.Signal(int)  # position
    moveRequested = QtCore.Signal(int, int)  # from, to
    deleteRequested = QtCore.Signal(int)  # position

    def __init__(
        self, viewer: ViewerProtocol, position: int, pageNum: int, size: int = 200
    ) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.position: int = position
        self.pageNum: int = pageNum
        self.size: int = size
        self.selected: bool = False
        self.dragStartPosition: QtCore.QPoint = QtCore.QPoint()

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Slide number label (above thumbnail)
        self.numberLabel = BodyLabel(f"{position + 1}")
        self.numberLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.numberLabel)

        # Thumbnail container with border
        self.thumbnailFrame = QtWidgets.QLabel()
        self.thumbnailFrame.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.thumbnailFrame.setScaledContents(False)

        # Calculate size maintaining aspect ratio
        aspect_ratio = 1.41  # Approximate A4/Letter aspect ratio
        thumb_height = int(size * aspect_ratio)

        self.thumbnailFrame.setFixedSize(size, thumb_height)
        self.updateStyle()

        layout.addWidget(self.thumbnailFrame)

        # Delete button (below thumbnail)
        self.deleteBtn = PushButton("🗑")
        self.deleteBtn.setFixedSize(size, 28)
        self.deleteBtn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.deleteBtn.clicked.connect(lambda: self.deleteRequested.emit(self.position))
        layout.addWidget(self.deleteBtn)

        self.setAcceptDrops(True)
        self.updateImage()

    def sizeHint(self) -> QtCore.QSize:
        """Provide size hint for flow layout."""
        aspect_ratio = 1.41
        thumb_height = int(self.size * aspect_ratio)
        total_height = 18 + thumb_height + 4 + 24 + 8  # number + thumb + spacing + button + margin
        return QtCore.QSize(self.size, total_height)

    def updateImage(self) -> None:
        """Update the thumbnail image."""
        if self.pageNum in self.viewer.thumbnails:
            pixmap = QtGui.QPixmap.fromImage(self.viewer.thumbnails[self.pageNum])
            # Scale to fit the current size setting
            aspect_ratio = 1.41
            display_height = int(self.size * aspect_ratio)
            scaled = pixmap.scaled(
                self.size - 4,  # Account for border
                display_height - 4,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnailFrame.setPixmap(scaled)

    def setSelected(self, selected: bool) -> None:
        """Highlight this thumbnail as selected."""
        self.selected = selected
        self.updateStyle()

    def updateStyle(self) -> None:
        """Update visual style based on selection state."""
        if self.selected:
            self.thumbnailFrame.setStyleSheet(
                """
                QLabel {
                    background-color: white;
                    border: 3px solid #FF6B35;
                    padding: 2px;
                }
            """
            )
        else:
            self.thumbnailFrame.setStyleSheet(
                """
                QLabel {
                    background-color: white;
                    border: 1px solid #D0D0D0;
                    padding: 2px;
                }
            """
            )

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

        # Create drag pixmap of the thumbnail
        pixmap = self.thumbnailFrame.grab()
        scaled_pixmap = pixmap.scaled(
            100,
            141,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        drag.setPixmap(scaled_pixmap)
        drag.setHotSpot(scaled_pixmap.rect().center())

        drag.exec(QtCore.Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Only emit click if we didn't drag
            if (event.pos() - self.dragStartPosition).manhattanLength() < 5:
                self.clicked.emit(self.position)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mimeData = event.mimeData()
        if mimeData is not None and mimeData.hasText():
            event.acceptProposedAction()
            self.thumbnailFrame.setStyleSheet(
                """
                QLabel {
                    background-color: #E8F4FF;
                    border: 3px dashed #2196F3;
                    padding: 2px;
                }
            """
            )

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
