# Spec: AI Retry Logic

## ADDED Requirements

### Requirement: Automatic Retry on Transient Failures
The AITextProcessor SHALL automatically retry AI API calls when specific transient failures occur, with exponential backoff between attempts.

#### Scenario: Retry on null response
- **Given** AI processing is enabled
- **And** retry is enabled in settings (ZHIPU_RETRY_ENABLED = True)
- **And** retry count is set to 1 (ZHIPU_RETRY_COUNT = 1)
- **When** the AI API returns null or empty content
- **Then** the system SHALL log "Attempt 1/2 failed: AI returned empty content"
- **And** the system SHALL wait 1 second (exponential backoff)
- **And** the system SHALL make a second API call
- **And** if the second call succeeds, the system SHALL log "Retry attempt 1 succeeded"
- **And** the system SHALL return the successfully processed text

#### Scenario: Retry on timeout
- **Given** AI processing is enabled
- **And** retry is enabled in settings
- **And** the API call times out after 15 seconds
- **When** the timeout occurs
- **Then** the system SHALL log the timeout error
- **And** the system SHALL wait 1 second
- **And** the system SHALL make a second API call
- **And** if the second call succeeds, return the processed text
- **And** if the second call also fails, fall back to original text

#### Scenario: Retry on connection error
- **Given** AI processing is enabled
- **And** retry is enabled in settings
- **When** a network connection error occurs (DNS failure, refused connection, etc.)
- **Then** the system SHALL detect this as a retryable error
- **And** the system SHALL wait 1 second
- **And** the system SHALL retry the API call
- **And** if successful, return the processed text

#### Scenario: No retry on authentication error
- **Given** AI processing is enabled
- **And** retry is enabled in settings
- **When** the API returns 401 Unauthorized or 403 Forbidden
- **Then** the system SHALL NOT retry
- **And** the system SHALL immediately raise an authentication error
- **And** the system SHALL log "Non-retryable error: Authentication failed"
- **And** the view SHALL return the original text to the user

#### Scenario: No retry on invalid request
- **Given** AI processing is enabled
- **And** retry is enabled in settings
- **When** the API returns 400 Bad Request (invalid parameters)
- **Then** the system SHALL NOT retry
- **And** the system SHALL immediately raise a validation error
- **And** the system SHALL log "Non-retryable error: Invalid request"
- **And** the view SHALL return the original text to the user

#### Scenario: Exponential backoff with multiple retries
- **Given** AI processing is enabled
- **And** retry count is set to 2 (ZHIPU_RETRY_COUNT = 2)
- **And** initial delay is 1.0 second (ZHIPU_RETRY_INITIAL_DELAY = 1.0)
- **When** the first two API attempts fail with retryable errors
- **Then** the system SHALL wait 1 second before retry attempt 1
- **And** the system SHALL wait 2 seconds before retry attempt 2
- **And** the delays SHALL follow exponential backoff: 1s, 2s, 4s, 8s...

#### Scenario: Retry disabled by settings
- **Given** AI processing is enabled
- **And** retry is disabled in settings (ZHIPU_RETRY_ENABLED = False)
- **When** the AI API returns null or times out
- **Then** the system SHALL NOT retry
- **And** the system SHALL immediately fall back to original text
- **And** the system SHALL log "AI API 调用（无重试）..."

### Requirement: Transparent Retry Progress Logging
The system SHALL log all retry attempts with clear status messages for debugging and monitoring.

#### Scenario: Log initial attempt
- **Given** AI processing is enabled
- **And** retry is enabled
- **When** the first API call is made
- **Then** the system SHALL log "AI API 调用尝试 1/2"
- **And** the log level SHALL be INFO

#### Scenario: Log retry attempt
- **Given** the first API attempt failed
- **And** retry is enabled
- **When** preparing to retry
- **Then** the system SHALL log "重试第 1/1 次（延迟 1s）..."
- **And** the log level SHALL be INFO
- **And** the log SHALL include the attempt number and delay

#### Scenario: Log retry success
- **Given** a retry attempt is made
- **When** the retry succeeds
- **Then** the system SHALL log "重试第 1 次成功"
- **And** the log level SHALL be INFO

#### Scenario: Log all attempts failed
- **Given** retry is enabled with 1 retry
- **When** both attempts fail
- **Then** the system SHALL log "全部 2 次尝试均失败"
- **And** the log level SHALL be ERROR
- **And** the system SHALL fall back to original text

### Requirement: User-Visible Retry Progress
The web interface SHALL display real-time retry progress to users during AI processing.

#### Scenario: Show attempt progress
- **Given** a user submits a document for AI processing
- **And** retry is enabled
- **When** AI processing begins
- **Then** the UI SHALL display "正在使用 AI 处理...（尝试 1/2）"
- **And** the message SHALL update to "正在使用 AI 处理...（尝试 2/2）" on retry
- **And** the message SHALL be styled as processing (blue background)

#### Scenario: Show retry success
- **Given** a retry attempt succeeded
- **When** the processed text is received
- **Then** the UI SHALL display "AI 处理完成"
- **And** the message SHALL be styled as success (green background)

#### Scenario: Show all retries failed
- **Given** all retry attempts failed
- **When** falling back to original text
- **Then** the UI SHALL display "AI 处理失败，使用原始文本"
- **And** the message SHALL be styled as warning (orange background)
- **And** the document SHALL still be formatted (just without AI enhancement)

#### Scenario: Status polling updates
- **Given** the form is submitted
- **When** the document is being processed
- **Then** the UI SHALL poll the server every 500ms for status updates
- **And** the status SHALL be stored in the user's session
- **And** polling SHALL stop after 30 seconds or when processing completes

### Requirement: Configurable Retry Settings
Administrators SHALL be able to configure retry behavior via Django settings without code changes.

#### Scenario: Configure retry count
- **Given** an administrator wants to change retry attempts
- **When** they set `ZHIPU_RETRY_COUNT = 2` in settings.py
- **Then** the system SHALL make up to 2 retries (3 total attempts)
- **And** the log SHALL show "重试次数：2"

#### Scenario: Configure initial delay
- **Given** an administrator wants to change backoff delay
- **When** they set `ZHIPU_RETRY_INITIAL_DELAY = 2.0` in settings.py
- **Then** the first retry SHALL wait 2 seconds
- **And** the second retry SHALL wait 4 seconds (exponential)
- **And** the log SHALL show "初始延迟：2s"

#### Scenario: Disable retry entirely
- **Given** an administrator wants to disable retry
- **When** they set `ZHIPU_RETRY_ENABLED = False` in settings.py
- **Then** the system SHALL not make any retry attempts
- **And** the log SHALL show "重试：禁用"
- **And** failures SHALL immediately fall back to original text

#### Scenario: Use defaults when settings missing
- **Given** settings.py does not contain retry configuration
- **When** AITextProcessor is initialized
- **Then** the system SHALL use default values:
  - ZHIPU_RETRY_ENABLED = True
  - ZHIPU_RETRY_COUNT = 1
  - ZHIPU_RETRY_INITIAL_DELAY = 1.0
- **And** the system SHALL log these defaults

#### Scenario: Validate retry settings
- **Given** an administrator sets invalid retry configuration
- **When** ZHIPU_RETRY_COUNT = -1 (negative value)
- **Then** the system SHALL treat it as 0 (no retry)
- **When** ZHIPU_RETRY_INITIAL_DELAY = 0 (zero delay)
- **Then** the system SHALL use a minimum of 0.1 seconds

### Requirement: Retry Behavior with Cache
The existing cache decorator SHALL work correctly with retry logic, avoiding redundant API calls.

#### Scenario: Cache hit prevents retry
- **Given** a text was processed successfully 10 seconds ago
- **And** the result is cached (30-second cache)
- **When** the same text is processed again
- **Then** the system SHALL return the cached result immediately
- **And** no API call SHALL be made
- **And** no retry SHALL be attempted
- **And** the log SHALL show "命中文本缓存，直接返回结果"

#### Scenario: Cache miss triggers retry
- **Given** a text is being processed for the first time
- **And** retry is enabled
- **When** the API returns null on first attempt
- **Then** the cache decorator SHALL NOT cache the null result
- **And** the system SHALL retry
- **And** if retry succeeds, the successful result SHALL be cached
- **And** subsequent calls SHALL return the cached success

#### Scenario: Retry does not bypass cache
- **Given** retry is enabled
- **And** a text is already cached
- **When** process_text is called with the cached text
- **Then** the cache SHALL be checked before any retry logic
- **And** if cache hits, return cached result without API call or retry

## MODIFIED Requirements

### Requirement: AITextProcessor Initialization
The AITextProcessor SHALL read retry configuration from Django settings during initialization.

#### Scenario: Initialize with retry settings
- **Given** Django settings contain:
  - ZHIPU_RETRY_ENABLED = True
  - ZHIPU_RETRY_COUNT = 1
  - ZHIPU_RETRY_INITIAL_DELAY = 1.0
- **When** AITextProcessor is initialized
- **Then** the instance SHALL store these values
- **And** the log SHALL show "AI 文本处理器初始化完成（...重试：启用，重试次数：1，初始延迟：1s...）"

#### Scenario: Initialize with defaults
- **Given** Django settings do NOT contain retry configuration
- **When** AITextProcessor is initialized
- **Then** the instance SHALL use default values
- **And** retry SHALL be enabled by default
- **And** retry count SHALL default to 1

### Requirement: AI Text Processing (Extended)
The existing process_text() method SHALL incorporate retry logic while maintaining backward compatibility.

#### Scenario: Backward compatibility maintained
- **Given** existing code calls process_text(raw_text) without knowing about retry
- **When** the method is called
- **Then** retry SHALL be applied automatically based on settings
- **And** the return value SHALL still be a string (never None)
- **And** errors SHALL still fall back to original text
- **And** no breaking changes SHALL occur to the API

## REMOVED Requirements
None - this is a pure enhancement with backward compatibility.
