# Design: Text Tone Selection

## Architecture Overview

This feature extends the existing AI text processing pipeline without introducing new components. The tone parameter flows from the UI through the view layer to the AI service, where it influences the prompt generation.

```
[UI] → [View] → [Formatter] → [AI Processor] → [Zhipu AI]
  ↓       ↓          ↓                ↓
Tone    Extract    Pass to         Apply tone
Select  from POST  AIProcessor     prompt
```

## Component Changes

### 1. AITextProcessor (ai_word_utils.py)

**New Method**: `get_tone_prompt(tone: str) -> str`
- Maps tone enum to tone-specific system prompts
- Returns default prompt for unknown tones
- No external dependencies

**Modified Method**: `__init__(self, tone='no_preference')`
- Stores tone preference as instance variable
- Validates tone against allowed values
- Logs warning for invalid tones

**Modified Method**: `process_text(self, raw_text)`
- Uses `self.get_tone_prompt()` to get system message
- Passes tone-specific prompt to Zhipu AI
- Maintains all existing error handling

**Tone Prompt Mapping**:
```python
TONES = {
    'rigorous': "你是专业的文字处理助手，使用严谨、精确、证据驱动的语言风格...",
    'cold_sharp': "你是专业的文字处理助手，使用权威、果断、直截了当的语言风格...",
    'humorous': "你是专业的文字处理助手，使用轻松、有趣、引人入胜的语言风格...",
    'empathetic': "你是专业的文字处理助手，使用温暖、理解、富有人情味的语言风格...",
    'direct': "你是专业的文字处理助手，使用简洁、清晰、行动导向的语言风格...",
    'inspirational': "你是专业的文字处理助手，使用鼓舞人心、有远见、充满活力的语言风格...",
    'no_preference': "你是专业的文字处理助手，擅长结构化文本优化。"
}
```

### 2. View Layer (views.py)

**Modified Function**: `ai_format_word(request)`
- Extract `tone = request.POST.get('tone', 'no_preference')`
- Pass to `AIWordFormatter(input_file_path, use_ai=use_ai, tone=tone)`
- Add logging: `logger.info(f"Selected tone: {tone}")`

### 3. Service Layer (word_formatter.py)

**Modified Class**: `AIWordFormatter`
- Update `__init__(self, input_file_path, use_ai=True, tone='no_preference')`
- Store `self.tone = tone`
- Pass to `AITextProcessor(tone=self.tone)` when instantiating

### 4. UI Layer (upload_word_ai.html)

**New HTML Section**: Tone selector (inserted after AI checkbox)
```html
<div class="form-group">
    <label for="tone">文本语调 (Text Tone):</label>
    <select id="tone" name="tone" class="tone-selector">
        <option value="no_preference" selected>无偏好 (No preference)</option>
        <option value="rigorous">严格 (Rigorous) - 适合正式文档</option>
        <option value="cold_sharp">冷酷权威 (Cold/Sharp) - 适合指令</option>
        <option value="humorous">幽默 (Humorous) - 适合营销</option>
        <option value="empathetic">同理心 (Empathetic) - 适合沟通</option>
        <option value="direct">直接 (Direct) - 适合内部通知</option>
        <option value="inspirational">鼓舞人心 (Inspirational) - 适合演讲</option>
    </select>
    <small id="tone-hint"></small>
</div>
```

**New JavaScript**: Conditional enabling/disabling
```javascript
const aiCheckbox = document.getElementById('use_ai');
const toneSelector = document.getElementById('tone');
const toneHint = document.getElementById('tone-hint');

function updateToneSelector() {
    if (aiCheckbox.checked) {
        toneSelector.disabled = false;
        toneHint.textContent = '';
    } else {
        toneSelector.disabled = true;
        toneHint.textContent = '需要启用 AI 处理 (Requires AI processing)';
    }
}

aiCheckbox.addEventListener('change', updateToneSelector);
updateToneSelector(); // Initialize state
```

## Data Flow

### Request Flow
1. User selects tone from dropdown
2. User submits form with `tone="rigorous"` (example)
3. View extracts tone from POST data
4. View passes tone to `AIWordFormatter`
5. Formatter passes tone to `AITextProcessor`
6. AI processor applies "rigorous" system prompt
7. Zhipu AI returns tone-styled text
8. Document formatted and returned

### Error Handling Flow
1. If tone is invalid/missing → default to "no_preference"
2. If AI processing fails → fallback to original text (existing behavior)
3. If tone selector disabled → visual feedback + form submission uses selected value

## Trade-offs and Decisions

### Decision 1: Extend AITextProcessor vs Create New Classes
**Choice**: Extend existing `AITextProcessor`
**Rationale**:
- Minimal code duplication
- Consistent error handling and caching
- Easier to maintain
- Single source of truth for AI interaction

**Trade-off**: Slightly larger class, but acceptable given focused responsibility

### Decision 2: Dropdown vs Radio Buttons
**Choice**: Dropdown (select element)
**Rationale**:
- Compact UI (7 options + default = 8 total)
- Familiar pattern for settings
- Easy to disable/enable visually
- Mobile-friendly

**Trade-off**: All options not visible at once, but acceptable for secondary setting

### Decision 3: Always Visible vs Hidden When AI Disabled
**Choice**: Always visible, conditionally enabled
**Rationale**:
- Users discover the feature exists
- Clear relationship to AI checkbox
- Better UX than hiding/showing dynamically

**Trade-off**: Slightly more complex UI state management, but worth it for discoverability

## Testing Strategy

### Unit Tests
- Test `get_tone_prompt()` returns correct prompts for all tones
- Test `get_tone_prompt()` returns default for invalid tone
- Test `process_text()` with each tone produces distinct output
- Test backward compatibility (no tone parameter)

### Integration Tests
- Test full flow: UI → View → Formatter → AI → Output
- Test tone selector disabled state with JavaScript
- Test form submission with each tone
- Test invalid tone falls back gracefully

### Manual Testing
- Process sample document with each tone
- Verify tone characteristics in output
- Verify "No preference" matches pre-change behavior
- Verify disabled state when AI is off

## Security Considerations
- Tone parameter is server-side validated (whitelist approach)
- No risk of prompt injection (predefined prompts only)
- No additional attack surface (uses existing AI pipeline)

## Performance Impact
- Negligible: One additional string lookup per request
- No additional API calls
- Same caching behavior (30-second cache)
- Same timeout limits (15 seconds)

## Migration Notes
- No database changes required
- No configuration changes required
- No breaking changes to existing API
- Feature flag not needed (can be deployed directly)
