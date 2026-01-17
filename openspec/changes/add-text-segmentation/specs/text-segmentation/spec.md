## ADDED Requirements

### Requirement: Structured Text Extraction
The system SHALL provide the ability to extract structured information from text using predefined templates or custom field specifications.

#### Scenario: Extract cause-process-result structure
- **GIVEN** a text document containing narrative information
- **WHEN** user requests extraction with `cause_process_result` template
- **THEN** system SHALL return structured data with three fields: "cause", "process", "result"
- **AND** each field SHALL contain the relevant extracted text content
- **AND** extraction SHALL use AI processing for accurate content identification

#### Scenario: Extract with custom template
- **GIVEN** a text document
- **AND** a custom template with fields ["background", "analysis", "conclusion"]
- **WHEN** user requests extraction with the custom template
- **THEN** system SHALL return structured data with the specified fields
- **AND** system SHALL populate each field with relevant content from the text

#### Scenario: Handle extraction with missing content
- **GIVEN** a text document
- **WHEN** user requests extraction with a template
- **AND** the text does not contain content for one or more template fields
- **THEN** system SHALL return the structure with empty strings for missing fields
- **AND** system SHALL not raise an error for missing content

#### Scenario: No content fabrication
- **GIVEN** a text document
- **WHEN** user requests extraction with a template
- **AND** the text does not contain information for a specific field
- **THEN** system MUST NOT generate, invent, or fabricate content for that field
- **AND** system MUST return an empty string for fields with no matching content
- **AND** system MUST only extract content that explicitly exists in the source text

#### Scenario: Partial content extraction
- **GIVEN** a text document that only contains 2 out of 3 requested fields
- **WHEN** user requests extraction with `cause_process_result` template
- **AND** the text contains "cause" and "result" but no "process" information
- **THEN** system SHALL extract and return content for "cause" and "result" fields
- **AND** system SHALL return empty string for "process" field
- **AND** system MUST NOT create or infer "process" content from other parts of the text

### Requirement: Rule-Based Text Segmentation
The system SHALL provide the ability to segment text into logical parts using rule-based patterns without AI processing.

#### Scenario: Segment by paragraphs
- **GIVEN** a text document with multiple paragraphs
- **WHEN** user requests segmentation with `mode="paragraph"`
- **THEN** system SHALL return a list of text segments
- **AND** each segment SHALL correspond to one paragraph (split by double newlines)
- **AND** empty paragraphs SHALL be filtered out

#### Scenario: Segment by sentences
- **GIVEN** a text document with multiple sentences
- **WHEN** user requests segmentation with `mode="sentence"`
- **THEN** system SHALL return a list of text segments
- **AND** each segment SHALL correspond to one sentence (split by sentence-ending punctuation)
- **AND** segments SHALL preserve original sentence text without modification

#### Scenario: Segment by semantic sections
- **GIVEN** a text document with headings and sections
- **WHEN** user requests segmentation with `mode="semantic"`
- **THEN** system SHALL return a list of text segments
- **AND** each segment SHALL correspond to a logical section (text between headings)
- **AND** segments SHALL include the heading text as the first line of each segment

### Requirement: Hybrid Processing Mode
The system SHALL support a hybrid processing mode that automatically selects AI or rule-based processing based on the operation complexity.

#### Scenario: Hybrid mode for structured extraction
- **GIVEN** a text document
- **WHEN** user enables hybrid mode and requests structured extraction
- **THEN** system SHALL use AI processing for extraction operations
- **AND** system SHALL apply result caching to avoid redundant AI calls

#### Scenario: Hybrid mode for simple segmentation
- **GIVEN** a text document
- **WHEN** user enables hybrid mode and requests rule-based segmentation
- **THEN** system SHALL use rule-based patterns (no AI processing)
- **AND** operation SHALL complete faster than AI-based extraction

### Requirement: Extraction Result Caching
The system SHALL cache extraction results to avoid redundant AI API calls for identical text and template combinations.

#### Scenario: Cache hit for repeated extraction
- **GIVEN** a text document has been processed with template T
- **WHEN** user requests extraction with the same text and template T within 30 seconds
- **THEN** system SHALL return cached results without calling AI API
- **AND** response time SHALL be significantly faster than uncached extraction

#### Scenario: Cache miss after expiration
- **GIVEN** a text document was processed with template T more than 30 seconds ago
- **WHEN** user requests extraction with the same text and template T
- **THEN** system SHALL call AI API for fresh extraction
- **AND** new result SHALL be cached for future requests

### Requirement: Template Configuration Management
The system SHALL provide predefined templates for common extraction patterns and support custom template definitions.

#### Scenario: Use predefined template
- **GIVEN** the system provides predefined template `cause_process_result`
- **WHEN** user specifies template="cause_process_result"
- **THEN** system SHALL use the predefined field structure ["cause", "process", "result"]
- **AND** extraction SHALL be performed using these fields

#### Scenario: Create and use custom template
- **GIVEN** user defines custom template with fields ["summary", "key_points", "action_items"]
- **WHEN** user passes this custom template to extraction method
- **THEN** system SHALL use the custom field structure for extraction
- **AND** result SHALL match the custom field names

#### Scenario: Invalid template handling
- **GIVEN** user specifies an invalid template name
- **WHEN** user requests extraction with the invalid template
- **THEN** system SHALL log a warning message
- **AND** system SHALL fall back to default template
- **AND** processing SHALL continue without error

### Requirement: Segmentation Output Format
The system SHALL return segmentation results in a consistent, machine-readable format.

#### Scenario: Return list of text segments
- **GIVEN** a text document segmented into N parts
- **WHEN** segmentation operation completes
- **THEN** system SHALL return a list of strings
- **AND** each string SHALL contain one text segment
- **AND** segments SHALL be in original document order

#### Scenario: Include metadata in segmentation result
- **GIVEN** a text document segmented with `include_metadata=True`
- **WHEN** segmentation operation completes
- **THEN** system SHALL return a list of dictionaries
- **AND** each dictionary SHALL contain "text" and "type" keys
- **AND** "type" SHALL indicate the segment type (e.g., "heading", "paragraph", "sentence")

### Requirement: Error Handling and Fallbacks
The system SHALL handle errors gracefully and provide meaningful fallback behavior.

#### Scenario: AI API failure during extraction
- **GIVEN** an extraction request that requires AI processing
- **WHEN** AI API call fails after all retry attempts
- **THEN** system SHALL log the error
- **AND** system SHALL return a fallback structure with empty field values
- **AND** system SHALL not raise an exception to the caller

#### Scenario: Empty text input handling
- **GIVEN** an empty or whitespace-only text input
- **WHEN** user requests segmentation or extraction
- **THEN** system SHALL return an empty list or empty structure
- **AND** system SHALL not call AI API for empty input
- **AND** operation SHALL complete without error
