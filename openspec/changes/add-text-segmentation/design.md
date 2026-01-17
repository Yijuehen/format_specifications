# Design: Text Segmentation and Structured Extraction

## Context

The current AI text processing system focuses on text polishing and paragraph restructuring. Users need additional capabilities to:
1. Extract structured information from documents (e.g., reports with cause/process/result sections)
2. Segment long text into manageable parts for analysis
3. Perform these operations efficiently without always requiring AI processing

The system already has:
- `AITextProcessor` class with AI integration (Zhipu GLM-4)
- Caching mechanism for API results
- Retry logic and error handling
- Tone-based processing capabilities

### Constraints
- Must maintain backward compatibility with existing `AITextProcessor` methods
- AI API has rate limits and timeouts (15s default)
- Processing should work efficiently for both AI and rule-based operations
- Chinese language text is the primary use case

## Goals / Non-Goals

### Goals
- Add structured extraction methods to `AITextProcessor` using AI
- Add rule-based segmentation methods for fast text processing
- Support both predefined and custom extraction templates
- Reuse existing caching and error handling infrastructure
- Provide consistent, predictable output formats

### Non-Goals
- Creating a separate service class (extend `AITextProcessor` instead)
- Adding new external dependencies (use existing Python standard library)
- Creating database models for storing extraction results
- Building a frontend UI for this feature (API-only initially)
- Supporting real-time streaming of extraction results

## Decisions

### Decision 1: Extend AITextProcessor Class
**Choice**: Add new methods to existing `AITextProcessor` in `ai_word_utils.py`

**Rationale**:
- Code reuse: Leverages existing AI client, caching, retry logic, and error handling
- Consistency: Keeps all text processing in one place
- Simplicity: No new classes or imports needed for users
- Maintainability: Easier to update one class than multiple services

**Alternatives considered**:
- **Create new TextSegmenter class**: Rejected due to code duplication (AI client, caching, retry logic)
- **Create standalone module functions**: Rejected due to harder to maintain state and configuration

### Decision 2: Hybrid Processing Architecture
**Choice**: Separate methods for AI extraction and rule-based segmentation

**Rationale**:
- Performance: Rule-based segmentation is instant, no AI latency
- Cost: Reduces unnecessary AI API calls for simple operations
- Flexibility: Users can choose the right tool for each job
- Clarity: Separate method names make intent explicit (`extract_structure` vs `segment_text`)

**Alternatives considered**:
- **Single method with auto-detection**: Rejected due to unpredictability and potential confusion
- **AI-only approach**: Rejected due to cost and latency for simple segmentation

### Decision 3: Template System Design
**Choice**: Dictionary-based template configuration with class attribute storage

**Implementation**:
```python
class AITextProcessor:
    EXTRACTION_TEMPLATES = {
        'cause_process_result': ['cause', 'process', 'result'],
        'problem_solution': ['problem', 'solution'],
        'summary_bullets': ['summary']
    }
```

**Rationale**:
- Simple and easy to understand
- Allows users to pass custom lists as templates
- No external configuration files needed
- Easy to extend with new templates

**Alternatives considered**:
- **JSON/YAML config files**: Rejected due to added complexity and file I/O
- **Database storage**: Rejected due to overengineering for static templates

### Decision 4: Caching Strategy
**Choice**: Extend existing `@cache_text_result` decorator for extraction operations

**Rationale**:
- Code reuse: Existing decorator already handles cache key generation and expiration
- Consistency: Same 30-second cache across all AI operations
- Simplicity: No new cache implementation needed
- Performance: Avoids redundant AI calls for identical text + template combinations

**Cache key design**: Include template hash in cache key
```python
text_feature = f"{len(raw_text)}_{raw_text[:100]}_{template}"
```

**Alternatives considered**:
- **Separate cache for extraction**: Rejected due to code duplication
- **No caching for extraction**: Rejected due to wasted API calls on repeated requests

### Decision 5: Rule-Based Segmentation Algorithms
**Choice**: Use Python standard library for segmentation (re, text processing)

**Paragraph segmentation**:
- Split by `\n\n` (double newlines)
- Filter empty segments
- Strip whitespace

**Sentence segmentation**:
- Split by punctuation marks (。！？ for Chinese, .!? for English)
- Handle abbreviations and decimal points
- Preserve original spacing

**Semantic segmentation**:
- Detect headings (lines starting with specific patterns like "一、", "1.", "#")
- Group content under each heading
- Handle nested headings (depth levels)

**Rationale**:
- No external dependencies (nltk, spaCy not needed for basic segmentation)
- Sufficient accuracy for Chinese text segmentation
- Fast and lightweight
- Easy to customize patterns

**Alternatives considered**:
- **Use NLP libraries (nltk, spaCy)**: Rejected due to added dependencies and overkill
- **AI-based segmentation**: Rejected due to cost and latency for simple operations

### Decision 6: Output Format
**Choice**: Return consistent data structures
- Extraction: `dict[str, str]` - field name to extracted content
- Segmentation: `list[str]` - list of text segments
- Segmentation with metadata: `list[dict]` - each with "text" and "type" keys

**Rationale**:
- Pythonic and easy to use
- JSON-serializable for API responses
- Type-hint friendly
- Compatible with existing code patterns

**Alternatives considered**:
- **Custom result objects**: Rejected due to overengineering
- **Named tuples**: Rejected due to less flexibility than dict

### Decision 7: Error Handling Strategy
**Choice**: Graceful degradation with logging, no exceptions raised to caller

**Implementation**:
- AI API failures: Return empty structure, log error
- Empty input: Return empty result, no AI call
- Invalid templates: Fall back to default template, log warning

**Rationale**:
- Consistent with existing `process_text` behavior
- Allows caller to handle empty results without try/catch
- Production-friendly: Doesn't crash on AI failures
- Debuggable: Comprehensive logging for troubleshooting

**Alternatives considered**:
- **Raise exceptions on failures**: Rejected due to breaking existing pattern
- **Silent failures**: Rejected due to difficulty debugging

## Technical Architecture

### Method Signatures

```python
class AITextProcessor:
    # Existing methods
    def process_text(self, raw_text: str) -> str

    # New methods
    def extract_structure(
        self,
        text: str,
        template: Union[str, list[str]]
    ) -> dict[str, str]:
        """Extract structured information using AI"""

    def segment_text(
        self,
        text: str,
        mode: Literal["paragraph", "sentence", "semantic"],
        include_metadata: bool = False
    ) -> Union[list[str], list[dict]]:
        """Segment text using rule-based patterns"""

    def extract_with_template(
        self,
        text: str,
        fields: list[str]
    ) -> dict[str, str]:
        """Alias for extract_structure with custom field list"""
```

### Data Flow

**AI Extraction Flow**:
1. User calls `extract_structure(text, "cause_process_result")`
2. Method validates template and converts to field list
3. Check cache for existing result
4. If cache miss: Build AI prompt with field instructions
5. Call AI API with retry logic
6. Parse AI response into structured dict
7. Cache result
8. Return dict

**Rule-Based Segmentation Flow**:
1. User calls `segment_text(text, "sentence")`
2. Method validates mode parameter
3. Apply segmentation patterns based on mode
4. Filter empty segments
5. Optionally add metadata (type, position)
6. Return list of segments

### Prompt Engineering for Extraction

**Template prompt structure**:
```python
prompt = f"""请从以下文本中提取{len(fields)}个部分的信息：
{field_instructions}

**重要约束**：
- 只能从文本中提取明确存在的内容
- 如果文本中不包含某个字段的信息，该字段必须返回空字符串
- 绝对禁止编造、推断或生成文本中没有的内容
- 保持原文表述，不要改写或总结

文本：
{text}

请以JSON格式返回结果，字段名为：{fields}"""
```

**Example for cause_process_result**:
```python
field_instructions = """
1. 原因（cause）：问题的起因或背景
2. 过程（process）：采取的行动或处理步骤
3. 结果（result）：最终的结果或成效
"""
```

**Critical constraint enforcement**:
- Add explicit "DO NOT FABRICATE" instruction in every prompt
- Include "empty string for missing content" in system prompt
- Validate AI response against source text length (warn if response longer than source)
- Post-processing: Check if extracted content actually exists in source text

### Segmentation Patterns

**Chinese sentence detection**:
```python
SENTENCE_PATTERN = re.compile(r'[^。！？.!?]+[。！？.!?]\s*')
```

**Heading detection for semantic segmentation**:
```python
HEADING_PATTERNS = [
    r'^[一二三四五六七八九十]+、',  # Chinese numerals
    r'^\d+[\.\)]',                 # Arabic numerals
    r'^第[一二三四五六七八九十]+[章节部分]',  # Chapter markers
    r'^#+\s',                      # Markdown headings
]
```

## Risks / Trade-offs

### Risk 1: AI Extraction Accuracy
**Risk**: AI may not consistently extract the correct content for each field

**Mitigation**:
- Provide clear, structured prompts with field definitions
- Include examples in prompts for few-shot learning
- Add validation to detect empty/malformed responses
- Allow users to refine templates for better results

**Trade-off**: More detailed prompts increase token usage and cost

### Risk 2: Sentence Segmentation Accuracy
**Risk**: Regex-based sentence splitting may fail on edge cases (abbreviations, decimals)

**Mitigation**:
- Focus on Chinese text (simpler punctuation rules)
- Test on common document patterns
- Provide semantic segmentation as more accurate alternative
- Document known limitations

**Trade-off**: Rule-based is less accurate than NLP libraries but faster and dependency-free

### Risk 3: Template Key Collisions in Cache
**Risk**: Different templates with same field names could cause cache collisions

**Mitigation**:
- Include template identifier in cache key
- Sort field names alphabetically for consistent keys
- Use hash of template list for cache key

**Trade-off**: More complex cache keys vs potential cache misses

### Risk 4: AI Response Parsing Failures
**Risk**: AI may return malformed JSON or unexpected format

**Mitigation**:
- Add robust JSON parsing with error handling
- Provide fallback to original text if parsing fails
- Log parsing failures for prompt refinement
- Use structured output mode if available in API

**Trade-off**: More error handling code vs reliability

### Risk 5: Performance on Large Documents
**Risk**: Processing very long documents (10000+ characters) may be slow or exceed limits

**Mitigation**:
- Enforce `max_text_length` limit (existing: 1000 chars)
- Recommend chunking for large documents
- Provide batch processing capability
- Document size limits in API

**Trade-off**: Smaller limits vs failed extractions on large docs

## Migration Plan

### Phase 1: Implementation
1. Add template configuration to `AITextProcessor` class
2. Implement `extract_structure()` method with AI integration
3. Implement `segment_text()` method with rule-based patterns
4. Add unit tests for both methods
5. Update documentation

### Phase 2: Integration
1. Add optional view/endpoint in `views.py` for web access
2. Update existing `AIWordFormatter` to use new methods if beneficial
3. Add integration tests

### Phase 3: Enhancement (Future)
1. Add more predefined templates based on user feedback
2. Improve segmentation patterns with real-world testing
3. Add batch processing for multiple documents
4. Consider adding output format options (Markdown, JSON, XML)

### Rollback Plan
- All changes are additive (no modifications to existing methods)
- If issues arise, new methods can be deprecated without breaking existing functionality
- Git revert available for clean removal

## Open Questions

1. **Should we add a web UI for this feature?**
   - Current scope: API/methods only
   - Future consideration: Add to existing template if demand exists

2. **Should extraction support multiple languages?**
   - Current focus: Chinese text
   - Future: Add language detection and prompt customization

3. **Should we support saving/loading custom templates?**
   - Current approach: Define templates in code
   - Future: Database or file-based template storage if templates become complex

4. **What's the maximum number of fields in a template?**
   - Current decision: No limit, but AI prompt length constraints apply
   - Recommendation: Limit to 5-7 fields for best AI performance

5. **Should we add confidence scores for extraction?**
   - Current decision: Not included (AI doesn't provide this)
   - Future: Consider if AI model supports confidence/certainty metrics
