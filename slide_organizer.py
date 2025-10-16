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
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    PushButton,
    ScrollArea,
    SimpleCardWidget,
    Slider,
    SubtitleLabel,
)
from qfluentwidgets.components.layout import FlowLayout

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


class SlideOrganizer(ScrollArea):
    """Grid view of slides with drag-and-drop reordering."""

    filesDropped = QtCore.Signal(list)  # list of file paths

    def __init__(self, viewer: ViewerProtocol) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.selectedPosition: int | None = None
        self.thumbnailSize: int = 200  # Default thumbnail width

        self.setAcceptDrops(True)
        self.enableTransparentBackground()

        # Container widget with flow layout
        self.container: QtWidgets.QWidget = QtWidgets.QWidget()
        self.flowLayout: FlowLayout = FlowLayout(self.container, needAni=True)
        self.flowLayout.setAnimation(200)
        self.flowLayout.setContentsMargins(20, 20, 20, 20)
        self.flowLayout.setVerticalSpacing(20)
        self.flowLayout.setHorizontalSpacing(20)

        self.container.setLayout(self.flowLayout)
        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.thumbnailWidgets: list[SlideThumbnail] = []

        # Create overlay widget for empty state
        self.emptyOverlay = QtWidgets.QWidget(self)
        self.emptyOverlay.setStyleSheet("background: transparent;")
        overlayLayout = QtWidgets.QVBoxLayout(self.emptyOverlay)
        overlayLayout.setContentsMargins(0, 0, 0, 0)
        overlayLayout.addStretch()

        # Center container
        centerContainer = QtWidgets.QHBoxLayout()
        centerContainer.addStretch()

        # Empty state card
        self.emptyCard = CardWidget()
        self.emptyCard.setFixedSize(400, 200)
        emptyLayout = QtWidgets.QVBoxLayout(self.emptyCard)
        emptyLayout.setContentsMargins(40, 40, 40, 40)
        emptyLayout.setSpacing(16)

        emptyTitle = SubtitleLabel("No slides loaded")
        emptyTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        emptyLayout.addWidget(emptyTitle)

        emptyText = BodyLabel("Drop PDF files here or use 'Import PDF' to get started")
        emptyText.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        emptyLayout.addWidget(emptyText)

        centerContainer.addWidget(self.emptyCard)
        centerContainer.addStretch()

        overlayLayout.addLayout(centerContainer)
        overlayLayout.addStretch()

        self.emptyOverlay.show()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Update overlay size when scroll area is resized."""
        super().resizeEvent(event)
        if hasattr(self, "emptyOverlay"):
            self.emptyOverlay.setGeometry(self.rect())

    def _onFilesDropped(self, files: list[str]) -> None:
        """Handle files dropped on the drop widget."""
        self.filesDropped.emit(files)

    def createSizeControl(self) -> QtWidgets.QWidget:
        """Create the thumbnail size slider control as a separate widget."""
        controlWidget = QtWidgets.QWidget()
        controlLayout = QtWidgets.QHBoxLayout(controlWidget)
        controlLayout.setContentsMargins(10, 8, 10, 8)

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
        self.flowLayout.removeAllWidgets()

        # Show/hide empty overlay
        if not self.viewer.slideOrder:
            self.emptyOverlay.show()
            self.emptyOverlay.raise_()
            return
        else:
            self.emptyOverlay.hide()

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

        if hasattr(self.viewer, "presentationWindow") and self.viewer.presentationWindow:
            self.viewer.presentationWindow.jumpToSlide(position)

    def onMoveSlide(self, fromPos: int, toPos: int) -> None:
        """Move slide from one position to another."""
        if 0 <= fromPos < len(self.viewer.slideOrder) and 0 <= toPos < len(self.viewer.slideOrder):
            pageNum = self.viewer.slideOrder.pop(fromPos)
            self.viewer.slideOrder.insert(toPos, pageNum)

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

            if self.viewer.currentPage >= len(self.viewer.slideOrder):
                self.viewer.currentPage = len(self.viewer.slideOrder) - 1
            elif self.viewer.currentPage > position:
                self.viewer.currentPage -= 1

            self.updateThumbnails()
            if hasattr(self.viewer, "presentationWindow") and self.viewer.presentationWindow:
                self.viewer.presentationWindow.projectorWindow.update()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """Accept file drops."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(".pdf") for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """Handle dropped PDF files."""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                if filepath.lower().endswith(".pdf"):
                    files.append(filepath)

            if files:
                self.filesDropped.emit(files)
                event.acceptProposedAction()


class SlideThumbnail(SimpleCardWidget):
    """Individual slide thumbnail with drag-and-drop support."""

    clicked = QtCore.Signal(int)
    moveRequested = QtCore.Signal(int, int)
    deleteRequested = QtCore.Signal(int)

    def __init__(
        self, viewer: ViewerProtocol, position: int, pageNum: int, thumbSize: int = 200
    ) -> None:
        super().__init__()
        self.viewer: ViewerProtocol = viewer
        self.position: int = position
        self.pageNum: int = pageNum
        self.thumbSize: int = thumbSize
        self.selected: bool = False
        self.dragStartPosition: QtCore.QPoint = QtCore.QPoint()

        # Set card properties
        self.setBorderRadius(8)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Slide number label
        self.numberLabel = BodyLabel(f"{position + 1}")
        self.numberLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.numberLabel)

        # Thumbnail container - still QLabel for image display
        self.thumbnailFrame = QtWidgets.QLabel()
        self.thumbnailFrame.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.thumbnailFrame.setScaledContents(False)
        self.thumbnailFrame.setStyleSheet("QLabel { background: transparent; }")

        aspect_ratio = 1.41
        thumb_height = int(thumbSize * aspect_ratio)
        self.thumbnailFrame.setFixedSize(thumbSize, thumb_height)

        layout.addWidget(self.thumbnailFrame)

        # Delete button - already using Fluent PushButton
        self.deleteBtn = PushButton("Delete")
        self.deleteBtn.setFixedHeight(32)
        self.deleteBtn.clicked.connect(lambda: self.deleteRequested.emit(self.position))
        layout.addWidget(self.deleteBtn)

        self.setAcceptDrops(True)
        self.updateImage()

    def sizeHint(self) -> QtCore.QSize:
        """Provide size hint for flow layout."""
        aspect_ratio = 1.41
        thumb_height = int(self.thumbSize * aspect_ratio)
        total_height = 24 + thumb_height + 32 + 32  # label + thumb + button + margins
        return QtCore.QSize(self.thumbSize + 24, total_height)

    def updateImage(self) -> None:
        """Update the thumbnail image."""
        if self.pageNum in self.viewer.thumbnails:
            pixmap = QtGui.QPixmap.fromImage(self.viewer.thumbnails[self.pageNum])
            aspect_ratio = 1.41
            display_height = int(self.thumbSize * aspect_ratio)
            scaled = pixmap.scaled(
                self.thumbSize,
                display_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.thumbnailFrame.setPixmap(scaled)

    def setSelected(self, selected: bool) -> None:
        """Highlight this thumbnail as selected using border radius."""
        self.selected = selected
        if selected:
            self.setBorderRadius(16)  # More rounded when selected
        else:
            self.setBorderRadius(8)  # Default radius

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragStartPosition = event.pos()
        super().mousePressEvent(event)

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
            if (event.pos() - self.dragStartPosition).manhattanLength() < 5:
                self.clicked.emit(self.position)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        mimeData = event.mimeData()
        if mimeData is not None and mimeData.hasText():
            event.acceptProposedAction()
            self.setBorderRadius(16)  # Visual feedback during drag

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.setBorderRadius(8 if not self.selected else 16)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        mimeData = event.mimeData()
        if mimeData is not None:
            fromPos = int(mimeData.text())
            toPos = self.position
            self.moveRequested.emit(fromPos, toPos)
            event.acceptProposedAction()
        self.setBorderRadius(8 if not self.selected else 16)
        self.setBorderRadius(8 if not self.selected else 16)
        self.setBorderRadius(8 if not self.selected else 16)
        self.setBorderRadius(8 if not self.selected else 16)
        self.setBorderRadius(8 if not self.selected else 16)
