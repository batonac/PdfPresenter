#!/usr/bin/env python
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
import sys
import traceback

from PySide6 import QtWidgets

from editor_window import EditorWindow


def excepthook(exc_type, exc_value, exc_tb):
    """Global exception handler to catch crashes."""
    print("\n" + "=" * 80)
    print("UNHANDLED EXCEPTION:")
    print("=" * 80)
    traceback.print_exception(exc_type, exc_value, exc_tb)
    print("=" * 80 + "\n")
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main() -> None:
    # Install global exception handler
    sys.excepthook = excepthook

    print("Starting PDF Presenter...")
    app = QtWidgets.QApplication(sys.argv)

    try:
        print("Creating EditorWindow...")
        editor = EditorWindow()
        print("Showing EditorWindow...")
        editor.show()
        print("Entering event loop...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Fatal error in main: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
