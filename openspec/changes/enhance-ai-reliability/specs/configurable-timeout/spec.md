# Spec: Configurable Timeout

## ADDED Requirements

### Requirement: Configurable API Timeout
The Zhipu AI API timeout SHALL be configurable via Django settings, allowing administrators to adjust timeout values per deployment environment.

#### Scenario: Configure custom timeout
- **Given** an administrator needs a longer timeout for slow networks
- **When** they set `ZHIPU_TIMEOUT = 30` in settings.py
- **Then** the AI API calls SHALL timeout after 30 seconds
- **And** the initialization log SHALL show "超时：30s"

#### Scenario: Use default timeout when not configured
- **Given** settings.py does NOT contain ZHIPU_TIMEOUT
- **When** AITextProcessor is initialized
- **Then** the system SHALL use the default timeout of 15 seconds
- **And** the initialization log SHALL show "超时：15s"
- **And** behavior SHALL match the pre-change implementation

#### Scenario: Configure short timeout for fast-fail
- **Given** an administrator wants fast failure for better UX
- **When** they set `ZHIPU_TIMEOUT = 10` in settings.py
- **Then** the AI API calls SHALL timeout after 10 seconds
- **And** timeout errors SHALL trigger retry if enabled
- **And** the system SHALL fall back to original text after all retries

#### Scenario: Validate timeout setting
- **Given** an administrator sets an invalid timeout
- **When** ZHIPU_TIMEOUT = 0 (zero)
- **Then** the system SHALL use a minimum of 5 seconds
- **When** ZHIPU_TIMEOUT = -1 (negative)
- **Then** the system SHALL use the default of 15 seconds
- **When** ZHIPU_TIMEOUT = 300 (excessively long, 5 minutes)
- **Then** the system SHALL use a maximum of 60 seconds
- **And** the log SHALL show a warning about the adjustment

### Requirement: Timeout Triggers Retry
When an API call times out, the timeout exception SHALL be treated as a retryable error, triggering the retry logic if enabled.

#### Scenario: Timeout with retry enabled
- **Given** retry is enabled (ZHIPU_RETRY_ENABLED = True)
- **And** timeout is set to 15 seconds
- **When** the API call times out after 15 seconds
- **Then** the system SHALL log "Attempt 1/2 failed: Request timeout"
- **And** the system SHALL wait 1 second (backoff delay)
- **And** the system SHALL make a second API call
- **And** if the second call succeeds within 15 seconds, return the result

#### Scenario: Timeout with retry disabled
- **Given** retry is disabled (ZHIPU_RETRY_ENABLED = False)
- **And** timeout is set to 15 seconds
- **When** the API call times out after 15 seconds
- **Then** the system SHALL NOT retry
- **And** the system SHALL immediately fall back to original text
- **And** the log SHALL show "AI 接口请求超时（超过 15 秒），返回原始文本"

#### Scenario: Timeout with extended timeout setting
- **Given** retry is enabled
- **And** timeout is set to 30 seconds (ZHIPU_TIMEOUT = 30)
- **When** the first API attempt times out after 30 seconds
- **Then** the system SHALL log "Attempt 1/2 failed: Request timeout"
- **And** the system SHALL retry
- **And** the second attempt SHALL also have a 30-second timeout
- **And** the total maximum wait time SHALL be 60 seconds (30s + 1s backoff + 30s retry)

#### Scenario: Timeout is logged with configured value
- **Given** timeout is configured as 20 seconds
- **When** a timeout occurs
- **Then** the error log SHALL include the configured timeout value
- **And** the log SHALL show "AI 接口请求超时（超过 20 秒）"

### Requirement: Timeout Configuration Documentation
The timeout setting SHALL be documented with recommended values for different deployment scenarios.

#### Scenario: Documentation for slow networks
- **Given** a deployment environment has slow network connectivity
- **When** an administrator reads the documentation
- **Then** they SHALL find recommended timeout of 30 seconds
- **And** the documentation SHALL explain this accommodates high latency

#### Scenario: Documentation for fast networks
- **Given** a deployment environment has fast network connectivity
- **When** an administrator reads the documentation
- **Then** they SHALL find recommended timeout of 10 seconds
- **And** the documentation SHALL explain this provides faster feedback

#### Scenario: Documentation for default value
- **Given** an administrator uses default settings
- **When** they read the documentation
- **Then** they SHALL find the default timeout is 15 seconds
- **And** the documentation SHALL explain this balances speed and reliability

### Requirement: Timeout Per-Request
The timeout setting SHALL apply to each individual API request, not the overall processing time.

#### Scenario: Each retry has independent timeout
- **Given** timeout is set to 15 seconds
- **And** retry is enabled with 1 retry
- **When** the first request times out after 15 seconds
- **And** the system retries after 1 second
- **Then** the retry request SHALL have a fresh 15-second timeout
- **And** the total processing time could be up to 31 seconds (15 + 1 + 15)

#### Scenario: Timeout does not include backoff delay
- **Given** timeout is set to 15 seconds
- **And** the system waits 1 second for backoff
- **When** the retry request is made
- **Then** the 1-second backoff delay SHALL NOT count toward the timeout
- **And** the API request SHALL have the full 15-second timeout

## MODIFIED Requirements

### Requirement: AITextProcessor Initialization (Extended)
The AITextProcessor initialization SHALL read the timeout configuration from Django settings.

#### Scenario: Read timeout from settings
- **Given** settings.py contains `ZHIPU_TIMEOUT = 20`
- **When** AITextProcessor() is instantiated
- **Then** self.request_timeout SHALL be set to 20
- **And** all API calls SHALL use this timeout value
- **And** the initialization log SHALL include "超时：20s"

#### Scenario: Backward compatible timeout
- **Given** settings.py does NOT contain ZHIPU_TIMEOUT
- **When** AITextProcessor() is instantiated
- **Then** self.request_timeout SHALL default to 15 seconds
- **And** behavior SHALL match pre-change implementation exactly
- **And** the log SHALL show "超时：15s"

### Requirement: API Request Execution (Extended)
The API request execution SHALL use the configured timeout value instead of a hardcoded 15 seconds.

#### Scenario: API call uses configured timeout
- **Given** timeout is configured as 25 seconds
- **When** client.chat.completions.create() is called
- **Then** the timeout parameter SHALL be set to 25
- **And** the request SHALL wait up to 25 seconds before timing out

#### Scenario: Timeout parameter passed to ZhipuAI SDK
- **Given** request_timeout is set to 18
- **When** making the API call
- **Then** the call SHALL include `timeout=self.request_timeout`
- **And** the ZhipuAI SDK SHALL enforce this timeout

## REMOVED Requirements
None - this is a pure enhancement with backward compatibility.
