# PDF Presenter - Project Structure

## Overview
The application is split into two modes: Editor Mode for organizing slides, and Presentation Mode for delivering the presentation.

## File Organization

### Main Entry Point
- **`main.py`** - Application entry point that launches the editor window

### Core Windows

- **`editor_window.py`** - Contains the `EditorWindow` class
  - Main editing interface with toolbar
  - PDF import and slide organization
  - Launches presentation mode

- **`presentation_window.py`** - Contains `PresentationWindow` and `ProjectorWindow` classes
  - Presenter view with notes, timer, and preview
  - Projector window for full-screen display
  - Handles navigation and slide jumping

### Component Modules

- **`slide_organizer.py`** - Contains `SlideOrganizer` and `SlideThumbnail` classes
  - Grid view of slide thumbnails
  - Drag-and-drop reordering
  - Slide deletion and navigation
  - Click-to-jump during presentation

- **`notes.py`** - Contains the `Notes` class
  - Text editor for speaker notes
  - Per-slide note storage and retrieval
  - Auto-save functionality

- **`timer.py`** - Contains the `PauseableTimer` class
  - Pauseable presentation timer
  - Time formatting utilities

### Legacy Modules

- **`projector_view.py`** - Contains the legacy `ProjectorView` class (deprecated, replaced by ProjectorWindow)
- **`pdf_view.py`** - Contains the `PDFView` class (legacy, currently unused)

## Application Flow

1. **Launch** → Opens `EditorWindow`
2. **Import PDF** → User loads PDF file
3. **Organize** → User reorders/removes slides in `SlideOrganizer`
4. **Present** → Opens `PresentationWindow` (presenter) and `ProjectorWindow` (audience)
5. **Navigate** → Arrow keys or click thumbnails to move through slides
6. **Exit** → Returns to editor mode
