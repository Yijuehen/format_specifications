# Tasks: Cleanup and Optimize Codebase

## Phase 1: File Organization and Quick Wins

### 1.1 Create proper test directory structure
- [x] Create `tests/` directory with subdirectories: `unit/`, `integration/`, `e2e/`
- [x] Move `test_segmentation.py` → `tests/unit/test_segmentation.py`
- [x] Move `test_templates.py` → `tests/unit/test_templates.py`
- [x] Move `test_ai_generation.py` → `tests/integration/test_ai_generation.py`
- [x] Move `test_ai_generation_simple.py` → `tests/integration/test_ai_generation_simple.py`
- [x] Move `test_homepage_integration.py` → `tests/integration/test_homepage.py`
- [x] Move `test_segmentation_e2e.py` → `tests/e2e/test_segmentation_e2e.py`
- [x] Move `test_web_interface.py` → `tests/e2e/test_web_interface.py`
- [x] Move `verify_implementation.py` → `tests/integration/verify_implementation.py`
- [x] Move `verify_simple.py` → `tests/integration/verify_simple.py`

### 1.2 Clean up root directory
- [x] Move test documents to `tests/fixtures/`:
  - [x] Move `test_custom_structure.docx` → `tests/fixtures/`
  - [x] Move `test_small.docx` → `tests/fixtures/`
  - [x] Move `test_small_doc.txt` → `tests/fixtures/`
- [ ] Archive or delete `PHASE_0_COMPLETE.md`
- [x] Confirm `picture_test.py` can be deleted (already staged for deletion)

### 1.3 Update .gitignore
- [x] Add `tmpclaude-*` pattern to `.gitignore`
- [x] Add `tests/__pycache__/` to `.gitignore` (already covered by `__pycache__/`)
- [x] Add `*.pyc` to `.gitignore` (if not already present) (already covered by `*.py[cod]`)
- [x] Add `.pytest_cache/` to `.gitignore`
- [x] Add `coverage.xml` and `.coverage` to `.gitignore`

### 1.4 Update test imports
- [x] Update all import statements in moved test files
- [x] Update `manage.py` test commands if needed (no changes needed)
- [ ] Verify all tests still run from new locations

---

## Phase 2: Code Cleanup

### 2.1 Remove duplicate imports in views.py
- [x] Remove duplicate `from datetime import datetime` at line 30
- [x] Consolidate all datetime imports to top of file
- [x] Verify datetime usage still works

### 2.2 Scan for unused imports across all files
- [ ] Run `autoflake` or `pyflakes` on all Python files
- [ ] Remove unused imports from:
  - [ ] `format_specifications/views.py` (1,166 lines)
  - [ ] `format_specifications/utils/ai_word_utils.py` (1,111 lines)
  - [ ] `format_specifications/utils/word_formatter.py` (535 lines)
  - [ ] `format_specifications/services/template_manager.py` (333 lines)
  - [ ] `format_specifications/utils/document_extractor.py` (223 lines)
- [ ] Document any imports that appear unused but are actually used for side effects

### 2.3 Remove dead code
- [ ] Identify unreachable code branches
- [ ] Remove commented-out code blocks
- [ ] Remove unused helper functions
- [ ] Remove unused class methods

### 2.4 Add type hints (optional, quality improvement)
- [ ] Add type hints to `views.py` public functions
- [ ] Add type hints to `ai_word_utils.py` core methods
- [ ] Add type hints to `word_formatter.py` public methods

---

## Phase 3: Performance Optimization

### 3.1 Database optimization
- [ ] Analyze SQLite usage patterns
- [ ] Add indexes to commonly queried fields (if any tables exist)
- [ ] Optimize session storage:
  - [ ] Review session data size (logs capped at 50 entries ✓)
  - [ ] Consider session compression for large data
  - [ ] Document session cleanup strategy
- [ ] Add database connection pooling configuration (for future PostgreSQL migration)

### 3.2 AI API optimization
- [ ] Profile AI API call performance
- [ ] Implement request batching for `generate_from_template_batch()`
- [ ] Add connection pooling for ZhipuAI client
- [ ] Optimize timeout and retry logic:
  - [ ] Review current timeout (15s)
  - [ ] Review retry count and backoff strategy
  - [ ] Add circuit breaker for API failures

### 3.3 Caching optimization
- [ ] Review AI text cache (30-second TTL in `ai_word_utils.py`)
- [ ] Add template result caching
- [ ] Implement request-level caching for expensive operations
- [ ] Add cache invalidation strategy

### 3.4 Document processing optimization
- [ ] Profile `AIWordFormatter.format()` method
- [ ] Optimize image processing pipeline
- [ ] Reduce unnecessary document re-parsing
- [ ] Batch similar operations

---

## Phase 4: Developer Tooling

### 4.1 Pre-commit hooks setup
- [ ] Install `pre-commit` framework
- [ ] Add `trailing-whitespace` hook
- [ ] Add `end-of-file-fixer` hook
- [ ] Add `check-yaml` hook
- [ ] Add `check-added-large-files` hook
- [ ] Add `isort` hook for import sorting
- [ ] Add `black` or `ruff` hook for code formatting

### 4.2 Linting configuration
- [ ] Choose between `ruff` (fast) or `black` + `flake8` (traditional)
- [ ] Create `pyproject.toml` configuration:
  - [ ] Configure `isort` settings
  - [ ] Configure `ruff` or `black` settings
  - [ ] Configure line length (e.g., 100 or 120 characters)
- [ ] Add `ruff.toml` or `setup.cfg` if needed

### 4.3 CI/CD integration
- [ ] Add GitHub Actions workflow or similar
- [ ] Run linting on every PR
- [ ] Run tests on every PR
- [ ] Add coverage reporting (optional)

### 4.4 Documentation
- [ ] Document pre-commit hook installation in README
- [ ] Document how to run tests
- [ ] Document code style standards
- [ ] Add CONTRIBUTING.md with development setup

---

## Validation and Testing

### Test after each phase
- [ ] Phase 1 complete: Verify all tests pass from new locations
- [ ] Phase 2 complete: Verify no import errors, all tests pass
- [ ] Phase 3 complete: Benchmark performance improvements
- [ ] Phase 4 complete: Verify pre-commit hooks work correctly

### End-to-end validation
- [ ] Run full test suite: `python manage.py test`
- [ ] Manual testing: Upload and process documents via web interface
- [ ] Performance testing: Measure AI API response time before/after
- [ ] Code quality check: Run linter on entire codebase

---

## Rollback Plan

If issues arise:
- [ ] Git revert individual phase commits
- [ ] Restore files from backup if needed
- [ ] Document what went wrong for future reference

---

## Dependencies and Blocking

- **Blocked by**: None (can start immediately)
- **Blocks**: New feature development (should complete before major features)
- **Requires**: Python environment, test database, git access
