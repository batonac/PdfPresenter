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
from pathlib import Path

from PySide6 import QtCore, QtGui, QtQml, QtQuick

from pdf_backend import PdfBackend


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
    
    # Set application attributes
    QtGui.QGuiApplication.setApplicationName("PDF Presenter")
    QtGui.QGuiApplication.setOrganizationName("PdfPresenter")
    
    # Set the FluentWinUI3 style
    import os
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "FluentWinUI3"
    
    app = QtGui.QGuiApplication(sys.argv)
    
    try:
        print("Creating QML engine...")
        engine = QtQml.QQmlApplicationEngine()
        
        # Create backend
        from pdf_backend import SlideImageProvider, ProjectionImageProvider
        backend = PdfBackend()
        
        # Register image providers
        slide_provider = SlideImageProvider(backend)
        projection_provider = ProjectionImageProvider(backend)
        engine.addImageProvider("slideimage", slide_provider)
        engine.addImageProvider("thumbnail", slide_provider)
        engine.addImageProvider("projection", projection_provider)
        
        # Register backend as context property
        engine.rootContext().setContextProperty("pdfBackend", backend)
        
        # Register custom types
        qml_import_path = Path(__file__).parent / "qml"
        engine.addImportPath(str(qml_import_path))
        
        # Load main QML file
        main_qml = qml_import_path / "Main.qml"
        print(f"Loading QML from: {main_qml}")
        engine.load(main_qml)
        
        if not engine.rootObjects():
            print("Failed to load QML file")
            sys.exit(1)
        
        print("Entering event loop...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Fatal error in main: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
