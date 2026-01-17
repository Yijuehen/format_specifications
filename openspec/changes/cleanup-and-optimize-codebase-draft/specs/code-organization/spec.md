# Spec: Code Organization

## ADDED Requirements

### Requirement: Organized Test Directory Structure

The project MUST organize all test files under a `tests/` directory with clear separation between unit, integration, and end-to-end tests.

#### Scenario: Developer runs unit tests
**Given** the project has an organized test structure
**When** the developer runs `python manage.py test tests/unit`
**Then** only unit tests are executed
**And** the test results show clear pass/fail status

#### Scenario: Developer runs integration tests
**Given** the project has an organized test structure
**When** the developer runs `python manage.py test tests/integration`
**Then** only integration tests are executed
**And** external dependencies (AI API, database) may be accessed

#### Scenario: Developer runs e2e tests
**Given** the project has an organized test structure
**When** the developer runs `python manage.py test tests/e2e`
**Then** only end-to-end tests are executed
**And** the full application stack is tested

---

### Requirement: Test Fixtures Directory

All test data files (documents, images, etc.) MUST be stored in `tests/fixtures/` directory.

#### Scenario: Test needs a sample document
**Given** a test requires a sample Word document
**When** the test accesses `tests/fixtures/test_small.docx`
**Then** the file is found and loaded successfully
**And** the test can use the file for testing

#### Scenario: New test fixture added
**Given** a developer creates a new test document
**When** they save it to `tests/fixtures/`
**Then** the file is automatically ignored by git if it matches `.gitignore` patterns
**And** other developers can access the fixture

---

### Requirement: Clean Root Directory

The project root directory MUST contain only essential files and directories (≤10 items).

#### Scenario: Developer clones repository
**Given** a new developer clones the repository
**When** they list the root directory contents
**Then** they see a clean, organized structure
**And** temporary files and test scripts are not in the root

#### Scenario: Navigate to source code
**Given** a developer wants to find the application code
**When** they look at the root directory
**Then** they see `format_specifications/` directory clearly
**And** they are not confused by test files mixed in

---

### Requirement: Comprehensive .gitignore

The project MUST have a `.gitignore` file that excludes temporary files, test artifacts, and Python cache files.

#### Scenario: Temporary files not committed
**Given** a developer creates temporary Claude files (`tmpclaude-*`)
**When** they run `git status`
**Then** these files are not listed as untracked
**And** they will not be accidentally committed

#### Scenario: Python cache files ignored
**Given** Python creates `__pycache__/` directories and `.pyc` files
**When** the developer runs `git status`
**Then** these cache files are not shown
**And** repository stays clean

---

## MODIFIED Requirements

### Requirement: Test Discovery

**MODIFIED**: Django's test runner MUST discover tests in the new `tests/` directory structure instead of root-level test files. The test discovery mechanism uses Django's default test runner which automatically finds test modules in `tests/` subdirectories following the `test_*.py` pattern.

#### Scenario: Run all tests
**Given** the project has tests in `tests/` directory
**When** the developer runs `python manage.py test`
**Then** all tests from `tests/unit/`, `tests/integration/`, and `tests/e2e/` are discovered
**And** all tests are executed
**And** a summary is shown

#### Scenario: Run specific test file
**Given** the project has tests in `tests/` directory
**When** the developer runs `python manage.py test tests.unit.test_templates`
**Then** only that specific test module is executed

---

## REMOVED Requirements

### Requirement: Root-Level Test Files (REMOVED)

**REMOVED**: Test files SHOULD NOT be in the project root directory.

**Rationale**: Test files in root directory clutter the project structure and make it harder to navigate. By moving tests to a dedicated `tests/` directory, the project becomes more organized and follows Python best practices.

#### Scenario: Old test file locations no longer work
**Given** a test file was previously in root directory (e.g., `test_templates.py`)
**When** the test file is moved to `tests/unit/test_templates.py`
**Then** imports and references to the old location are updated
**And** the test continues to work from the new location

---

## Cross-References

- **Related**: [Performance Optimization Spec](../performance-optimization/spec.md) - Optimizing imports affects performance
- **Related**: [Developer Tooling](../developer-tooling/spec.md) - Pre-commit hooks enforce organization

---

## Implementation Notes

### File Moves

Use `git mv` to preserve file history when moving tests:

```bash
git mv test_segmentation.py tests/unit/test_segmentation.py
git mv test_templates.py tests/unit/test_templates.py
git mv test_ai_generation.py tests/integration/test_ai_generation.py
# ... etc
```

### Import Updates

After moving files, update imports in test files:

**Before**:
```python
# In test_ai_generation.py
from format_specifications.utils.ai_word_utils import AITextProcessor
```

**After**:
```python
# In tests/integration/test_ai_generation.py
from format_specifications.utils.ai_word_utils import AITextProcessor
# No change needed if using absolute imports
```

### Django Test Discovery

Django's test runner will automatically discover tests in `tests/` directory if:

1. `tests/` directory has an `__init__.py` file
2. Test files follow the pattern `test_*.py`
3. Tests use Django's `TestCase` or `TransactionTestCase`

No configuration changes needed in `settings.py`.

---

## Migration Plan

1. Create `tests/` directory structure
2. Move test files using `git mv`
3. Update imports if needed
4. Run test suite to verify everything works
5. Update `.gitignore`
6. Commit changes
