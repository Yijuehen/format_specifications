# Implementation Tasks

## 1. Core Implementation
- [x] 1.1 Add `EXTRACTION_TEMPLATES` class attribute to `AITextProcessor` with predefined templates
- [x] 1.2 Implement `extract_structure(text, template)` method in `AITextProcessor`
  - [x] 1.2.1 Add template validation (resolve string to field list, validate custom lists)
  - [x] 1.2.2 Implement cache key generation including template hash
  - [x] 1.2.3 Build AI prompt with field instructions and explicit "no fabrication" constraints
  - [x] 1.2.4 Call AI API with existing retry logic
  - [x] 1.2.5 Parse AI response into structured dictionary
  - [x] 1.2.6 **CRITICAL**: Validate extracted content exists in source text (substring check)
  - [x] 1.2.7 Log warning if extracted content is not found in source (potential AI fabrication)
  - [x] 1.2.8 Handle errors gracefully (return empty dict, log error)
- [x] 1.3 Implement `segment_text(text, mode, include_metadata)` method
  - [x] 1.3.1 Add mode validation (paragraph, sentence, semantic)
  - [x] 1.3.2 Implement paragraph segmentation (split by `\n\n`, filter empty)
  - [x] 1.3.3 Implement sentence segmentation (Chinese and English punctuation patterns)
  - [x] 1.3.4 Implement semantic segmentation (heading detection, content grouping)
  - [x] 1.3.5 Add optional metadata generation (type, position)
- [x] 1.4 Implement `extract_with_template(text, fields)` convenience method
- [x] 1.5 Add helper methods for prompt generation and response parsing
  - [x] 1.5.1 `_build_extraction_prompt(fields, text)` - Generate structured prompt with anti-fabrication constraints
  - [x] 1.5.2 `_parse_extraction_response(response_text, fields)` - Parse AI response to dict
  - [x] 1.5.3 **CRITICAL**: `_validate_extracted_content(extracted_data, source_text)` - Check if extracted content exists in source
  - [x] 1.5.4 `_segment_by_sentences(text)` - Regex-based sentence splitting
  - [x] 1.5.5 `_segment_by_semantic(text)` - Heading-based segmentation

## 2. Testing
- [x] 2.1 Create unit tests for `extract_structure()` method
  - [x] 2.1.1 Test with predefined template (cause_process_result)
  - [x] 2.1.2 Test with custom template (field list)
  - [x] 2.1.3 **CRITICAL**: Test no content fabrication - partial content in source
  - [x] 2.1.4 **CRITICAL**: Test all fields empty when source has no matching content
  - [x] 2.1.5 **CRITICAL**: Test validation detects AI-fabricated content
  - [x] 2.1.6 Test cache hit/miss behavior
  - [x] 2.1.7 Test AI API failure handling
  - [x] 2.1.8 Test empty text input
  - [x] 2.1.9 Test invalid template (fallback to default)
- [x] 2.2 Create unit tests for `segment_text()` method
  - [x] 2.2.1 Test paragraph segmentation mode
  - [x] 2.2.2 Test sentence segmentation mode (Chinese and English)
  - [x] 2.2.3 Test semantic segmentation mode
  - [x] 2.2.4 Test metadata inclusion
  - [x] 2.2.5 Test empty text input
  - [x] 2.2.6 Test invalid mode (raise error or fallback)
- [x] 2.3 Create integration tests
  - [x] 2.3.1 Test extraction + segmentation workflow
  - [x] 2.3.2 Test with real document samples
  - [x] 2.3.3 Test concurrent request handling
- [x] 2.4 Add test fixtures and sample data
  - [x] 2.4.1 Sample Chinese text paragraphs
  - [x] 2.4.2 Sample text with headings
  - [x] 2.4.3 Sample documents for extraction

## 3. Documentation
- [x] 3.1 Add docstrings to new methods (Google style or NumPy style)
  - [x] 3.1.1 Document parameters, return types, and examples
  - [x] 3.1.2 Document available templates and modes
  - [x] 3.1.3 Document error handling behavior
- [ ] 3.2 Update `openspec/project.md` if needed (new capabilities section)
- [ ] 3.3 Add usage examples in code comments or separate examples file
  - [ ] 3.3.1 Example: Extract cause-process-result from report
  - [ ] 3.3.2 Example: Segment long document into sentences
  - [ ] 3.3.3 Example: Custom template for specific use case

## 4. Code Quality
- [x] 4.1 Add type hints to all new methods
- [x] 4.2 Add logging statements for debugging (info, warning, error)
- [x] 4.3 Ensure consistent error handling with existing code
- [ ] 4.4 Run code linting and formatting (black, flake8, mypy)
- [x] 4.5 Review code for performance considerations
  - [x] 4.5.1 Check regex patterns for efficiency
  - [x] 4.5.2 Validate cache key generation doesn't cause collisions
  - [x] 4.5.3 Ensure no memory leaks in caching

## 5. Optional Enhancements
- [ ] 5.1 Add Django view/endpoint for web API access (if requested)
  - [ ] 5.1.1 Create URL route in `urls.py`
  - [ ] 5.1.2 Implement view function in `views.py`
  - [ ] 5.1.3 Add request validation and error handling
  - [ ] 5.1.4 Return JSON responses
- [x] 5.2 Add more predefined templates based on common use cases
  - [x] 5.2.1 `problem_solution` template
  - [x] 5.2.2 `summary_bullets` template
  - [ ] 5.2.3 `background_analysis_conclusion` template
- [ ] 5.3 Add batch processing support for multiple texts
- [ ] 5.4 Add configuration options in Django settings
  - [ ] 5.4.1 Custom template definitions
  - [ ] 5.4.2 Segmentation pattern customization

## 6. Validation and Deployment
- [ ] 6.1 Run `openspec validate add-text-segmentation --strict`
- [ ] 6.2 Fix any validation errors
- [ ] 6.3 Run full test suite and ensure all tests pass
- [ ] 6.4 Test manually with sample documents
- [ ] 6.5 Create git commit with conventional commit message
- [ ] 6.6 Update proposal status (ready for review/approval)

## Dependencies and Parallel Work

**Can be done in parallel**:
- Tasks 1.2-1.4 (method implementations) can be done independently
- Tasks 2.1-2.2 (unit tests) can be written alongside implementation
- Tasks 3.1-3.3 (documentation) can be done in parallel with coding

**Must be sequential**:
- Task 1.1 must be done before 1.2-1.4 (templates needed first)
- Task 1.5 helpers must be done before 1.2-1.3 (implementation depends on helpers)
- Task 6 (validation) must be last (requires all other tasks complete)

**External dependencies**:
- None - all work is self-contained in existing files
- No new Python packages required
- No database migrations needed
