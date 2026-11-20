# PDFEdit Roadmap

## Viewer v0.1 (Completed)

- [x] Open PDF
- [x] View PDF
- [x] Scroll PDF
- [x] Previous Page
- [x] Next Page
- [x] Zoom In
- [x] Zoom Out
- [x] Print PDF
- [x] Close PDF

## Additor v0.2 (Completed)

### Add Text (Completed)

- [x] Add Text menu item
- [x] Text input dialog
- [x] Insert text into PDF
- [x] Font selection
- [x] Font size
- [x] Color selection
- [x] Cursor-following placement preview
- [x] OK / Cancel buttons
- [x] Single-click placement
- [x] Repeat text entry
- [x] Preserve previous font selection
- [x] Preserve previous font size
- [x] Preserve previous color selection

### Insert Images (Completed)

- [x] Add Image menu item
- [x] Image file selection
- [x] PNG support
- [x] JPG support
- [x] JPEG support
- [x] BMP support
- [x] Small size
- [x] Medium size
- [x] Large size
- [x] X-Large size
- [x] Aspect ratio preservation
- [x] Phone image orientation correction
- [x] Mouse placement
- [x] Performance optimization

### Signatures (Completed)

- [x] Add Signature menu item
- [x] Signature input dialog
- [x] Great Vibes font
- [x] Allura font
- [x] Dancing Script font
- [x] Conservative size
- [x] Typical size
- [x] Formal size
- [x] Showpiece size
- [x] Mouse placement
- [x] OK / Cancel buttons

### Date (Completed)

- [x] Add Date menu item
- [x] Current date generation
- [x] Insert date into PDF
- [x] Font selection
- [x] Font size selection
- [x] Color selection
- [x] Mouse placement
- [x] OK / Cancel buttons

### QR Code (Completed)

- [x] Add QR Code menu item
- [x] QR Code input dialog
- [x] Generate QR Code image
- [x] Temporary QR image creation
- [x] QR Code placement
- [x] Mouse placement

## Saver v0.3 (Completed)
### Save Modified PDF (Completed)

- [x] Save As

## Editor v0.4 (Completed — Core Functionality)
## Edit Existing Text (Completed)

- [x] Select text block
- [x] View/Edit selected text
- [x] Replace text within selected block
- [x] Add text within selected block
- [x] Delete text within selected block
- [x] Preserve original font size
- [x] Preserve original text color
- [x] Preserve original line height
- [x] Expand text block when required
- [x] Base-14 font fallback
- [x] Normalize replacement text

### Delete Content Block (Completed)

- [x] Delete entire selected content block
- [x] Confirmation dialog before deletion

### Text Formatting

- [ ] Improve typography fidelity
- [ ] Preserve original line breaks
- [ ] Improve unavailable font handling
- [ ] Preserve original font where supported

### Rich Text Editing

- [ ] Bold
- [ ] Italic
- [ ] Underline
- [ ] Font selection
- [ ] Font size changes
- [ ] Font color changes
- [ ] Mixed formatting within a text block

## Image Editor v0.5 (Completed — Core Functionality)

### Image Selection (Completed)

- [x] Select image
- [x] Highlight selected image
- [x] Display image information
- [x] Select rectangular region within image
- [x] Highlight selected image region
- [x] Clear image region when selection changes

### Image Editing

### Image Editing

- [ ] View image properties
- [x] Replace selected image region using overlay
- [x] Preserve replacement image aspect ratio
- [x] Correct replacement image EXIF orientation
- [x] Save and reopen PDF with replacement images
- [ ] Resize selected image
- [ ] Reposition selected image
- [ ] Delete selected image

## Usability Improvements

- [x] Unified preview placement engine for text
- [x] Cursor-following preview
- [x] Single-click placement
- [x] Repeat text workflow
- [ ] Migrate image placement to preview engine
- [ ] Migrate date placement to preview engine
- [ ] Migrate signature placement to preview engine
- [ ] Migrate QR placement to preview engine
- [ ] Keyboard nudging for precise placement


## Next Development Priorities

1. Validate core functionality through regression testing
2. Package PDFEdit for distribution
3. Test packaged application on macOS
4. Prepare external testing and feedback process
5. Resolve defects identified during testing
6. Evaluate deferred Editor and Image Editor enhancements

## Wrapitor v1.0 (Planned)

- [ ] Review runtime dependencies
- [ ] Create standalone macOS application
- [ ] Include required fonts and application assets
- [ ] Verify PDF viewing and editing in packaged application
- [ ] Verify Save As and Print
- [ ] Test application outside PyCharm
- [ ] Prepare distribution package
- [ ] Prepare tester instructions
- [ ] Distribute test release
- [ ] Collect and review tester feedback