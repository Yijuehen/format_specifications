# Proposal: Cleanup and Optimize Codebase

## Change ID
`cleanup-and-optimize-codebase`

## Status
**PROPOSED** - 2025-01-17

## Problem Statement

The codebase has accumulated technical debt across multiple dimensions:

1. **Temporary File Clutter**: 53+ `tmpclaude-*` files in project root
2. **Test File Disorganization**: 7+ test scripts in project root instead of proper test directory
3. **Code Duplication**: Multiple verification/implementation test files with overlapping functionality
4. **Import Inefficiency**: Redundant imports (e.g., `datetime` imported twice in views.py:11 and :30)
5. **Performance Issues**:
   - No database indexing on SQLite
   - Session data not optimized (log buffer grows unbounded in some paths)
   - AI API calls lack connection pooling
6. **Missing Code Quality Standards**: No automated cleanup or linting configuration

## User Impact

- **Developer Experience**: Difficult to navigate root directory with 50+ temp files
- **Testing**: No clear test structure, hard to find and run tests
- **Performance**: Unnecessary overhead in imports and database operations
- **Maintainability**: Dead code and unused imports accumulate over time

## Proposed Solution

### Phase 1: File Organization (Quick Wins)
1. **Create proper test directory structure**: Move `test_*.py`, `verify_*.py` to `tests/` or `tests/integration/`
2. **Consolidate duplicate test files**: Merge overlapping test functionality
3. **Add `.gitignore` entries**: Ensure temp files and test artifacts are ignored

### Phase 2: Code Cleanup
1. **Remove unused imports**: Auto-detect and remove unused imports across all Python files
2. **Fix duplicate imports**: Consolidate redundant imports (e.g., `datetime` in views.py)
3. **Remove dead code**: Identify and remove unreachable/dead code branches
4. **Add type hints**: Improve code documentation and IDE support

### Phase 3: Performance Optimization
1. **Database optimization**:
   - Add indexes to commonly queried fields
   - Optimize session storage (consider Redis for production)
   - Database query optimization (avoid N+1 queries)
2. **AI API optimization**:
   - Implement request batching where possible
   - Add connection pooling for ZhipuAI client
   - Optimize timeout and retry logic
3. **Caching strategy**:
   - Review and optimize AI text cache (currently 30-second TTL)
   - Add template result caching
   - Implement request-level caching for expensive operations

### Phase 4: Developer Tooling
1. **Add pre-commit hooks**: Auto-format code, remove unused imports, run linting
2. **Add linting configuration**: `ruff` or `black` + `isort` for consistent code style
3. **Add CI checks**: Ensure code quality on every PR

## Success Criteria

- [ ] Root directory contains only essential files (≤10 items)
- [ ] All test files organized under `tests/` directory
- [ ] Zero unused imports in production code
- [ ] Zero duplicate imports within files
- [ ] Database queries optimized (no N+1 queries)
- [ ] AI API response time improved by ≥20%
- [ ] Pre-commit hooks configured and documented
- [ ] All existing tests still pass after cleanup

## Alternatives Considered

### Option 1: Minimal Cleanup (REJECTED)
Only remove temp files, no code changes.
- **Pros**: Minimal risk, quick
- **Cons**: Doesn't address performance or maintainability issues

### Option 2: Full Rewrite (REJECTED)
Rewrite entire codebase with best practices.
- **Pros**: Clean slate, optimal architecture
- **Cons**: Too risky, time-consuming, may introduce new bugs

### Option 3: Phased Cleanup (SELECTED)
Incremental cleanup in phases, testing after each phase.
- **Pros**: Controlled risk, visible progress, easy to rollback
- **Cons**: Requires careful coordination

## Dependencies

- Requires testing environment to validate changes don't break functionality
- Should be done during a maintenance window, not before feature releases
- Coordinate with team to avoid conflicts with ongoing development

## Timeline Estimate

- **Phase 1**: 1-2 hours (file moves, gitignore)
- **Phase 2**: 2-3 hours (import cleanup, dead code removal)
- **Phase 3**: 4-6 hours (database, AI, caching optimization)
- **Phase 4**: 2-3 hours (tooling setup, documentation)

**Total**: 9-14 hours of work

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing functionality | Medium | High | Comprehensive testing after each phase |
| Performance regression | Low | Medium | Benchmark before/after optimization |
| Git history confusion | Low | Low | Use `git mv` for file moves to preserve history |
| Team disruption | Low | Medium | Schedule during low-activity periods |

## Related Changes

- None (this is a standalone cleanup effort)

## Open Questions

1. Should we keep the `picture_test.py` file (marked for deletion in git)?
2. What is the purpose of `PHASE_0_COMPLETE.md` - should it be archived or deleted?
3. Are any of the `tmpclaude-*` files actually needed for debugging?
