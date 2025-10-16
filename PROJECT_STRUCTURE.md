# PDF Presenter - Project Structure

## Overview
The application uses a **declarative QML UI** with a Python backend. It has two modes: Editor Mode for organizing slides, and Presentation Mode for delivering the presentation.

## Architecture

### Declarative UI (QML)
The user interface is built with Qt Quick/QML for a modern, declarative approach:
- Clear separation between UI and business logic
- Responsive layouts using Flow, ColumnLayout, RowLayout
- Modern FluentWinUI3-inspired styling
- Smooth animations and transitions

### Backend (Python)
The Python backend handles all business logic:
- PDF loading and rendering using QtPdf
- Slide organization and management
- Notes storage and retrieval
- Timer functionality
- Image providers for QML

## File Organization

### Main Entry Point
- **`main.py`** - Application entry point
  - Initializes QQmlApplicationEngine
  - Registers backend and image providers
  - Loads Main.qml

### Backend Logic
- **`pdf_backend.py`** - Core business logic
  - `PdfBackend` class - Main backend exposed to QML
  - `SlideModel` - QAbstractListModel for slides
  - `SlideImageProvider` - Image provider for thumbnails
  - `ProjectionImageProvider` - Image provider for full-size images
  - PDF import/export functionality
  - Slide organization (add, remove, reorder)
  - Notes management
  - Presentation state management

- **`timer.py`** - Timer functionality
  - `PauseableTimer` class
  - Time formatting utilities

### QML UI Files

#### Main Window
- **`qml/Main.qml`** - Main application window
  - Navigation sidebar with actions
  - Slide organizer view
  - File dialogs for import/export
  - Error dialogs

#### Components
- **`qml/components/NavButton.qml`** - Navigation button
  - Reusable button for sidebar actions
  - Hover effects and styling

- **`qml/components/SlideOrganizer.qml`** - Slide organizer
  - Flow layout for responsive grid
  - Empty state display
  - Drag & drop support
  - Size control slider

- **`qml/components/SlideThumbnail.qml`** - Individual slide card
  - Slide preview image
  - Page number display
  - Delete button
  - Selection state
  - Click-to-jump functionality

#### Views
- **`qml/views/PresentationView.qml`** - Presentation mode
  - Presenter window with preview, timer, notes
  - Projector window for full-screen display
  - Keyboard shortcuts
  - Dual window management

### Legacy Files (Qt Widgets)
These files are from the previous Qt Widgets implementation and are kept for reference but no longer used:
- **`editor_window.py`** - Old EditorWindow (Qt Widgets)
- **`presentation_window.py`** - Old PresentationWindow (Qt Widgets)
- **`slide_organizer.py`** - Old SlideOrganizer (Qt Widgets)
- **`file_browser.py`** - Old FileBrowser (Qt Widgets)
- **`notes.py`** - Old Notes (Qt Widgets)
- **`pdf_view.py`** - Old PDFView (Qt Widgets)

## Data Flow

1. **PDF Import**
   - User selects PDF via FileDialog
   - `PdfBackend.importFile()` called
   - QPdfDocument loads and renders pages
   - Thumbnails cached in backend
   - `SlideModel` updated
   - QML UI updates automatically via bindings

2. **Slide Organization**
   - User interacts with `SlideThumbnail` in QML
   - Signals trigger backend methods
   - Backend updates `_slideOrder` list
   - Model emits dataChanged
   - QML view updates

3. **Presentation Mode**
   - User clicks "Present" button
   - `presentationMode` property set to true
   - `PresentationView` window shown
   - Backend renders full-size images
   - Notes loaded for current slide
   - Image providers serve images to QML

4. **Navigation**
   - Arrow keys trigger `nextSlide()`/`prevSlide()`
   - Backend updates `currentPage` property
   - Property binding updates QML
   - Image sources reloaded
   - Notes updated

## Application Flow

1. **Launch** → `main.py` creates engine and loads `Main.qml`
2. **Import PDF** → User selects file, backend loads and renders
3. **Organize** → User interacts with slides in Flow layout
4. **Present** → `PresentationView` window opens with dual display
5. **Navigate** → Arrow keys or clicks trigger backend methods
6. **Exit** → Presentation window closes, returns to editor mode
