# Text Tone Selection - Proposal Summary

## 📋 Overview
This proposal adds a tone selection feature to the AI Word document formatting tool, allowing users to choose from 7 predefined text tones that influence AI text processing.

## 🎯 What's Being Added

### 7 Tone Options
| Tone | Chinese | Purpose |
|------|---------|---------|
| Rigorous | 严格 | To prove/inform - Formal, precise language |
| Cold/Sharp | 冷酷/尖锐 | Authoritative - Direct, commanding style |
| Humorous | 幽默 | To engage - Light, fun, memorable |
| Empathetic | 同理心 | To comfort - Kind, soft, human |
| Direct | 直接 | To act - Fast, clear, urgent |
| Inspirational | 鼓舞人心 | To motivate - High energy, visionary |
| No preference | 无偏好 | Default - Maintains current behavior |

### User Experience
- **UI**: Dropdown selector below the AI checkbox
- **Behavior**: Disabled when AI is off, enabled when AI is on
- **Default**: "No preference" maintains current neutral tone
- **Feedback**: Tooltip explains why disabled when AI is unchecked

## 🏗️ Technical Approach

### Architecture
```
UI → View → Formatter → AI Processor → Zhipu AI
↓    ↓        ↓              ↓
Tone Extract Pass to      Apply tone
Select  POST  AIProcessor  prompt
```

### Key Changes
1. **Backend**: Extend `AITextProcessor` with tone parameter
2. **View**: Extract and pass tone from POST data
3. **Service**: Pass tone through `AIWordFormatter`
4. **UI**: Add dropdown with JavaScript conditional enabling

### Design Decisions
- ✅ Extend existing `AITextProcessor` (not new classes)
- ✅ Dropdown UI (compact, familiar pattern)
- ✅ Always visible, conditionally enabled (better discoverability)
- ✅ Server-side validation (whitelist approach)

## 📊 Impact Assessment

### Positive Impact
- ✅ Users can tailor document tone to specific contexts
- ✅ No breaking changes (backward compatible)
- ✅ Minimal performance overhead (one string lookup)
- ✅ No additional API calls or costs

### Risk Mitigation
- ✅ Invalid tones default to "No preference"
- ✅ Existing tests pass (backward compatibility)
- ✅ Graceful degradation if AI service fails
- ✅ No security concerns (predefined prompts only)

## 📝 Implementation Steps

### 1. Backend (High Priority)
- Add tone parameter to `AITextProcessor.__init__()`
- Create `get_tone_prompt()` method with tone-specific prompts
- Update `process_text()` to use tone prompts
- Add validation and fallback logic

### 2. View Layer (High Priority)
- Extract tone from POST data in `ai_format_word()`
- Pass tone to `AIWordFormatter`
- Add logging for debugging

### 3. Service Layer (High Priority)
- Update `AIWordFormatter.__init__()` to accept tone
- Pass tone to `AITextProcessor`

### 4. Frontend (Medium Priority)
- Add tone dropdown to `upload_word_ai.html`
- Implement JavaScript for conditional enabling/disabling
- Style to match existing UI

### 5. Testing (Medium Priority)
- Unit tests for each tone
- Integration tests for full flow
- Manual validation with sample documents

## ✅ Success Criteria
- [ ] All 7 tones + "No preference" appear in UI
- [ ] Tone selector is disabled when AI is off
- [ ] Each tone produces distinctly styled output
- [ ] "No preference" matches pre-change behavior
- [ ] Invalid tones fall back gracefully
- [ ] No errors in processing

## 🚀 Next Steps

1. **Review this proposal** - Ensure it meets your needs
2. **Approve for implementation** - Use `openspec apply add-text-tone-selection`
3. **Monitor implementation** - Track progress via tasks.md
4. **Test thoroughly** - Validate each tone produces expected output

## 📁 Proposal Files
- `proposal.md` - Detailed proposal with motivation and alternatives
- `tasks.md` - Ordered implementation tasks with dependencies
- `design.md` - Technical architecture and design decisions
- `specs/text-tone-selection/spec.md` - Formal requirements with scenarios

---

**Status**: ✅ Validated and ready for approval
**Validation**: `openspec validate add-text-tone-selection --strict` ✓
