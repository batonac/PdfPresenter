# PDF Presenter

A PDF presentation tool with presenter view, notes, and timer functionality built with PyQt6.

## Features

- Dual window display (presenter view and projection view)
- Speaker notes with autosave
- Built-in timer
- Keyboard shortcuts for navigation
- Full-screen presentation mode

## Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- PyQt6
- qpageview (modern PDF rendering library for Qt6)

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

This application uses `qpageview` for PDF rendering, which is a modern Qt6-compatible library. 
The original `python-poppler-qt` bindings were never officially ported to Qt6, so `qpageview` 
provides a clean alternative with better Qt6 integration.

## Usage

Run with uv:
```bash
uv run pdfpresenter
```

Or run the script directly:
```bash
uv run python main.py
```

### Keyboard Shortcuts

- **O**: Open PDF file
- **Left Arrow**: Previous slide
- **Right Arrow**: Next slide
- **F11** or **F**: Toggle fullscreen
- **Ctrl+S**: Save notes
- **Q**: Quit (from projection window)

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
├── main.py                 # Main application file with QtPDFViewer
├── projector_view.py       # ProjectorView - presentation window
├── slide_organizer.py      # SlideOrganizer and SlideThumbnail classes
├── notes.py                # Notes - speaker notes editor
├── timer.py                # PauseableTimer - presentation timer
├── pdf_view.py             # PDFView - legacy PDF view widget
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
