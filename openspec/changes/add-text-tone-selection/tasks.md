# Tasks: Add Text Tone Selection

## Implementation Tasks

### 1. Backend: Extend AITextProcessor
**Priority**: High
**Effort**: Small
- [x] Add tone parameter to `AITextProcessor.__init__(self, tone='no_preference')`
- [x] Add `get_tone_prompt(tone)` method that returns tone-specific system prompts
- [x] Update `process_text(self, raw_text)` to use tone-specific prompts
- [x] Add tone validation with fallback to 'no_preference' on invalid input
- [ ] Add unit tests for each tone variant

### 2. View Layer: Pass Tone Parameter
**Priority**: High
**Effort**: Small
- [x] Update `ai_format_word()` view to extract `tone` from POST data
- [x] Pass `tone` parameter to `AIWordFormatter` constructor
- [x] Pass `tone` parameter to `AITextProcessor` constructor
- [x] Add logging for tone selection

### 3. Service Layer: Integrate Tone
**Priority**: High
**Effort**: Small
- [x] Update `AIWordFormatter.__init__()` to accept and store `tone` parameter
- [x] Pass `tone` to `AITextProcessor` when instantiating

### 4. Frontend: Add Tone Selector UI
**Priority**: High
**Effort**: Medium
- [x] Add tone dropdown/radio buttons below AI checkbox in `upload_word_ai.html`
- [x] Implement JavaScript to disable/enable tone selector based on AI checkbox state
- [x] Add visual feedback (tooltip) when tone selector is disabled
- [x] Style tone selector to match existing UI design

### 5. Testing & Validation
**Priority**: Medium
**Effort**: Medium
- [ ] Test each tone produces appropriate output style
- [ ] Test "No preference" maintains current behavior
- [ ] Test tone selector is disabled when AI is off
- [ ] Test invalid tone selection falls back gracefully
- [ ] Test with sample documents for each tone

## Dependencies & Ordering
1. Task 1 (Backend) must be completed before Task 2 (View)
2. Task 3 (Service) can be done in parallel with Task 2
3. Task 4 (Frontend) can be done independently but should wait for backend completion
4. Task 5 (Testing) depends on all previous tasks

## Parallelizable Work
- Tasks 1, 2, 3 can be done in parallel by different developers
- Task 4 (UI) can be mocked before backend is ready
- Task 5 (Testing) can have test cases written before implementation

## Validation Checklist
- [x] All 7 tones + "No preference" appear in UI
- [x] Tone selector is disabled when AI checkbox is unchecked
- [ ] Each tone demonstrates distinct writing style
- [ ] "No preference" output matches pre-change behavior
- [ ] No errors when processing with any tone
- [x] Logging shows tone selection for debugging
