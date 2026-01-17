# Spec: Performance Optimization

## ADDED Requirements

### Requirement: Eliminate Duplicate Imports

All Python files MUST NOT contain duplicate imports of the same module.

#### Scenario: Import inspection
**Given** any Python file in the project
**When** analyzing imports with a linter tool
**Then** zero duplicate imports are found
**And** each module is imported only once

#### Scenario: views.py imports
**Given** the file `format_specifications/views.py`
**When** reviewing the import section
**Then** `datetime` is imported only once at the top of the file
**And** no duplicate imports exist within the file

---

### Requirement: Remove Unused Imports

All Python files MUST NOT contain unused imports.

#### Scenario: Static analysis check
**Given** any Python file in the project
**When** running `autoflake` or `pyflakes`
**Then** zero unused imports are reported
**And** all imported modules/functions are actually used in the code

#### Scenario: Import cleanup after refactoring
**Given** a developer removes code that was using a specific import
**When** they run the linter
**Then** the linter flags the now-unused import
**And** the developer removes it

---

### Requirement: AI Client Connection Pooling

The `AITextProcessor` class MUST reuse HTTP connections to the ZhipuAI API across multiple instances.

#### Scenario: Multiple AI requests in single request
**Given** a user uploads a document requiring 10 AI API calls
**When** the `AITextProcessor` processes the document
**Then** HTTP connections are reused across all 10 calls
**And** no more than 2 TCP connections are established to the API

#### Scenario: Shared client across instances
**Given** multiple `AITextProcessor` instances are created
**When** they make API calls
**Then** they share the same underlying HTTP client
**And** connection pooling is utilized

---

### Requirement: Document Analysis Caching

The `AIWordFormatter` class MUST cache document analysis results to avoid redundant processing.

#### Scenario: Single document processed once
**Given** a document is uploaded for formatting
**When** `AIWordFormatter` analyzes the document
**Then** the analysis result is cached
**And** subsequent calls to `analyze_document()` return the cached result

#### Scenario: Cache invalidation on new document
**Given** a new `AIWordFormatter` instance is created with a different file
**When** the document is analyzed
**Then** a new cache entry is created
**And** previous cache entries are not affected

---

### Requirement: Batch AI API Requests

The AI text processor MUST support batching multiple text processing requests in a single API call when possible.

#### Scenario: Template-based generation with multiple sections
**Given** a template has 7 sections to generate
**When** the document is small enough for batch processing
**Then** all sections are processed in a single AI API call
**And** only 1 HTTP request is made instead of 7

#### Scenario: Large document falls back to sequential processing
**Given** a document is too large for batch processing
**When** the document is processed
**Then** it falls back to sequential processing (one section per call)
**And** a log message indicates the mode used

---

### Requirement: Optimize Session Storage

Session storage MUST be optimized to prevent database bloat and improve performance.

#### Scenario: Session log buffer management
**Given** a long-running document processing operation
**When** log entries are added to the session
**Then** the log buffer is capped at 50 entries
**And** old entries are automatically removed (FIFO)

#### Scenario: Session cleanup after completion
**Given** a document processing operation completes
**When** the session is no longer needed
**Then** session data is cleared or expires
**And** database storage is freed

---

## MODIFIED Requirements

### Requirement: AI API Timeout Configuration

**MODIFIED**: AI API timeout MUST be configurable per request type with sensible defaults. The system uses shorter timeouts (10s) for quick text polishing operations and longer timeouts (30s) for full content generation, instead of a fixed 15-second timeout for all operations.

#### Scenario: Quick text polishing
**Given** a short text (<100 chars) is being polished
**When** the AI API call is made
**Then** a shorter timeout (e.g., 10 seconds) is used
**And** the API responds quickly or fails fast

#### Scenario: Long content generation
**Given** a full document template is being generated
**When** the AI API call is made
**Then** a longer timeout (e.g., 30 seconds) is used
**And** the API has time to generate the full response

---

### Requirement: Caching TTL Strategy

**MODIFIED**: AI response cache MUST use content-based cache keys with a 5-minute TTL instead of the current 30-second fixed TTL. The cache key includes template name, source text hash, and tone parameter to allow cache reuse across different requests with identical content.

#### Scenario: Identical content requested twice
**Given** the same template and source text are processed
**When** the second request is made within 5 minutes
**Then** the cached response is returned
**And** no AI API call is made

#### Scenario: Different content cache miss
**Given** a different source text is provided
**When** the request is made
**Then** a cache miss occurs
**And** a new AI API call is made

---

## REMOVED Requirements

None - All existing functionality is preserved, only optimized.

---

## Cross-References

- **Related**: [Code Organization Spec](../code-organization/spec.md) - Removing unused imports is part of cleanup
- **Related**: [Developer Tooling](../developer-tooling/spec.md) - Linting enforces import requirements

---

## Implementation Notes

### Duplicate Import Detection

Use automated tools to detect duplicates:

```bash
# Option 1: Using ruff
ruff check format_specifications/ --select F401

# Option 2: Using pyflakes
pyflakes format_specifications/

# Option 3: Using autoflake (auto-fix)
autoflake --remove-all-unused-imports --in-place format_specifications/**/*.py
```

### Connection Pooling Implementation

**Current Code** (`ai_word_utils.py`):
```python
class AITextProcessor:
    def __init__(self, tone='no_preference', log_callback=None):
        self.client = ZhipuAI(api_key=self.api_key)
```

**Optimized Code**:
```python
class AITextProcessor:
    _shared_client = None

    def __init__(self, tone='no_preference', log_callback=None):
        if AITextProcessor._shared_client is None:
            AITextProcessor._shared_client = ZhipuAI(
                api_key=settings.ZHIPU_API_KEY
            )
        self.client = AITextProcessor._shared_client
```

### Document Analysis Caching

**Current Code** (`word_formatter.py`):
```python
class AIWordFormatter:
    def analyze_document(self):
        word_count = 0
        # ... expensive analysis ...
        return stats
```

**Optimized Code**:
```python
class AIWordFormatter:
    def __init__(self, input_file_path, ...):
        # ... existing init ...
        self._analysis_cache = None

    def analyze_document(self):
        if self._analysis_cache is None:
            self._analysis_cache = self._perform_analysis()
        return self._analysis_cache

    def _perform_analysis(self):
        word_count = 0
        # ... expensive analysis ...
        return stats
```

### Batch Processing Threshold

**Current Batch Threshold**: 500 characters

**Optimization**: Make threshold configurable and document trade-offs:

```python
BATCH_MODE_THRESHOLD = 500  # chars
SEQUENTIAL_MODE_THRESHOLD = 5000  # chars

if len(source_text) < BATCH_MODE_THRESHOLD:
    mode = "batch"
elif len(source_text) < SEQUENTIAL_MODE_THRESHOLD:
    mode = "sequential"
else:
    mode = "chunked"  # NEW: split and process in chunks
```

---

## Performance Targets

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| AI API latency | 3-5s | 2-3s | 20-40% improvement |
| Document processing | 10-15s | 8-12s | 20% improvement |
| Import time (views.py) | Unknown | <100ms | 50% improvement |
| Duplicate imports | 2+ | 0 | Zero tolerance |
| Unused imports | Unknown | 0 | Zero tolerance |

---

## Testing Strategy

### Performance Tests

Create benchmarks to verify improvements:

```python
# tests/performance/test_ai_performance.py
import time
from format_specifications.utils.ai_word_utils import AITextProcessor

def test_ai_api_latency():
    """Measure AI API call latency"""
    processor = AITextProcessor()
    start = time.time()
    result = processor.process_text("Test text")
    elapsed = time.time() - start
    assert elapsed < 5.0, f"API call took {elapsed}s, expected <5s"

def test_connection_reuse():
    """Verify HTTP connection reuse"""
    # Check that multiple calls don't create new connections
    pass
```

### Regression Tests

Ensure optimizations don't break functionality:

```python
# tests/regression/test_import_cleanup.py
def test_views_imports():
    """Verify views.py has no duplicate imports"""
    import format_specifications.views as views
    imports = []
    # Parse and check imports
    assert len(imports) == len(set(imports)), "Duplicate imports found"
```

---

## Rollback Plan

If performance optimizations cause issues:

1. **Revert connection pooling**: Remove `_shared_client` logic
2. **Revert caching**: Remove `_analysis_cache` logic
3. **Restore old timeout values**: Change back to fixed 15s timeout
4. **Disable batch processing**: Always use sequential mode

Each optimization can be independently reverted via feature flags or simple code changes.
