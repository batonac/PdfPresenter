# PDF Presenter - Project Structure

## Overview
The project has been refactored to separate concerns into individual modules for better organization and maintainability.

## File Organization

### Main Entry Point
- **`main.py`** - Contains the main `QtPDFViewer` class and application entry point
  - Main application window with slide organizer, clock, and notes
  - Coordinates between all components
  - Handles PDF loading and rendering

### Component Modules

- **`projector_view.py`** - Contains the `ProjectorView` class
  - Presentation/projector window for displaying slides
  - Handles fullscreen mode and navigation shortcuts
  - Manages slide rendering and scrolling

- **`slide_organizer.py`** - Contains `SlideOrganizer` and `SlideThumbnail` classes
  - Grid view of slide thumbnails
  - Drag-and-drop reordering
  - Slide deletion and navigation

- **`notes.py`** - Contains the `Notes` class
  - Text editor for speaker notes
  - Per-slide note storage and retrieval
  - Auto-save functionality

- **`timer.py`** - Contains the `PauseableTimer` class
  - Pauseable presentation timer
  - Time formatting utilities

- **`pdf_view.py`** - Contains the `PDFView` class (legacy)
  - Original PDF view widget (currently unused)
  - Kept for potential future use

## Dependencies

Each module imports only what it needs:
- All UI modules depend on PyQt6
- Component modules use TYPE_CHECKING to avoid circular imports when referencing QtPDFViewer
- Main module imports all component classes

## Benefits of This Organization

1. **Separation of Concerns** - Each class has its own file
2. **Easier Maintenance** - Smaller, focused files are easier to understand and modify
3. **Better Reusability** - Components can be imported individually
4. **Clearer Dependencies** - Import statements show module relationships
5. **Improved Testability** - Individual modules can be tested in isolation
