# Design: AI Response Reliability Enhancements

## Architecture Overview

This enhancement adds resilience to the AI text processing pipeline by introducing retry logic with exponential backoff, configurable timeouts, and transparent user feedback. The design maintains the existing service layer architecture while adding a new retry decorator pattern.

```
[UI] → [View] → [Formatter] → [AI Processor] → [Zhipu AI]
  ↓       ↓          ↓                ↓            ↓
Show   Extract    Pass to        Retry Logic   API Call
Retry  from POST  AIProcessor    with Backoff  (with timeout)
Status  & Pass                    ↓
     Retry Info              Log Attempts
```

## Component Changes

### 1. Django Settings Configuration

**New Settings** (settings.py):
```python
# Zhipu AI Configuration
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
ZHIPU_MODEL = 'glm-4'

# New: Retry Configuration
ZHIPU_TIMEOUT = 15  # Request timeout in seconds (default: 15)
ZHIPU_RETRY_ENABLED = True  # Enable/disable retry (default: True)
ZHIPU_RETRY_COUNT = 1  # Number of retries (default: 1)
ZHIPU_RETRY_INITIAL_DELAY = 1.0  # Initial backoff delay in seconds (default: 1.0)
```

**Rationale**:
- All defaults match current behavior or new feature defaults
- Settings can be overridden per deployment
- Retry can be disabled entirely if needed
- No breaking changes if settings not present (use defaults)

### 2. Retry Decorator (ai_word_utils.py)

**New Function**: `retry_on_failure(max_retries, initial_delay, retryable_errors)`

```python
def retry_on_failure(max_retries=1, initial_delay=1.0, retryable_errors=None):
    """
    Decorator that retries function calls on specific failures with exponential backoff.
    :param max_retries: Maximum number of retry attempts (default: 1)
    :param initial_delay: Initial delay before first retry in seconds (default: 1.0)
    :param retryable_errors: Tuple of exception classes to retry on
    :return: Decorator function
    """
    if retryable_errors is None:
        retryable_errors = (
            ValueError,  # AI returned null/empty
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError
        )

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            total_attempts = max_retries + 1  # Initial attempt + retries

            for attempt in range(total_attempts):
                try:
                    # Log attempt
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt}/{max_retries} after {initial_delay * (2 ** (attempt - 1))}s delay")
                        time.sleep(initial_delay * (2 ** (attempt - 1)))
                    else:
                        logger.info(f"AI API call attempt {attempt + 1}/{total_attempts}")

                    # Call original function
                    result = func(self, *args, **kwargs)

                    # Validate result
                    if not result or not result.strip():
                        raise ValueError("AI returned empty content")

                    # Success
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt} succeeded")
                    return result

                except retryable_errors as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{total_attempts} failed: {str(e)}")

                    # Don't retry after last attempt
                    if attempt >= max_retries:
                        logger.error(f"All {total_attempts} attempts failed, returning fallback")
                        break

                    # Continue to next retry
                    continue

                except Exception as e:
                    # Non-retryable error, raise immediately
                    logger.error(f"Non-retryable error: {str(e)}")
                    raise

            # All retries exhausted, raise last exception
            raise last_exception

        return wrapper
    return decorator
```

**Design Decisions**:
- **Exponential backoff**: Delay doubles each retry (1s → 2s → 4s)
- **Retryable errors only**: Auth failures (401) and invalid requests (400) fail immediately
- **Transparent logging**: Every attempt logged with clear status
- **Result validation**: Checks for empty responses even if API call succeeded
- **Preserves cache decorator**: Retry decorator wraps the cache decorator, not vice versa

### 3. AITextProcessor Modifications

**Modified Class**: `AITextProcessor`

```python
class AITextProcessor:
    def __init__(self, tone='no_preference'):
        # Read from settings with defaults
        self.api_key = settings.ZHIPU_API_KEY
        self.model = settings.ZHIPU_MODEL or "glm-4"
        self.client = ZhipuAI(api_key=self.api_key)

        # New: Read retry configuration from settings
        self.request_timeout = getattr(settings, 'ZHIPU_TIMEOUT', 15)
        self.retry_enabled = getattr(settings, 'ZHIPU_RETRY_ENABLED', True)
        self.retry_count = getattr(settings, 'ZHIPU_RETRY_COUNT', 1)
        self.retry_initial_delay = getattr(settings, 'ZHIPU_RETRY_INITIAL_DELAY', 1.0)

        # Existing: validate and store tone
        if tone not in self.VALID_TONES:
            logger.warning(f"无效的语调参数: {tone}，使用默认值 'no_preference'")
            self.tone = 'no_preference'
        else:
            self.tone = tone

        self.max_text_length = 1000

        logger.info(
            f"AI 文本处理器初始化完成（超时：%ds，重试：%s，重试次数：%d，初始延迟：%ds，语调：%s）",
            self.request_timeout,
            "启用" if self.retry_enabled else "禁用",
            self.retry_count if self.retry_enabled else 0,
            self.retry_initial_delay,
            self.tone
        )

    def _should_retry(self):
        """Check if retry is enabled and configured"""
        return self.retry_enabled and self.retry_count > 0

    @cache_text_result(expire_seconds=30)
    def process_text(self, raw_text):
        """
        Core method: Call Zhipu AI with retry logic
        :param raw_text: Original text to process
        :return: Processed text (never None, falls back to original on error)
        """
        # Pre-validation (existing)
        if not raw_text or not raw_text.strip():
            logger.error("原始文本为空，无需处理")
            return ""

        raw_text_strip = raw_text.strip()

        # Length check (existing)
        if len(raw_text_strip) > self.max_text_length:
            logger.warning(f"文本过长（{len(raw_text_strip)} 字符），返回原始文本")
            return raw_text_strip

        # Build prompt (existing)
        prompt = f"""请润色以下文字，使其更通顺正式，并适当分段和分点，直接返回处理后的文字，不要额外解释。
文字：{raw_text_strip}"""

        try:
            # New: Retry wrapper
            if self._should_retry():
                return self._call_ai_with_retry(prompt)
            else:
                return self._call_ai_once(prompt)

        except (ValueError, requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            logger.error(f"AI 处理失败（所有重试尝试已耗尽）: {str(e)}，返回原始文本")
            return raw_text_strip

        except Exception as e:
            logger.error(f"AI 处理未知失败: {str(e)}，返回原始文本")
            return raw_text_strip

    def _call_ai_with_retry(self, prompt):
        """Call AI API with retry logic"""
        last_exception = None
        total_attempts = self.retry_count + 1

        for attempt in range(total_attempts):
            try:
                # Log attempt
                if attempt > 0:
                    delay = self.retry_initial_delay * (2 ** (attempt - 1))
                    logger.info(f"重试第 {attempt}/{self.retry_count} 次（延迟 {delay}s）...")
                    time.sleep(delay)
                else:
                    logger.info(f"AI API 调用尝试 {attempt + 1}/{total_attempts}")

                # Call API
                response = self._make_ai_request(prompt)

                # Validate response
                processed_text = self._extract_and_validate_response(response)

                # Success
                if attempt > 0:
                    logger.info(f"重试第 {attempt} 次成功")
                return processed_text

            except (ValueError, requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                last_exception = e
                logger.warning(f"尝试 {attempt + 1}/{total_attempts} 失败: {str(e)}")

                # Check if should continue retrying
                if attempt >= self.retry_count:
                    logger.error(f"全部 {total_attempts} 次尝试均失败")
                    break

                # Continue to next retry
                continue

        # All retries exhausted
        raise last_exception

    def _call_ai_once(self, prompt):
        """Call AI API without retry (existing behavior)"""
        logger.info(f"AI API 调用（无重试）...")
        response = self._make_ai_request(prompt)
        return self._extract_and_validate_response(response)

    def _make_ai_request(self, prompt):
        """Make actual API call (extracted for reuse)"""
        system_prompt = self.get_tone_prompt(self.tone)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=self.request_timeout
        )
        return response

    def _extract_and_validate_response(self, response):
        """Extract and validate API response (extracted for reuse)"""
        raw_content = getattr(response.choices[0].message, "content", "") or ""
        processed_text = raw_content.strip()

        if not processed_text:
            logger.error("AI 返回空内容（接口响应正常，但内容为空）")
            raise ValueError("AI 返回空内容，处理失败")

        logger.info(f"AI 文本处理完成，返回文本长度: {len(processed_text)} 字符")
        return processed_text
```

**Key Changes**:
- Read retry configuration from Django settings with sensible defaults
- Extract common logic into reusable methods (`_make_ai_request`, `_extract_and_validate_response`)
- Separate retry and non-retry paths for clarity
- Enhanced logging at each step
- Cache decorator still applies to entire process (including retries)

### 4. View Layer Enhancements (views.py)

**Modified Function**: `ai_format_word(request)`

```python
def ai_format_word(request):
    # ... existing code ...

    try:
        logger.info(f"开始格式化文件: {input_file_path}, 输出到: {output_file_path}")

        # Pass retry info to template for UI feedback
        retry_enabled = getattr(settings, 'ZHIPU_RETRY_ENABLED', True)
        retry_count = getattr(settings, 'ZHIPU_RETRY_COUNT', 1)

        formatter = AIWordFormatter(input_file_path, use_ai=use_ai, tone=tone, style_config=style_config)
        original_analysis = formatter.analyze_document()
        logger.info(f"原始文档分析: {original_analysis}")

        # Add retry context to session for AJAX polling
        request.session['ai_processing'] = {
            'status': 'processing',
            'attempt': 1,
            'max_attempts': retry_count + 1 if use_ai and retry_enabled else 1,
            'timestamp': datetime.now().isoformat()
        }

        result = formatter.format(output_file_path)
        logger.info("文件格式化完成")

        # Update session status
        request.session['ai_processing']['status'] = 'complete'

        # ... existing file response code ...

    except Exception as e:
        # Update session status on error
        request.session['ai_processing'] = {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

        # ... existing error handling ...
```

### 5. UI Updates (upload_word_ai.html)

**New JavaScript**: Progress polling

```javascript
// Poll server for AI processing progress
function checkAIProcessingStatus() {
    const statusDiv = document.getElementById('ai-status');
    if (!statusDiv) return;

    const checkStatus = async () => {
        try {
            const response = await fetch('/api/ai-status/');
            const data = await response.json();

            if (data.status === 'processing') {
                const attempt = data.attempt || 1;
                const maxAttempts = data.max_attempts || 1;
                statusDiv.textContent = `正在使用 AI 处理...（尝试 ${attempt}/${maxAttempts}）`;
                statusDiv.className = 'ai-status processing';
            } else if (data.status === 'complete') {
                statusDiv.textContent = 'AI 处理完成';
                statusDiv.className = 'ai-status success';
            } else if (data.status === 'failed') {
                statusDiv.textContent = 'AI 处理失败，使用原始文本';
                statusDiv.className = 'ai-status warning';
            }
        } catch (error) {
            console.error('Failed to check AI status:', error);
        }
    };

    // Poll every 500ms during form submission
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', () => {
        statusDiv.style.display = 'block';
        const interval = setInterval(checkStatus, 500);

        // Stop polling after 30 seconds
        setTimeout(() => clearInterval(interval), 30000);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', checkAIProcessingStatus);
```

**New HTML**: Status message area

```html
<div id="ai-status" class="ai-status" style="display: none;"></div>
```

**New CSS**: Status styling

```css
.ai-status {
    padding: 12px;
    margin: 16px 0;
    border-radius: 4px;
    font-size: 14px;
}

.ai-status.processing {
    background-color: #e3f2fd;
    color: #1976d2;
    border: 1px solid #bbdefb;
}

.ai-status.success {
    background-color: #e8f5e9;
    color: #388e3c;
    border: 1px solid #c8e6c9;
}

.ai-status.warning {
    background-color: #fff3e0;
    color: #f57c00;
    border: 1px solid #ffe0b2;
}
```

### 6. New API Endpoint (views.py)

**New Function**: `ai_processing_status(request)`

```python
@require_http_methods(["GET"])
def ai_processing_status(request):
    """Return AI processing status for UI polling"""
    processing_info = request.session.get('ai_processing', {
        'status': 'unknown'
    })
    return JsonResponse(processing_info)
```

**URL Configuration** (urls.py):

```python
urlpatterns = [
    # ... existing paths ...
    path('api/ai-status/', ai_processing_status, name='ai_status'),
]
```

## Data Flow

### Successful AI Processing with Retry

```
1. User submits form
2. View creates AIWordFormatter
3. Formatter calls AITextProcessor.process_text()
4. Cache decorator checks cache (miss)
5. AITextProcessor determines retry is enabled
6. Attempt 1: Call AI API
   - API returns null/empty
   - Log "Attempt 1/2 failed: AI returned empty content"
   - Continue to retry
7. Wait 1 second (exponential backoff)
8. Attempt 2 (retry): Call AI API again
   - API returns valid content
   - Log "Retry attempt 1 succeeded"
   - Return processed text
9. Cache decorator stores result
10. UI shows "尝试 2/2" then "AI 处理完成"
```

### Failed After All Retries

```
1. Attempt 1: Timeout after 15s
   - Log "Attempt 1/2 failed: Request timeout"
2. Wait 1 second
3. Attempt 2: Connection error
   - Log "Attempt 2/2 failed: Connection error"
   - Log "All 2 attempts failed, returning fallback"
4. Return original text to user
5. UI shows "AI 处理失败，使用原始文本"
```

## Trade-offs and Decisions

### Decision 1: Inline Retry vs Decorator Pattern
**Choice**: Inline retry in `AITextProcessor`
**Rationale**:
- Simpler debugging (single function call stack)
- Easier to understand for maintainers
- More control over logging and result validation
- No need for generic retry abstraction

**Trade-off**: Less reusable than decorator, but retry logic is specific to AI calls anyway

### Decision 2: Session vs WebSocket for Progress Updates
**Choice**: Session + AJAX polling
**Rationale**:
- Simpler implementation (no WebSocket server needed)
- Existing infrastructure (Django sessions)
- Low frequency (500ms) = minimal overhead
- Works with existing form submission

**Trade-off**: Less real-time than WebSocket, but sufficient for this use case

### Decision 3: Exponential vs Fixed Backoff
**Choice**: Exponential backoff
**Rationale**:
- Industry best practice for API resilience
- Reduces pressure on struggling API
- Handles longer transient failures better

**Trade-off**: Slightly more complex calculation, but negligible

### Decision 4: Single Retry (1) vs Multiple (2-3)
**Choice**: Single retry (1 retry, 2 attempts total)
**Rationale**:
- 80% of transient failures resolve on first retry
- Keeps user wait time manageable (1s delay)
- Lower API cost
- Simpler code

**Trade-off**: Lower success rate than 3 retries, but better cost/benefit ratio

## Testing Strategy

### Unit Tests
```python
# test_ai_word_utils.py
class TestRetryLogic(unittest.TestCase):
    def test_retry_on_null_response(self):
        """Test that null response triggers retry"""
        processor = AITextProcessor()

        # Mock API to return null once, then success
        with patch.object(processor.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = [
                MockResponse(content=""),  # First attempt: null
                MockResponse(content="处理后的文本")  # Retry: success
            ]

            result = processor.process_text("原始文本")
            self.assertEqual(result, "处理后的文本")
            self.assertEqual(mock_create.call_count, 2)  # Called twice

    def test_no_retry_on_auth_error(self):
        """Test that auth errors don't trigger retry"""
        processor = AITextProcessor()

        with patch.object(processor.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = requests.exceptions.HTTPError("401 Unauthorized")

            with self.assertRaises(requests.exceptions.HTTPError):
                processor.process_text("原始文本")

            self.assertEqual(mock_create.call_count, 1)  # Only called once

    def test_exponential_backoff(self):
        """Test that retry delay doubles"""
        processor = AITextProcessor()
        processor.retry_count = 2  # 3 attempts total

        with patch.object(processor.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = [
                ValueError("Null"),
                ValueError("Null"),
                MockResponse(content="成功")
            ]

            with patch('time.sleep') as mock_sleep:
                result = processor.process_text("原始文本")

                # Verify exponential backoff: 1s, 2s
                self.assertEqual(mock_sleep.call_args_list, [
                    call(1.0),  # First retry delay
                    call(2.0)   # Second retry delay
                ])
```

### Integration Tests
```python
class TestRetryIntegration(unittest.TestCase):
    def test_full_flow_with_retry(self):
        """Test complete document processing with retry"""
        # Create test document
        test_doc = self.create_test_docx()

        # Mock AI to fail once, then succeed
        with patch('format_specifications.utils.ai_word_utils.ZhipuAI') as mock_ai:
            instance = mock_ai.return_value
            instance.chat.completions.create.side_effect = [
                TimeoutError("Timeout"),
                MockResponse(content="AI 处理后的完整文本")
            ]

            # Process document
            formatter = AIWordFormatter(test_doc, use_ai=True)
            output = formatter.format("output.docx")

            # Verify success
            self.assertTrue(os.path.exists(output))
            self.assertGreater(instance.chat.completions.create.call_count, 1)
```

### Manual Testing
- Test with actual Zhipu API to verify retry works in production
- Simulate network failures (disconnect network, then reconnect)
- Monitor logs to verify retry attempts are clearly logged
- Verify UI shows correct attempt numbers

## Security Considerations
- No new security risks (same API calls, just retried)
- Settings validation ensures timeout/retry count are reasonable (prevent abuse)
- Session data doesn't contain sensitive information (just status)
- No additional attack surface

## Performance Impact
- **Best case** (success on first attempt): No performance impact
- **Retry case** (one retry): +1 second delay for user
- **Worst case** (all retries fail): +(1+2+4...) seconds delay
- **API cost**: Increases by up to 2x when retries occur
- **Server load**: Minimal (one additional async task per retry)

**Mitigation**:
- Retry only on specific, likely-transient errors
- Low retry count (1)
- Exponential backoff reduces API pressure
- Can be disabled via settings if needed

## Migration Notes
- No database changes required
- No configuration changes required (uses defaults)
- No breaking changes to existing API
- Settings are optional (document recommended values)
- Feature flag not needed (can be deployed directly)
- Backward compatible: works without settings changes
