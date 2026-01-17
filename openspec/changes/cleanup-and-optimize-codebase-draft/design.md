# Design: Cleanup and Optimize Codebase

## Overview

This document describes the architectural decisions and trade-offs for cleaning up and optimizing the codebase. The work is divided into four phases, each building on the previous one.

## Phase 1: File Organization

### Current State
```
Format_specifications/
├── test_segmentation.py
├── test_templates.py
├── test_ai_generation.py
├── test_ai_generation_simple.py
├── test_homepage_integration.py
├── test_segmentation_e2e.py
├── test_web_interface.py
├── verify_implementation.py
├── verify_simple.py
├── test_custom_structure.docx
├── test_small.docx
├── test_small_doc.txt
├── PHASE_0_COMPLETE.md
├── picture_test.py (deleted in git)
└── tmpclaude-* (53 files)
```

### Target State
```
Format_specifications/
├── tests/
│   ├── fixtures/
│   │   ├── test_custom_structure.docx
│   │   ├── test_small.docx
│   │   └── test_small_doc.txt
│   ├── unit/
│   │   ├── test_segmentation.py
│   │   └── test_templates.py
│   ├── integration/
│   │   ├── test_ai_generation.py
│   │   ├── test_ai_generation_simple.py
│   │   ├── test_homepage.py
│   │   ├── verify_implementation.py
│   │   └── verify_simple.py
│   └── e2e/
│       ├── test_segmentation_e2e.py
│       └── test_web_interface.py
├── docs/
│   └── PHASE_0_COMPLETE.md (archived)
└── .gitignore (updated)
```

### Trade-offs

**Option A: Flat test structure** (`tests/test_*.py`)
- **Pros**: Simpler, easier to find tests
- **Cons**: No separation of concerns, hard to run specific test types
- **Decision**: REJECTED - Organized structure is better for long-term maintenance

**Option B: Organized test structure** (`tests/{unit,integration,e2e}/`)
- **Pros**: Clear separation, easy to run specific test types, follows best practices
- **Cons**: More directories, slightly more complex
- **Decision**: SELECTED - Better for long-term maintainability

---

## Phase 2: Code Cleanup

### Duplicate Import Example

**Current Code** (`views.py`):
```python
# Line 11
from datetime import datetime

# ... 20 lines later ...

# Line 30 (inside function!)
from datetime import datetime  # DUPLICATE!
```

**Fixed Code**:
```python
# Line 11 (top of file)
from datetime import datetime

# ... inside function, use datetime directly without re-importing
```

### Dead Code Detection Strategy

1. **Static Analysis**: Use `autoflake`, `pyflakes`, or `ruff` to detect:
   - Unused imports
   - Unused variables
   - Unreachable code

2. **Dynamic Analysis**: Use `coverage.py` to detect:
   - Unexecuted code branches
   - Unused functions/methods

3. **Manual Review**: Identify:
   - Commented-out code blocks
   - Debug/development code left in production
   - Deprecated functions

---

## Phase 3: Performance Optimization

### 3.1 Database Optimization

**Current State**:
- SQLite database with no visible schema (migration `0001_initial.py` exists but not inspected)
- Session storage uses Django's default database-backed sessions
- No connection pooling (not needed for SQLite)

**Optimization Strategy**:

1. **If using database-backed sessions**:
   - Add index on `session_key` column
   - Add index on `expire_date` column
   - Implement periodic session cleanup

2. **Alternative: File-based sessions** (better for this use case):
   - Switch to `django.contrib.sessions.backends.file`
   - Store sessions in `media/sessions/`
   - No database overhead for sessions

3. **Future: Redis for production**:
   - Consider Redis for session storage
   - Faster than database
   - Built-in expiration (no cleanup needed)

### 3.2 AI API Optimization

**Current State** (`ai_word_utils.py`):
```python
class AITextProcessor:
    def __init__(self, tone='no_preference'):
        self.client = ZhipuAI(api_key=self.api_key)  # New client every instance!
```

**Problem**: New HTTP client created for every request, no connection pooling.

**Optimized Code**:
```python
class AITextProcessor:
    _client = None  # Class-level shared client

    def __init__(self, tone='no_preference'):
        if AITextProcessor._client is None:
            AITextProcessor._client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        self.client = AITextProcessor._client
```

**Benefits**:
- Connection pooling shared across instances
- Fewer TCP connections to ZhipuAI API
- Reduced latency for repeated API calls

**Alternative Process-Based**:
```python
# Use process-local storage (thread-safe)
from threading import local

_thread_local = local()

def get_ai_client():
    if not hasattr(_thread_local, 'ai_client'):
        _thread_local.ai_client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
    return _thread_local.ai_client
```

### 3.3 Caching Strategy

**Current State** (`ai_word_utils.py`):
```python
@lru_cache(maxsize=128)
def _build_prompt_template(template_name, source_text, user_outline, tone):
    # Cache key depends on all parameters
    # 30-second TTL for AI responses
```

**Optimization Strategy**:

1. **Template Pre-compilation**:
   - Pre-build prompt templates at startup
   - Cache compiled templates in memory
   - Reduce string concatenation overhead

2. **Response Caching**:
   - Current: 30-second TTL
   - **Issue**: Too short for repeated content
   - **Proposal**: Increase to 5 minutes or use content-based cache key
   - **Cache key**: `hash(template_name + source_text[:500] + tone)`

3. **Request-Level Caching**:
   - Cache document analysis results per request
   - Avoid re-analyzing same document multiple times

### 3.4 Document Processing Optimization

**Current Pipeline**:
```
Upload → Extract Text → Analyze → AI Process → Format → Save
```

**Bottlenecks**:
1. **Text Extraction**: Parses entire document multiple times
2. **AI Processing**: Sequential API calls, no batching
3. **Formatting**: Re-parses document for formatting

**Optimized Pipeline**:
```
Upload → Extract Text (once) → Analyze (cached) → AI Process (batched) → Format → Save
```

**Implementation**:
```python
class AIWordFormatter:
    def __init__(self, input_file_path):
        self.doc = Document(input_file_path)
        self._text_cache = None  # Cache extracted text
        self._analysis_cache = None  # Cache document analysis

    def _extract_text(self):
        """Extract text once, cache result"""
        if self._text_cache is None:
            self._text_cache = '\n'.join([p.text for p in self.doc.paragraphs])
        return self._text_cache

    def analyze_document(self):
        """Use cached text for analysis"""
        if self._analysis_cache is None:
            self._analysis_cache = self._analyze(self._extract_text())
        return self._analysis_cache
```

---

## Phase 4: Developer Tooling

### Pre-commit Hooks Configuration

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ['--profile', 'black']

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        args: ['--line-length=100']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: ['--fix']
```

### Linting Configuration

**`pyproject.toml`**:
```toml
[tool.black]
line-length = 100
target-version = ['py314']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N"]
ignore = ["E501"]  # Line length handled by black

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports in __init__.py
```

---

## Performance Benchmarks

### Before Optimization (Baseline)

| Metric | Current Value |
|--------|--------------|
| AI API call latency | ~3-5 seconds |
| Document processing time | ~10-15 seconds (small doc) |
| Import time (views.py) | Not measured |
| Test suite runtime | Not measured |

### Target Metrics (After Optimization)

| Metric | Target Value | Improvement |
|--------|-------------|-------------|
| AI API call latency | ~2-3 seconds | 20-40% faster |
| Document processing time | ~8-12 seconds | 20% faster |
| Import time (views.py) | <100ms | 50% faster |
| Test suite runtime | <30 seconds | Measurable baseline |

---

## Risk Analysis

### Risk 1: Breaking Changes During Refactoring
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**:
  - Run full test suite after each change
  - Use git branches for each phase
  - Keep detailed commit messages for easy rollback

### Risk 2: Performance Regression
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Benchmark before and after each optimization
  - Use profiling tools to identify actual bottlenecks
  - Test with real-world documents

### Risk 3: Tooling Compatibility Issues
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**:
  - Test pre-commit hooks on different OSes
  - Document tool versions in requirements.txt
  - Provide alternative setups if needed

---

## Success Metrics

1. **Code Quality**:
   - Zero unused imports (verified by `autoflake`)
   - Zero duplicate imports (manual review)
   - All tests passing after refactoring

2. **Performance**:
   - 20% reduction in AI API latency
   - 20% reduction in document processing time
   - Measurable improvement in import time

3. **Developer Experience**:
   - Root directory contains ≤10 files/directories
   - All tests organized under `tests/`
   - Pre-commit hooks installed and working
   - Documentation updated

4. **Maintainability**:
   - Code follows consistent style (black/ruff)
   - Type hints added to public APIs
   - Linting passes with zero errors

---

## Future Improvements (Out of Scope)

1. **Migration to PostgreSQL**:
   - Better for production than SQLite
   - Supports connection pooling
   - More robust concurrent access

2. **Async Task Queue**:
   - Use Celery or Django Q for background tasks
   - AI processing in background
   - Better user experience for long operations

3. **Dockerization**:
   - Containerize application
   - Easier deployment and scaling
   - Consistent development environment

4. **API Documentation**:
   - Add OpenAPI/Swagger documentation
   - Auto-generate from type hints
   - Better API discoverability
