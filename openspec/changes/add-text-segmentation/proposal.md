# Change: Add Text Segmentation and Structured Extraction

## Why

Users need the ability to extract structured information from text documents and perform intelligent text segmentation. Currently, the system only provides basic text polishing via AI. There's no way to:

1. Extract key points from text in a structured format (e.g., Cause, Process, Result)
2. Segment long text into logical sections without AI processing
3. Configure different extraction patterns based on document needs

This limitation prevents users from quickly analyzing document structure and extracting critical information for reports, summaries, or further processing.

## What Changes

- **Add new methods to `AITextProcessor`** in `format_specifications/utils/ai_word_utils.py`:
  - `extract_structure(text, template)` - Extract structured information using AI
  - `segment_text(text, mode)` - Segment text using rule-based patterns
  - `extract_with_template(text, fields)` - Extract specific fields using custom templates

- **Add template configuration** for common extraction patterns:
  - `cause_process_result` - Extract cause, process, and result points
  - `problem_solution` - Extract problems and solutions
  - `summary_bullets` - Extract key points as bullet list

- **Add segmentation modes**:
  - `paragraph` - Split by paragraph boundaries
  - `sentence` - Split by sentence boundaries
  - `semantic` - Split by semantic sections (headings, logical blocks)

- **Add hybrid processing option** - Use AI for complex extraction, rules for simple segmentation

- **Extend caching mechanism** to support template-based extraction results

## Impact

- **Affected specs**: New capability `text-segmentation`
- **Affected code**:
  - `format_specifications/utils/ai_word_utils.py` - Add segmentation methods to AITextProcessor
  - `format_specifications/views.py` - Optional: Add new endpoint for segmentation API
  - Tests: Add unit tests for segmentation functionality

- **Backwards compatibility**: No breaking changes - all additions are new methods
- **Performance**: Rule-based segmentation adds minimal overhead; AI extraction uses existing caching
- **AI costs**: Template-based extraction will use AI API, but cached results reduce redundant calls
