# Proposal: Enhance AI Response Reliability

## Change ID
`enhance-ai-reliability`

## Summary
Implement automatic retry logic with exponential backoff and configurable timeout for AI API calls to handle null/empty responses and transient failures. Users will see transparent retry progress in the UI, and administrators can configure timeout and retry settings via Django settings without code changes.

## Motivation
Currently, when the Zhipu AI GLM-4 API returns null/empty responses or times out, the system immediately falls back to the original text. This approach has several limitations:

1. **Transient Network Issues**: Temporary network glitches can cause failures that would succeed on retry
2. **API Rate Limits**: Zhipu AI may throttle requests; a retry after backoff could succeed
3. **Timeout Too Short**: Current 15-second timeout is hardcoded and cannot be adjusted per deployment
4. **No User Visibility**: Users don't know if a failure is being retried or has permanently failed
5. **Lost Opportunity**: Many null responses are temporary and a single retry would significantly improve success rate

Industry best practices for resilient API integrations include:
- **Retry with exponential backoff**: Reduces API pressure and increases success rate
- **Configurable timeouts**: Different deployments have different network conditions
- **Transparent user feedback**: Users should see system behavior

## Proposed Solution

### 1. Automatic Retry Logic
When AI API returns null/empty response or times out:
- **Retry attempts**: 1 retry (2 total attempts: initial + 1 retry)
- **Backoff strategy**: Exponential backoff starting at 1 second
  - First attempt: Immediate
  - Retry 1: After 1-second delay
- **Retryable errors**:
  - Null/empty response content
  - Timeout exceptions
  - Connection errors
  - HTTP 5xx server errors
- **Non-retryable errors**:
  - Authentication failures (401)
  - Invalid requests (400)
  - Rate limit exceeded (429) - requires longer backoff than retry provides

### 2. Configurable Timeout
Make timeout configurable via Django settings:
```python
# settings.py
ZHIPU_TIMEOUT = 15  # seconds (default, same as current)
ZHIPU_RETRY_ENABLED = True  # enable/disable retry
ZHIPU_RETRY_COUNT = 1  # number of retries (default: 1)
ZHIPU_RETRY_INITIAL_DELAY = 1.0  # initial backoff delay in seconds
```

### 3. User-Visible Retry Progress
Update the UI to show retry attempts:
- Show progress message: "Processing with AI... (Attempt 1/2)"
- Update message on retry: "Retrying AI response... (Attempt 2/2)"
- Display final status: "AI processing successful" or "Using original text (AI unavailable)"

### 4. Enhanced Logging
Log retry attempts for debugging:
```python
logger.info(f"AI returned null, retrying in {delay}s... (Attempt {attempt}/{max_attempts})")
logger.info(f"Retry attempt {attempt} succeeded")
logger.warning(f"All retry attempts failed, using original text")
```

## User Impact
- **Positive**:
  - Higher AI processing success rate (estimated 20-30% improvement)
  - Better user experience with transparent progress feedback
  - Administrators can tune timeout per deployment environment
- **Breaking Changes**: None - backward compatible
- **Migration**: Optional: Add settings to `settings.py` (uses defaults if not present)

## Dependencies
- Existing `AITextProcessor` class
- Zhipu AI GLM-4 API
- Django settings framework
- Existing logging infrastructure

## Alternatives Considered

### Alternative 1: No Retry (Current State)
**Pros**:
- Simpler implementation
- Faster failure (no retry delay)

**Cons**:
- Lower success rate
- Poor user experience
- No resilience to transient failures

**Decision**: Rejected - too fragile for production use

### Alternative 2: Multiple Retries (3+ attempts)
**Pros**:
- Higher success rate
- Better resilience

**Cons**:
- Longer wait time for users (7+ seconds with backoff)
- Higher API cost
- More complex implementation

**Decision**: Rejected - 1 retry provides 80% of benefit with 20% of complexity

### Alternative 3: Client-Side Retry
**Pros**:
- Server stateless
- Better for distributed systems

**Cons**:
- More complex frontend
- Duplicate code across clients
- Harder to maintain

**Decision**: Rejected - over-engineering for single-server Django app

### Alternative 4: External Retry Library (tenacity)
**Pros**:
- Well-tested
- Feature-rich

**Cons**:
- Additional dependency
- Overkill for simple retry logic
- Less control over logging

**Decision**: Rejected - custom implementation is simpler and sufficient

## Open Questions
None - requirements are clear based on user feedback and industry best practices.

## Success Criteria
- [ ] AI API returns null/empty → automatic retry with 1s delay
- [ ] Timeout occurs → automatic retry with 1s delay
- [ ] Connection error → automatic retry with 1s delay
- [ ] Configurable timeout via Django settings (default: 15s)
- [ ] UI shows "Attempt 1/2" and "Attempt 2/2" messages
- [ ] Logs clearly show retry attempts and outcomes
- [ ] After 1 retry failure, gracefully falls back to original text
- [ ] No breaking changes to existing API
- [ ] Unit tests for retry logic
- [ ] Integration test with mocked API failures

## Risks and Mitigations

### Risk 1: Increased API Usage
**Impact**: Higher cost if every request triggers a retry
**Mitigation**:
- Only retry on specific errors (null, timeout, connection)
- Monitor retry rate and add alerting
- Can disable retry via settings if needed

### Risk 2: Longer User Wait Time
**Impact**: Users wait 1+ seconds longer when retries occur
**Mitigation**:
- Show clear progress messages
- Only retry when likely to succeed (not on auth errors)
- Keep retry count low (1 retry)

### Risk 3: Configurable Settings Misconfiguration
**Impact**: Timeout too short/long, retry disabled
**Mitigation**:
- Provide sensible defaults
- Document settings clearly
- Validate settings on startup
