# Tasks: Remove AI Status Polling Remnants

## Overview
Remove remaining AI status polling code that references the deleted `/api/ai-status/` endpoint.

## Tasks

### 1. Remove AI Status Display HTML
**Priority**: High
**Effort**: 5 minutes

- [ ] Delete `<div id="ai-status" class="ai-status"></div>` (line ~210)
- [ ] Verify no other HTML elements reference `ai-status`

**Validation**:
- Grep for `id="ai-status"` - should return 0 results
- Grep for `ai-status` class references

---

### 2. Remove AI Status CSS
**Priority**: High
**Effort**: 5 minutes

- [ ] Delete `.ai-status` CSS class definition (lines ~103-125)
- [ ] Delete `.ai-status.processing` variant
- [ ] Delete `.ai-status.success` variant
- [ ] Delete `.ai-status.warning` variant

**Validation**:
- Grep for `\.ai-status` - should return 0 results
- Page should render without errors

---

### 3. Remove AI Status Polling JavaScript
**Priority**: High
**Effort**: 15 minutes

- [ ] Delete `checkAIProcessingStatus()` function (lines ~779-880)
- [ ] Remove `aiStatusPolling` object definition
- [ ] Remove form submit handler that calls AI status polling
- [ ] Remove any references to `window.aiStatusPolling`

**Validation**:
- Grep for `checkAIProcessingStatus` - should return 0 results
- Grep for `aiStatusPolling` - should return 0 results
- Grep for `/api/ai-status/` - should return 0 results

---

### 4. Remove AI Session Management (views.py)
**Priority**: Medium
**Effort**: 5 minutes

- [ ] Delete `request.session['ai_processing']` initialization
- [ ] Delete `request.session.save()` call
- [ ] Search for any other `ai_processing` session references

**Validation**:
- Grep for `ai_processing` in views.py - should return 0 results

---

### 5. Comprehensive Verification
**Priority**: High
**Effort**: 15 minutes

- [ ] Grep entire codebase for `ai-status` references
- [ ] Grep entire codebase for `aiStatusPolling` references
- [ ] Grep entire codebase for `/api/ai-status/` references
- [ ] Grep entire codebase for `ai_processing` session references
- [ ] Test form submission in browser
- [ ] Verify no 404 errors in console
- [ ] Verify AI processing still works
- [ ] Verify document download works

**Validation**:
- All greps return 0 results
- No console errors
- Form submission works
- Document processing completes successfully

---

## Dependencies

- Task 4 depends on Task 3 (backend cleanup after frontend)
- Task 5 depends on Tasks 1-4 (verification after all removals)

## Total Effort Estimate

- **Implementation**: 30 minutes
- **Verification**: 15 minutes
- **Total**: 45 minutes

## Rollback Plan

If issues arise:
1. Git revert the changes
2. All changes are deletions - easy to undo
3. No database migrations involved
