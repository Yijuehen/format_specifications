# Tasks: Enhance AI Response Reliability

## Implementation Tasks

### 1. Settings Configuration
**Priority**: High
**Effort**: Small
- [x] Add ZHIPU_TIMEOUT setting to Django settings.py (default: 15)
- [x] Add ZHIPU_RETRY_ENABLED setting to Django settings.py (default: True)
- [x] Add ZHIPU_RETRY_COUNT setting to Django settings.py (default: 1)
- [x] Add ZHIPU_RETRY_INITIAL_DELAY setting to Django settings.py (default: 1.0)
- [x] Document all new settings with recommended values in comments
- [x] Test that missing settings use correct defaults

### 2. AITextProcessor: Configuration Reading
**Priority**: High
**Effort**: Small
- [x] Update `AITextProcessor.__init__()` to read ZHIPU_TIMEOUT from settings
- [x] Update `AITextProcessor.__init__()` to read ZHIPU_RETRY_ENABLED from settings
- [x] Update `AITextProcessor.__init__()` to read ZHIPU_RETRY_COUNT from settings
- [x] Update `AITextProcessor.__init__()` to read ZHIPU_RETRY_INITIAL_DELAY from settings
- [x] Add validation for timeout values (min: 5s, max: 60s, default: 15s)
- [x] Add validation for retry_count (min: 0, max: 5)
- [x] Add validation for retry_initial_delay (min: 0.1s, max: 10s)
- [x] Update initialization log to show retry configuration
- [x] Add helper method `_should_retry()` to check if retry is enabled

### 3. AITextProcessor: Extract Common Logic
**Priority**: High
**Effort**: Medium
- [x] Extract API call logic into `_make_ai_request(prompt)` method
- [x] Extract response validation into `_extract_and_validate_response(response)` method
- [x] Update `process_text()` to use extracted methods
- [x] Ensure all error handling is preserved
- [x] Test that extraction doesn't change behavior

### 4. AITextProcessor: Retry Logic
**Priority**: High
**Effort**: Medium
- [x] Implement `_call_ai_with_retry(prompt)` method with retry loop
- [x] Implement `_call_ai_once(prompt)` method for non-retry path
- [x] Add exponential backoff delay calculation: `delay * (2 ** (attempt - 1))`
- [x] Add retry attempt logging (attempt number, delay, success/failure)
- [x] Update `process_text()` to call `_call_ai_with_retry()` or `_call_ai_once()` based on settings
- [x] Ensure cache decorator works correctly with retry (cache on success only)
- [x] Add "all attempts failed" error logging

### 5. AITextProcessor: Retryable Error Detection
**Priority**: High
**Effort**: Medium
- [x] Identify retryable errors: ValueError (null), Timeout, ConnectionError
- [x] Identify non-retryable errors: HTTPError 401, 403, 400
- [x] Implement error type checking in retry loop
- [x] Ensure non-retryable errors raise immediately without retry
- [x] Add logging for "non-retryable error" cases
- [x] Test with each error type to verify correct behavior

### 6. View Layer: Session Management
**Priority**: Medium
**Effort**: Small
- [x] Update `ai_format_word()` to set session['ai_processing'] with initial status
- [x] Include retry configuration in session data (attempt, max_attempts)
- [x] Update session status on success (status: 'complete')
- [x] Update session status on error (status: 'failed', error message)
- [x] Ensure session data is cleared after processing

### 7. API Endpoint: Status Polling
**Priority**: Medium
**Effort**: Small
- [x] Create `ai_processing_status(request)` view function
- [x] Return JSON with status, attempt, max_attempts, error, timestamp
- [x] Add `@require_http_methods(["GET"])` decorator
- [x] Add URL pattern in urls.py: `path('api/ai-status/', ai_processing_status)`
- [x] Test endpoint returns valid JSON response

### 8. Frontend: Status Display Area
**Priority**: Medium
**Effort**: Small
- [x] Add `<div id="ai-status">` to upload_word_ai.html template
- [x] Add CSS styles for ai-status (processing, success, warning states)
- [x] Position status message above the form submit button
- [x] Ensure status div is hidden initially (display: none)
- [x] Test styling in different browser sizes (responsive)

### 9. Frontend: JavaScript Progress Polling
**Priority**: Medium
**Effort**: Medium
- [x] Implement `checkAIProcessingStatus()` JavaScript function
- [x] Add AJAX polling to `/api/ai-status/` endpoint
- [x] Update status message text based on response (attempt 1/2, success, failed)
- [x] Update status div styling based on state (blue/green/orange)
- [x] Start polling on form submit
- [x] Stop polling after 30 seconds or when status is complete/failed
- [x] Handle AJAX errors gracefully (network issues)
- [x] Test polling with actual form submission

### 10. Logging Enhancements
**Priority**: Medium
**Effort**: Small
- [x] Add "AI API 调用尝试 X/Y" log before each attempt
- [x] Add "重试第 X/Y 次（延迟 Zs）..." log before each retry
- [x] Add "重试第 X 次成功" log on retry success
- [x] Add "全部 X 次尝试均失败" log when all retries exhausted
- [x] Add "Non-retryable error" log for auth/validation errors
- [x] Ensure all logs use appropriate levels (INFO, WARNING, ERROR)
- [x] Test logging output with different failure scenarios

### 11. Unit Tests: Retry Logic
**Priority**: Medium
**Effort**: Medium
- [ ] Test `retry_on_null_response`: mock API returns null then success
- [ ] Test `retry_on_timeout`: mock API times out then succeeds
- [ ] Test `retry_on_connection_error`: mock connection error then success
- [ ] Test `no_retry_on_auth_error`: verify 401 doesn't trigger retry
- [ ] Test `no_retry_on_invalid_request`: verify 400 doesn't trigger retry
- [ ] Test `exponential_backoff`: verify delays (1s, 2s, 4s, 8s)
- [ ] Test `retry_disabled_by_settings`: verify no retry when disabled
- [ ] Test `cache_hit_prevents_retry`: verify cache is checked before retry
- [ ] Test `all_retries_fail`: verify fallback to original text
- [ ] Test `retry_settings_validation`: verify min/max bounds

### 12. Unit Tests: Configurable Timeout
**Priority**: Medium
**Effort**: Medium
- [ ] Test `configure_custom_timeout`: verify ZHIPU_TIMEOUT is used
- [ ] Test `use_default_timeout`: verify 15s default when not set
- [ ] Test `timeout_triggers_retry`: verify timeout is retryable
- [ ] Test `timeout_with_retry_disabled`: verify immediate fallback
- [ ] Test `timeout_validation`: verify min (5s) and max (60s) bounds
- [ ] Test `timeout_per_request`: verify each retry has independent timeout
- [ ] Test `timeout_in_logs`: verify timeout value appears in error messages

### 13. Integration Tests
**Priority**: Low
**Effort**: Medium
- [ ] Test `full_flow_with_retry`: complete document processing with mocked retry
- [ ] Test `ui_status_updates`: verify UI shows correct attempt numbers
- [ ] Test `session_status_endpoint`: verify API endpoint returns correct data
- [ ] Test `backward_compatibility`: verify existing code works without changes
- [ ] Test `settings_applied_correctly`: verify all settings are respected

### 14. Manual Testing
**Priority**: Medium
**Effort**: Medium
- [ ] Test with actual Zhipu AI API (monitor logs for retry behavior)
- [ ] Simulate network failure (disconnect network, reconnect during retry)
- [ ] Test with slow network (throttle connection to trigger timeout)
- [ ] Test UI feedback in different browsers (Chrome, Firefox, Safari)
- [ ] Test with various timeout settings (10s, 15s, 30s)
- [ ] Test with retry enabled vs disabled
- [ ] Test retry with different retry counts (0, 1, 2)
- [ ] Verify document formatting still works after retry failures

### 15. Documentation
**Priority**: Low
**Effort**: Small
- [ ] Update README.md with new settings documentation
- [ ] Add examples of timeout configuration for different environments
- [ ] Document retry behavior in API documentation
- [ ] Add troubleshooting section for common retry scenarios
- [ ] Document monitoring and alerting recommendations (retry rate tracking)

## Dependencies & Ordering

### Critical Path (Must be sequential):
1. **Task 1** (Settings) → **Task 2** (Read settings in AITextProcessor)
2. **Task 2** → **Task 3** (Extract logic)
3. **Task 3** → **Task 4** (Implement retry logic)
4. **Task 4** → **Task 5** (Error detection)
5. **Task 5** → **Task 11** (Unit tests for retry)
6. **Task 4** → **Task 6** (View layer integration)
7. **Task 6** → **Task 7** (Status endpoint)
8. **Task 7** → **Task 9** (Frontend polling)

### Parallelizable Work:
- **Tasks 11-12** (Unit tests) can be written alongside implementation
- **Task 8** (Frontend HTML/CSS) is independent of backend logic
- **Task 13** (Integration tests) depends on Tasks 1-9 but can run in parallel
- **Task 14** (Manual testing) depends on all implementation tasks
- **Task 15** (Documentation) can be written at any time

## Validation Checklist

### Code Completion:
- [ ] All new settings are defined with sensible defaults
- [ ] AITextProcessor reads and validates all settings correctly
- [ ] Retry logic implements exponential backoff (1s → 2s → 4s...)
- [ ] Only retryable errors trigger retry (null, timeout, connection)
- [ ] Non-retryable errors fail immediately (401, 400, 403)
- [ ] Cache decorator works correctly with retry (cache on success only)
- [ ] Session tracking stores and updates processing status
- [ ] API endpoint returns valid JSON status data
- [ ] UI displays attempt numbers (1/2, 2/2)
- [ ] UI shows final status (complete or failed)
- [ ] All retry attempts are logged with clear messages
- [ ] Timeout is configurable and applied to each API call

### Testing:
- [ ] Unit tests cover all retry scenarios (success, failure, disabled)
- [ ] Unit tests cover timeout configuration (custom, default, validation)
- [ ] Unit tests verify exponential backoff delays
- [ ] Unit tests verify cache behavior with retry
- [ ] Integration tests verify end-to-end flow
- [ ] Manual testing confirms retry works with real API
- [ ] UI feedback tested in multiple browsers

### Documentation:
- [ ] Settings documented in settings.py with comments
- [ ] README.md explains retry behavior
- [ ] Troubleshooting guide covers common issues
- [ ] Monitoring recommendations documented

### Backward Compatibility:
- [ ] Works without settings changes (uses defaults)
- [ ] Existing code calling process_text() works unchanged
- [ ] No breaking changes to API or behavior when retry disabled
- [ ] Pre-change timeout behavior maintained when ZHIPU_TIMEOUT not set

## Rollback Plan
If issues occur:
1. Disable retry by setting `ZHIPU_RETRY_ENABLED = False`
2. Revert to hardcoded timeout by removing ZHIPU_TIMEOUT setting
3. Disable UI status updates by removing JavaScript polling
4. Keep logging enhancements (they don't affect behavior)

No database changes or migrations required, so rollback is safe and instant.
