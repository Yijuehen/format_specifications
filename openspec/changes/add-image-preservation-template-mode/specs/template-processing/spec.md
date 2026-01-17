# Template Processing Capability Specification

## ADDED Requirements

### Requirement: Image Preservation in Template Mode

The system SHALL preserve all visual content (embedded images, inline shapes, drawings) from source documents when processing in template mode, for both predefined templates and custom user templates.

#### Scenario: Template mode with images

- **GIVEN** a user uploads a Word document containing images
- **AND** the user selects a template (predefined or custom)
- **WHEN** the system processes the document using template mode
- **THEN** all images from the source document SHALL be present in the output document
- **AND** the images SHALL be inserted at reasonable positions relative to the text content

#### Scenario: Template mode without images

- **GIVEN** a user uploads a Word document with no images
- **AND** the user selects any template
- **WHEN** the system processes the document
- **THEN** the system SHALL complete processing successfully
- **AND** no image-related errors SHALL occur

#### Scenario: Multiple images in template mode

- **GIVEN** a user uploads a Word document containing 20 images
- **AND** the user selects a predefined template (e.g., ANNUAL_WORK_SUMMARY)
- **WHEN** the system processes the document
- **THEN** all 20 images SHALL be extracted from the source
- **AND** all 20 images SHALL be inserted into the output document
- **AND** processing time SHALL not increase by more than 2 seconds compared to text-only processing

#### Scenario: Custom template with images

- **GIVEN** a user uploads a Word document containing images
- **AND** the user selects a custom template from the database
- **WHEN** the system processes the document
- **THEN** all images SHALL be preserved in the output
- **AND** images SHALL be matched to appropriate sections based on context

### Requirement: Image Extraction and Tracking

The system SHALL extract images from source documents before AI text processing and track their positions relative to the document structure.

#### Scenario: Extract images with context

- **GIVEN** a source document contains images
- **WHEN** the system extracts images
- **THEN** the system SHALL save each image to a temporary file
- **AND** the system SHALL capture the paragraph index where each image was located
- **AND** the system SHALL capture text context before and after each image (up to 3 paragraphs)
- **AND** the system SHALL store this metadata for later matching

#### Scenario: Detect image types

- **GIVEN** a source document contains various visual elements
- **WHEN** the system scans for images
- **THEN** the system SHALL detect embedded images using XML patterns (`<w:drawing>`, `<pic:pic>`)
- **AND** the system SHALL detect inline shapes (`<v:shape>`, `<v:image>`)
- **AND** the system SHALL detect legacy images (`<w:pict>`)
- **AND** all detected images SHALL be included in extraction

#### Scenario: Handle extraction errors gracefully

- **GIVEN** a source document contains a corrupted or missing image file
- **WHEN** the system attempts to extract images
- **THEN** the system SHALL log a warning for the failed image
- **AND** the system SHALL continue extracting remaining images
- **AND** the overall process SHALL not fail due to individual image errors

### Requirement: Semantic Image Matching

The system SHALL match extracted images to appropriate sections in the AI-generated content using context-aware keyword matching.

#### Scenario: Match image to relevant section

- **GIVEN** an image was originally located near text about "sales performance"
- **AND** the template contains a section titled "销售业绩" (Sales Performance)
- **WHEN** the system matches images to sections
- **THEN** the image SHALL be assigned to the "销售业绩" section
- **AND** the system SHALL use keyword matching on surrounding text context

#### Scenario: Fallback for unmatched images

- **GIVEN** an image has no clear keyword match to any section
- **WHEN** the system attempts to find a matching section
- **THEN** the system SHALL assign the image to the first section with substantial content (>100 characters)
- **OR** if no such section exists, assign to the last section
- **AND** the image SHALL still appear in the output document

#### Scenario: Multiple images to same section

- **GIVEN** multiple images are matched to the same section
- **WHEN** the system builds the output document
- **THEN** all matched images SHALL be inserted in that section
- **AND** images SHALL be inserted at the end of the section content
- **AND** images SHALL be center-aligned

### Requirement: Image Reinsertion

The system SHALL reinsert matched images into the output document during the document building phase.

#### Scenario: Insert images with proper formatting

- **GIVEN** an image has been matched to a section
- **WHEN** the system builds the output document
- **THEN** the system SHALL create a new paragraph for the image
- **AND** the image SHALL be center-aligned
- **AND** the image SHALL have 12pt spacing before and after
- **AND** the image SHALL be sized according to the style configuration

#### Scenario: Handle insertion failures gracefully

- **GIVEN** an image file cannot be inserted due to corruption or format issues
- **WHEN** the system attempts to insert the image
- **THEN** the system SHALL log a warning for the failure
- **AND** the system SHALL insert placeholder text "[图片加载失败]" in place of the image
- **AND** the document generation SHALL continue successfully

#### Scenario: Verify all images inserted

- **GIVEN** 10 images were extracted from the source document
- **WHEN** the output document is generated
- **THEN** all 10 images SHALL be present in the output
- **OR** if some images failed to insert, placeholder text SHALL appear for each failed image
- **AND** the total count of images + placeholders SHALL equal 10

### Requirement: Temporary File Management

The system SHALL manage temporary image files properly to prevent disk space exhaustion.

#### Scenario: Create temporary directory for images

- **GIVEN** the system begins processing a document with images
- **WHEN** images are extracted
- **THEN** the system SHALL create a temporary directory named `docx_temp_images`
- **AND** the directory SHALL be created in the same location as the source document

#### Scenario: Cleanup temporary files after processing

- **GIVEN** temporary image files were created during processing
- **WHEN** the processing completes (success or failure)
- **THEN** the system SHALL remove all temporary image files
- **AND** the system SHALL remove the temporary directory
- **AND** the cleanup SHALL occur in the finally block to ensure execution

#### Scenario: Handle cleanup errors

- **GIVEN** the temporary directory cannot be deleted due to permission issues
- **WHEN** the system attempts cleanup
- **THEN** the system SHALL log a warning
- **AND** the system SHALL not crash or fail the overall process
- **AND** the warning SHALL include the cleanup error details

### Requirement: Performance and Scalability

The system SHALL process images efficiently with minimal performance impact.

#### Scenario: Acceptable processing time

- **GIVEN** a typical document with 10 images
- **WHEN** processed in template mode
- **THEN** the total processing time SHALL not increase by more than 2 seconds compared to text-only processing
- **AND** the user experience SHALL remain responsive

#### Scenario: Handle image-heavy documents

- **GIVEN** a document contains 50 images
- **WHEN** the system processes the document
- **THEN** the system SHALL successfully extract all 50 images
- **AND** the system SHALL successfully insert all 50 images
- **AND** the system SHALL not run out of memory
- **AND** processing time SHALL remain reasonable (<30 seconds total)

#### Scenario: Support various image formats

- **GIVEN** a document contains images in different formats (PNG, JPG, GIF)
- **WHEN** the system processes the document
- **THEN** the system SHALL extract PNG images correctly
- **AND** the system SHALL extract JPG images correctly
- **AND** the system SHALL extract GIF images correctly
- **AND** all formats SHALL be preserved in the output

### Requirement: Backward Compatibility

The system SHALL maintain backward compatibility with existing functionality.

#### Scenario: Simple mode unchanged

- **GIVEN** a user processes a document in simple mode (not template mode)
- **WHEN** the system processes the document
- **THEN** the existing image preservation logic SHALL continue to work
- **AND** no changes SHALL be made to `AIWordFormatter._process_with_ai()`
- **AND** the behavior SHALL be identical to before this change

#### Scenario: Template mode without images

- **GIVEN** a user processes a text-only document in template mode
- **WHEN** the system processes the document
- **THEN** the system SHALL generate the output using only AI-generated text
- **AND** the system SHALL not fail or report errors due to lack of images
- **AND** the output SHALL match the current behavior exactly

#### Scenario: Existing templates work unchanged

- **GIVEN** the system has existing predefined templates (ANNUAL_WORK_SUMMARY, PROJECT_REPORT, etc.)
- **WHEN** these templates are used with the new image preservation feature
- **THEN** the template structure SHALL remain unchanged
- **AND** the AI text generation SHALL work identically
- **AND** images SHALL be added as an additional enhancement only
