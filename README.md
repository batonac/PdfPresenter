# PDF Presenter

A PDF presentation tool with presenter view, notes, and timer functionality built with PySide6 and Qt Quick QML.

## Features

- **Modern QML UI**: Declarative interface with native **FluentWinUI3 Style** from Qt Core
- **Integrated Navigation**: Files and slides in a unified interface
- **Drag & Drop Import**: Drag PDF files into slide organizer
- **Multi-PDF Support**: Import pages from multiple PDF documents
- **Slide Organization**: Reorder and remove slides before presenting
- **PDF Export**: Save your organized slides as a new PDF
- **Presentation Mode**: Dual window display (presenter view and projection view)
- **Responsive Layouts**: Flow-based layout for optimal slide organization
- Speaker notes with autosave
- Built-in timer
- Keyboard shortcuts for navigation
- Full-screen presentation mode
- Click-to-jump slide navigation

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- PySide6 >= 6.10.0 (includes QtPdf and Qt Quick)
- PyMuPDF (for PDF export)

## Installation

1. Install uv if you haven't already:
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone and setup the project:
```bash
cd c:\Users\Shenks\Development\PdfPresenter
uv sync
```

Or install with development dependencies:
```bash
uv sync --all-extras
```

## Technical Notes

This application uses:
- **PySide6 6.10+** for Qt6 bindings (official Qt support)
- **Qt Quick/QML** for declarative UI with the native **FluentWinUI3 Style** (Qt 6.8+)
- **QtPdf** (built into PySide6) for native PDF rendering
- **Qt Quick Layouts** for responsive, flow-based slide organization

The declarative QML approach provides:
- Cleaner separation of UI and business logic
- More maintainable and understandable code
- Modern, smooth animations and transitions
- Native FluentWinUI3 styling without external dependencies

The **FluentWinUI3 Style** is a modern, native-looking style designed for platforms running Windows 11 and above. It draws inspiration from the Fluent UI design and the WinUI3 framework, and can be run on all supported platforms.

QtPdf provides native, high-performance PDF rendering that's fully integrated with Qt, eliminating the need for external dependencies.

## Usage

Run with uv:
```bash
uv run pdfpresenter
```

Or run the script directly:
```bash
uv run python main.py
```

### Workflow

1. **Editor Mode** (opens by default):
   - Click "Browse Folder" in the navigation sidebar to select a folder with PDFs
   - PDF files appear in the navigation tree
   - **Double-click** a PDF file to import it
   - **Drag and drop** PDF files from the navigation tree into the slide organizer
   - Or use "Import PDF" to select files manually
   - In the slide organizer:
     - Drag thumbnails to reorder slides
     - Select and delete unwanted slides
     - Adjust thumbnail size with the slider
   - Use navigation actions:
     - "Export PDF" to save your organized slides
     - "Remove Page" to delete selected slide
     - "Present" to start presentation mode

2. **Presentation Mode**:
   - Presenter view shows current slide preview, notes, and timer
   - Projector window shows full-screen slides
   - Click slides in editor to jump during presentation

### Keyboard Shortcuts

**Editor Mode:**
- **Ctrl+O**: Import PDF file

**Presentation Mode:**
- **Left Arrow**: Previous slide
- **Right Arrow**: Next slide
- **F11** or **F**: Toggle fullscreen (projector window)
- **Ctrl+S**: Save notes
- **Escape** or **Q**: Exit presentation mode

## Development

### Running in VSCode

1. Open the project folder in VSCode
2. Run `uv sync --all-extras` to install all dependencies
3. VSCode will automatically detect the `.venv` created by uv
4. Press F5 to start debugging

### Available Tasks

- **Ctrl+Shift+B**: Run PDF Presenter
- **Ctrl+Shift+P** → "Tasks: Run Task":
  - Sync Dependencies
  - Sync Dev Dependencies
  - Format Code
  - Lint Code
  - Add Dependency

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

### uv Commands

```bash
# Sync dependencies with lockfile
uv sync

# Run a command in the virtual environment
uv run python script.py

# Run the application
uv run pdfpresenter

# Update dependencies
uv lock --upgrade
uv sync
```

## Project Structure

```
PdfPresenter/
├── main.py                 # Application entry point (QML engine)
├── pdf_backend.py          # Backend logic and models for QML
├── timer.py                # PauseableTimer - presentation timer
├── qml/                    # QML UI files
│   ├── Main.qml           # Main application window
│   ├── qmldir             # QML module definition
│   ├── components/        # Reusable UI components
│   │   ├── NavButton.qml
│   │   ├── SlideOrganizer.qml
│   │   └── SlideThumbnail.qml
│   └── views/             # Main views
│       └── PresentationView.qml
├── editor_window.py        # (Legacy) EditorWindow - Qt Widgets version
├── presentation_window.py  # (Legacy) PresentationWindow - Qt Widgets version
├── slide_organizer.py      # (Legacy) SlideOrganizer - Qt Widgets version
├── notes.py                # (Legacy) Notes - Qt Widgets version
├── pyproject.toml          # Project configuration and dependencies
├── uv.lock                 # Lockfile for reproducible installs
├── PROJECT_STRUCTURE.md    # Detailed project organization
├── README.md               # This file
└── .vscode/                # VSCode configuration
    ├── launch.json         # Debug configurations
    ├── settings.json       # Workspace settings
    └── tasks.json          # Build and run tasks
```

## License

This program is licensed under the GNU General Public License v3.0 or later.
See LICENSE file for details.
