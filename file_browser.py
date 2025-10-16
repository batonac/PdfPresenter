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

import sys
import traceback
from pathlib import Path

from PySide6 import QtCore, QtWidgets


class FileBrowserTree(QtWidgets.QTreeWidget):
    """Tree widget for browsing folders and PDF files with drag support."""

    fileDoubleClicked = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.currentPath: Path | None = None

        # Configure tree
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

        # Apply custom styling to match Fluent theme
        self.setStyleSheet(
            """
            QTreeWidget {
                background-color: transparent;
                border: none;
                outline: none;
                color: #000000;
            }
            QTreeWidget::item {
                padding: 4px;
                border-radius: 4px;
            }
            QTreeWidget::item:hover {
                background-color: rgba(0, 0, 0, 10);
            }
            QTreeWidget::item:selected {
                background-color: rgba(0, 0, 0, 15);
                color: #000000;
            }
            QTreeWidget::branch {
                background-color: transparent;
            }
        """
        )

        print("FileBrowserTree initialized successfully")

    def loadFolder(self, folder: Path) -> None:
        """Load folder structure into tree."""
        try:
            print(f"Loading folder: {folder}")

            self.clear()
            self.currentPath = folder

            if not folder.exists():
                print(f"Folder does not exist: {folder}")
                return

            # Add the root folder
            self._addFolderToTree(folder, None)

            print("Folder loaded successfully")

        except Exception as e:
            print(f"Error loading folder: {e}")
            traceback.print_exc()
            sys.stderr.write(f"FileBrowserTree.loadFolder error: {e}\n")

    def _addFolderToTree(self, folder: Path, parent: QtWidgets.QTreeWidgetItem | None) -> None:
        """Recursively add folder contents to tree."""
        try:
            # Get all items (folders and PDFs)
            items = []

            # Add subfolders
            for subfolder in sorted(folder.iterdir()):
                if subfolder.is_dir():
                    items.append((subfolder, True))

            # Add PDF files
            for pdf_file in sorted(folder.glob("*.pdf"), key=lambda p: p.name.lower()):
                items.append((pdf_file, False))

            for item_path, is_folder in items:
                if is_folder:
                    folder_item = QtWidgets.QTreeWidgetItem([item_path.name])
                    folder_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(item_path))
                    folder_item.setData(0, QtCore.Qt.ItemDataRole.UserRole + 1, "folder")
                    folder_item.setIcon(
                        0, self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon)
                    )

                    if parent:
                        parent.addChild(folder_item)
                    else:
                        self.addTopLevelItem(folder_item)

                    # Recursively add contents of subfolder
                    self._addFolderToTree(item_path, folder_item)

                else:
                    # PDF file
                    file_item = QtWidgets.QTreeWidgetItem([item_path.name])
                    file_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, str(item_path))
                    file_item.setData(0, QtCore.Qt.ItemDataRole.UserRole + 1, "file")
                    file_item.setIcon(
                        0, self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
                    )

                    if parent:
                        parent.addChild(file_item)
                    else:
                        self.addTopLevelItem(file_item)

        except Exception as e:
            print(f"Error adding folder to tree: {e}")
            traceback.print_exc()

    def onItemDoubleClicked(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        """Handle double-click on tree item."""
        try:
            item_type = item.data(0, QtCore.Qt.ItemDataRole.UserRole + 1)
            filepath = item.data(0, QtCore.Qt.ItemDataRole.UserRole)

            if item_type == "file" and filepath:
                print(f"Double-clicked file: {filepath}")
                self.fileDoubleClicked.emit(filepath)
            elif item_type == "folder":
                # Toggle folder expansion - setExpanded is the correct method
                item.setExpanded(not item.isExpanded())

        except Exception as e:
            print(f"Error in onItemDoubleClicked: {e}")
            traceback.print_exc()

    def mimeData(self, items: list[QtWidgets.QTreeWidgetItem]) -> QtCore.QMimeData:
        """Create mime data for drag operation - only for PDF files."""
        try:
            mimeData = QtCore.QMimeData()
            urls = []

            for item in items:
                item_type = item.data(0, QtCore.Qt.ItemDataRole.UserRole + 1)
                if item_type == "file":  # Only allow dragging PDF files
                    filepath = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                    if filepath:
                        urls.append(QtCore.QUrl.fromLocalFile(filepath))

            if urls:
                mimeData.setUrls(urls)

            return mimeData

        except Exception as e:
            print(f"Error creating mimeData: {e}")
            traceback.print_exc()
            return QtCore.QMimeData()
