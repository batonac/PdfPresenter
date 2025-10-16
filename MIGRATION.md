# Migration from Qt Widgets to QML

This document explains the migration from Qt Widgets to Qt Quick/QML.

## Why QML?

The migration to QML provides several benefits:

1. **Declarative UI**: More readable and maintainable code
2. **Better Separation**: Clear separation between UI (QML) and logic (Python)
3. **Modern Look**: FluentWinUI3-inspired styling without external dependencies
4. **Responsive Layouts**: Flow and Layout components adapt naturally
5. **Smooth Animations**: Built-in animation framework
6. **Easier Customization**: Styling and theming is much simpler

## Architecture Changes

### Before (Qt Widgets)
```python
# editor_window.py
class EditorWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        # Mix of UI and logic
        self.pdfImages = {}
        self.initUI()
        self.renderImages()
```

### After (QML + Backend)
```python
# pdf_backend.py
class PdfBackend(QtCore.QObject):
    slideOrderChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._thumbnails = {}
        # Pure logic, no UI
```

```qml
// Main.qml
ApplicationWindow {
    // Declarative UI
    SlideOrganizer {
        model: pdfBackend.slideModel
    }
}
```

## Key Differences

### UI Construction

**Qt Widgets (Imperative)**
```python
layout = QtWidgets.QVBoxLayout()
button = PushButton("Import")
button.clicked.connect(self.importPDF)
layout.addWidget(button)
```

**QML (Declarative)**
```qml
ColumnLayout {
    Button {
        text: "Import"
        onClicked: pdfBackend.importFile()
    }
}
```

### Data Binding

**Qt Widgets**
```python
# Manual updates
def updateSlideCount(self):
    self.label.setText(f"{len(self.slides)} slides")
```

**QML**
```qml
// Automatic updates
Text {
    text: pdfBackend.slideCount + " slides"
}
```

### Layout Management

**Qt Widgets**
```python
# Fixed layouts
self.flowLayout = FlowLayout()  # From qfluentwidgets
self.flowLayout.addWidget(thumbnail)
```

**QML**
```qml
// Responsive flow
Flow {
    spacing: 20
    Repeater {
        model: pdfBackend.slideModel
        SlideThumbnail { }
    }
}
```

## Component Mapping

| Qt Widgets | QML | Notes |
|------------|-----|-------|
| `SplitFluentWindow` | `ApplicationWindow` | No external dependency needed |
| `PushButton` | `Button` | Native Qt Quick control |
| `CardWidget` | `Rectangle` | Custom styled rectangle |
| `FlowLayout` | `Flow` | Built-in Qt Quick layout |
| `ScrollArea` | `ScrollView` | Built-in Qt Quick control |
| `QLabel` (image) | `Image` | Image provider for QImages |
| `QtWidgets.QTextEdit` | `TextArea` | Built-in Qt Quick control |

## Signal/Slot Communication

### Python → QML
**Signals**: Automatically available in QML
```python
class PdfBackend(QtCore.QObject):
    slideOrderChanged = Signal()
```

```qml
Connections {
    target: pdfBackend
    function onSlideOrderChanged() {
        // Handle signal
    }
}
```

### QML → Python
**Slots**: Call directly from QML
```python
@Slot(str)
def importFile(self, filepath: str):
    # Handle import
```

```qml
Button {
    onClicked: pdfBackend.importFile(filePath)
}
```

## Properties

**Qt Widgets**: Manual getters/setters
```python
def getCurrentPage(self):
    return self.currentPage

def setCurrentPage(self, page):
    self.currentPage = page
    self.update()
```

**QML**: Automatic binding
```python
@Property(int, notify=currentPageChanged)
def currentPage(self):
    return self._currentPage

@currentPage.setter
def currentPage(self, value):
    if self._currentPage != value:
        self._currentPage = value
        self.currentPageChanged.emit()
```

```qml
// Automatically updates when property changes
Text { text: "Page " + pdfBackend.currentPage }
```

## Styling

### Qt Widgets
```python
# Requires FluentWidgets library
from qfluentwidgets import setTheme, Theme
setTheme(Theme.LIGHT)
```

### QML
```qml
// Pure QML styling
Button {
    background: Rectangle {
        color: parent.pressed ? "#005A9E" : "#0078D4"
        radius: 4
    }
}
```

## Image Display

### Qt Widgets
```python
pixmap = QtGui.QPixmap.fromImage(image)
label = QtWidgets.QLabel()
label.setPixmap(pixmap)
```

### QML + Image Provider
```python
class SlideImageProvider(QtQuick.QQuickImageProvider):
    def requestImage(self, id, size, requestedSize):
        return self._images[int(id)]
```

```qml
Image {
    source: "image://slideimage/" + position
}
```

## Models

### Qt Widgets
```python
# Manual list management
for i, slide in enumerate(self.slides):
    widget = SlideThumbnail(slide)
    self.layout.addWidget(widget)
```

### QML + Model
```python
class SlideModel(QtCore.QAbstractListModel):
    def rowCount(self, parent):
        return len(self._slides)
    
    def data(self, index, role):
        return self._slides[index.row()]
```

```qml
Repeater {
    model: pdfBackend.slideModel
    delegate: SlideThumbnail {
        slideImage: model.slideImage
    }
}
```

## Dependencies Removed

- ❌ `pyside6-fluent-widgets` - No longer needed
- ✅ `pyside6` >= 6.10.0 - All we need!

## File Changes

### Removed
- Dependencies on `qfluentwidgets` package
- Complex widget hierarchy management
- Manual UI updates and signal handling

### Added
- `qml/` directory with declarative UI
- `pdf_backend.py` with clean separation
- Image providers for QML

### Modified
- `main.py` - Now uses QQmlApplicationEngine
- `pyproject.toml` - Removed FluentWidgets dependency

### Kept (Legacy)
- `editor_window.py`
- `presentation_window.py`
- `slide_organizer.py`
- `file_browser.py`
- `notes.py`
- `pdf_view.py`

These are kept for reference but no longer used.

## Benefits Achieved

✅ **Cleaner Code**: Separation of concerns  
✅ **No External UI Dependencies**: Pure PySide6  
✅ **Modern Styling**: FluentWinUI3-inspired without libraries  
✅ **Better Maintainability**: Declarative UI is easier to understand  
✅ **Responsive Layouts**: Flow automatically adapts to window size  
✅ **Future-Proof**: Qt Quick is the future of Qt UI development
