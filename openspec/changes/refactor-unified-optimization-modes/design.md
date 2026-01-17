# Design: Unified Optimization Modes Architecture

## Overview

This design document explains the architectural decisions for refactoring the homepage to support three unified document optimization modes, addressing the template card selection bug and user experience issues.

## Current Architecture Problems

### Problem 1: Separated Sections
```
┌─────────────────────────────────────┐
│  Section 1: Document Formatting      │
│  - File upload                       │
│  - AI toggle                         │
│  - Style settings (when AI on)       │
│  [Submit Button]                      │
└─────────────────────────────────────┘

        [Visual Separator]

┌─────────────────────────────────────┐
│  Section 2: Template Generation      │
│  - Template cards                    │
│  - Outline input                     │
│  - Source doc upload                 │
│  - Tone selector                     │
│  [Submit Button]                      │
└─────────────────────────────────────┘
```

**Issues**:
- Two independent forms confusing users
- Duplicate settings (tone, style) in different contexts
- No clear way to choose between approaches
- Users must scroll past second section if they want first approach

### Problem 2: Template Card Selection Bug
```javascript
// Current buggy implementation
card.addEventListener('click', function() {
    document.querySelectorAll('.template-card').forEach(c => {
        c.style.borderColor = '#e0e0e0';  // ❌ Only sets border-color
        c.style.background = 'white';       // ❌ Doesn't clear other inline styles
    });
    this.style.borderColor = '#667eea';
    this.style.background = '#f8f9fa';
    // ❌ Doesn't clear box-shadow from previous selection
});
```

**Result**: Cards accumulate inline styles, some stay highlighted incorrectly

### Problem 3: Missing Custom Structure Mode
Users can only:
1. Format existing document (simple)
2. Generate from template with outline

They **cannot**:
- Provide their own custom structure for organizing content
- Extract content and organize it according to their specific requirements

## Proposed Architecture

### Single Unified Form with Mode Selection

```
┌─────────────────────────────────────────────────────────┐
│  AI 辅助 Word 格式化工具                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  文档上传 (Document Upload) - ALWAYS VISIBLE               │
│  [Browse/Choose File]                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  选择优化模式 (Select Optimization Mode)                 │
│  [简单优化 ▼] - 基础格式化和AI润色                       │
│  [模板优化 ▼] - 按预设模板重新组织内容                   │
│  [自定义结构 ▼] - 按自定义结构点组织                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  通用设置 (Common Settings) - ALWAYS VISIBLE              │
│  ✓ 文档语调 (Tone) - REQUIRED                          │
│  ✓ 样式模板 (Style Template) - REQUIRED                 │
│  ✓ 字体、字号、行间距等样式配置                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  模式特定设置 (Mode-Specific Settings)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ [SHOWN ONLY IN TEMPLATE MODE]                      │  │
│  │ Template Grid: [Card1] [Card2] ... [Card10]      │  │
│  │ Template Details Preview                             │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ [SHOWN ONLY IN CUSTOM MODE]                        │  │
│  │ Custom Structure Textarea:                         │  │
│  │ [Enter your structure points...]                   │  │
│  └───────────────────────────────────────────────────┘  │
│  (No extra settings in Simple mode)                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  [开始优化文档] - Single submit button                   │
└─────────────────────────────────────────────────────────┘
```

### State Management

**Mode State**:
```javascript
const currentMode = {
    value: 'simple',  // 'simple' | 'template' | 'custom'

    // Simple mode: no additional state

    // Template mode:
    selectedTemplateId: null,

    // Custom mode:
    customStructure: ''
}
```

**UI State per Mode**:

| Component | Simple Mode | Template Mode | Custom Mode |
|-----------|-------------|---------------|-------------|
| Document Upload | ✅ Visible | ✅ Visible | ✅ Visible |
| Mode Selector | ✅ Visible | ✅ Visible | ✅ Visible |
| Tone Selector | ✅ Visible | ✅ Visible | ✅ Visible |
| Style Settings | ✅ Visible | ✅ Visible | ✅ Visible |
| Template Grid | ❌ Hidden | ✅ Visible | ❌ Hidden |
| Template Details | ❌ Hidden | ✅ Visible (after selection) | ❌ Hidden |
| Custom Structure | ❌ Hidden | ❌ Hidden | ✅ Visible |

## Component Design

### 1. Mode Selector Component

**Type**: Dropdown select (HTML `<select>`)
**Options**:
```html
<select id="optimizationMode" name="optimization_mode">
    <option value="simple">简单优化 - 基础格式化和AI润色</option>
    <option value="template">模板优化 - 按预设模板重新组织内容</option>
    <option value="custom">自定义结构 - 按自定义结构点组织</option>
</select>
```

**Event Handler**:
```javascript
document.getElementById('optimizationMode').addEventListener('change', function() {
    const mode = this.value;

    // 1. Hide all mode-specific sections
    hideAllModeSpecificSections();

    // 2. Reset mode-specific state
    resetModeSpecificState(mode);

    // 3. Show relevant section
    showModeSpecificSection(mode);
});
```

### 2. Template Card Component

**Bug Fix Strategy**: Use `removeAttribute('style')` instead of manipulating individual style properties

**Before (Buggy)**:
```javascript
card.addEventListener('click', function() {
    document.querySelectorAll('.template-card').forEach(c => {
        c.style.borderColor = '#e0e0e0';     // ❌ Only sets border
        c.style.background = 'white';          // ❌ Doesn't clear all
        // box-shadow not touched at all ❌
    });
    this.style.borderColor = '#667eea';       // ❌ Adds more inline styles
});
```

**After (Fixed)**:
```javascript
card.addEventListener('click', function() {
    // Reset ALL cards to default state
    document.querySelectorAll('.template-card').forEach(c => {
        c.removeAttribute('style');              // ✅ Clear ALL inline styles
        // Re-apply CSS class default (optional, if needed)
        c.className = 'template-card';
    });

    // Apply selection via class (not inline styles)
    this.classList.add('selected');

    // Or apply inline styles if preferred
    this.style.cssText = 'border: 2px solid #667eea; background: #f8f9fa; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);';
});
```

**CSS Approach (Recommended)**:
```css
.template-card {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
    cursor: pointer;
    transition: all 0.3s;
    background: white;
}

.template-card:hover {
    border-color: #667eea;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.template-card.selected {
    border-color: #667eea;
    background: #f8f9fa;
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}
```

```javascript
// JavaScript just toggles class
card.addEventListener('click', function() {
    document.querySelectorAll('.template-card').forEach(c => {
        c.classList.remove('selected');
    });
    this.classList.add('selected');
});
```

**Why This Fixes the Bug**:
- `classList.remove('selected')` reliably removes the class from ALL cards
- No inline styles accumulate
- CSS selector (`.selected`) has higher specificity, overrides default styles
- Single source of truth (CSS class) instead of scattered inline styles

### 3. Show/Hide Logic

**Implementation**: Simple display toggle based on mode

```javascript
function showModeSpecificSection(mode) {
    // Hide all first
    document.getElementById('templateSelectionSection').style.display = 'none';
    document.getElementById('customStructureSection').style.display = 'none';

    // Show relevant
    if (mode === 'template') {
        document.getElementById('templateSelectionSection').style.display = 'block';
    } else if (mode === 'custom') {
        document.getElementById('customStructureSection').style.display = 'block';
    }
    // mode === 'simple': nothing to show
}
```

**Alternative (CSS Classes)**:
```css
.mode-specific-section {
    display: none;
}

.mode-specific-section.active {
    display: block;
}
```

```javascript
function showModeSpecificSection(mode) {
    document.querySelectorAll('.mode-specific-section').forEach(el => {
        el.classList.remove('active');
    });

    if (mode === 'template') {
        document.getElementById('templateSelectionSection').classList.add('active');
    } else if (mode === 'custom') {
        document.getElementById('customStructureSection').classList.add('active');
    }
}
```

## Backend Flow

### Request Processing Flow

```
┌─────────────────┐
│  User Submits    │
│  Form            │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  ai_format_word() view           │
│  - optimization_mode parameter   │
│  - Common settings (tone, style) │
└────────┬────────────────────────┘
         │
         ▼
    ┌────┴────┬────────────┬────────────┐
    │         │            │            │
    ▼         ▼            ▼            ▼
┌────────┐ ┌─────────┐  ┌──────────┐ ┌────────┐
│ Simple │ │ Template│  │ Custom   │ │ Error  │
│ Mode   │ │ Mode    │  │ Structure│ │        │
└───┬────┘ └────┬────┘  └────┬─────┘ └────────┘
    │           │            │
    ▼           ▼            ▼
┌────────┐ ┌─────────┐  ┌──────────┐
│AIWord  │ │Generate │  │Custom    │
│Formatter│ │From     │  │Structure │
│        │ │Template │  │Extraction│
└───┬────┘ └────┬────┘  └────┬─────┘
    │           │            │
    └───────────┴────────────┘
                │
                ▼
         ┌──────────────┐
         │  Build       │
         │  Document    │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │  File        │
         │  Response    │
         └──────────────┘
```

### Mode Handlers

#### Simple Mode Handler
```python
def handle_simple_optimization(uploaded_file, use_ai, tone, style_config):
    """
    Reuses existing AIWordFormatter logic
    """
    # 1. Save uploaded file
    # 2. Create AIWordFormatter instance
    # 3. Call formatter.format(output_path)
    # 4. Return FileResponse
```

**No changes to existing logic** - just extracted into a function

#### Template Mode Handler
```python
def handle_template_optimization(request, uploaded_file, tone, style_config):
    """
    Combines document extraction + template generation
    """
    # 1. Validate template_id from POST
    # 2. Get template from TemplateManager
    # 3. Extract text from uploaded document
    # 4. Call AITextProcessor.generate_from_template()
    #    - With extracted text as source_document_text
    #    - With empty user_outline (extract from doc instead)
    # 5. Build document from generated content
    # 6. Return FileResponse
```

**Key Decision**: Use extracted content, don't require user outline

#### Custom Structure Mode Handler
```python
def handle_custom_optimization(request, uploaded_file, tone, style_config):
    """
    Extracts and organizes content according to user's structure
    """
    # 1. Validate custom_structure from POST
    # 2. Parse structure into sections
    # 3. Extract text from uploaded document
    # 4. For each section: extract relevant content
    # 5. Build document with custom structure
    # 6. Return FileResponse
```

**New Logic**: Custom structure parsing + section-by-section extraction

## Data Flow Examples

### Example 1: Simple Mode

**Input**:
- Document: `messy_format.docx`
- Mode: `simple`
- Tone: `direct`
- Style: `professional`

**Process**:
```
messy_format.docx
  → Extract text
  → AIWordFormatter.format()
    → Apply style templates
    → AI polish (if enabled)
  → Output: messy_format_formatted.docx
```

### Example 2: Template Mode

**Input**:
- Document: `project_report.docx` (unstructured content)
- Mode: `template`
- Template: `年度工作总结`
- Tone: `rigorous`
- Style: `professional`

**Process**:
```
project_report.docx
  → Extract full text
  → Generate from template (年度工作总结)
    → For each section in template:
      → Extract relevant content from source
      → If found: refine to match section requirements
      → If not found: generate skeleton with placeholders
  → Output: project_report_年度总结.docx
    (structured according to 年度工作总结 template)
```

### Example 3: Custom Structure Mode

**Input**:
- Document: `project_notes.docx`
- Mode: `custom`
- Custom Structure:
  ```
  1. 项目背景
  2. 技术方案
  3. 实施过程
  4. 测试结果
  5. 结论
  ```
- Tone: `direct`
- Style: `technical`

**Process**:
```
project_notes.docx
  → Extract full text
  → Parse custom structure into 5 sections
  → For each section:
    → AI extracts relevant content for that section title
    → Example: "项目背景" → finds background information
  → Output: project_notes_custom.docx
    (organized with 5 sections as specified)
```

## Validation Strategy

### Frontend Validation

**Per-Mode Requirements**:

| Mode | File | Tone | Style | Template | Custom Structure |
|------|------|------|-------|----------|------------------|
| Simple | ✓ Required | ✓ Required | ✓ Required | ✗ N/A | ✗ N/A |
| Template | ✓ Required | ✓ Required | ✓ Required | ✓ Required | ✗ N/A |
| Custom | ✓ Required | ✓ Required | ✓ Required | ✗ N/A | ✓ Required |

**Validation Flow**:
```javascript
form.addEventListener('submit', function(e) {
    // Common validation
    if (!file) { showError('请上传文档'); e.preventDefault(); return; }
    if (!tone) { showError('请选择语调'); e.preventDefault(); return; }
    if (!style) { showError('请选择样式'); e.preventDefault(); return; }

    // Mode-specific validation
    switch(mode) {
        case 'template':
            if (!selectedTemplate) { showError('请选择模板'); e.preventDefault(); }
            break;
        case 'custom':
            if (!customStructure) { showError('请输入结构要点'); e.preventDefault(); }
            break;
    }
});
```

### Backend Validation

```python
def ai_format_word(request):
    mode = request.POST.get('optimization_mode')

    # Common validation
    if 'word_file' not in request.FILES:
        return error_response('请上传Word文档')

    # Mode-specific validation
    if mode == 'template':
        template_id = request.POST.get('template_id')
        if not template_id:
            return error_response('请选择模板')

        template = TemplateManager.get_template(template_id)
        if not template:
            return error_response(f'模板不存在: {template_id}')

    if mode == 'custom':
        custom_structure = request.POST.get('custom_structure', '').strip()
        if not custom_structure:
            return error_response('请输入自定义结构要点')

    # Process...
```

## Technical Trade-offs

### Decision 1: Dropdown vs Radio Buttons vs Tabs

**Chosen**: Dropdown

**Rationale**:
- Most compact UI option
- Familiar pattern for mode selection
- Mobile-friendly
- Easy to add more modes in future

**Rejected Alternatives**:
- **Radio buttons**: Take more space, not as mobile-friendly
- **Tabs**: Take more horizontal space, less clear that modes are mutually exclusive

### Decision 2: CSS Classes vs Inline Styles for Template Selection

**Chosen**: CSS classes with `.selected` modifier

**Rationale**:
- Single source of truth (CSS)
- No inline style accumulation bug
- Easier to maintain and extend
- Better separation of concerns

**Rejected Alternative**:
- **Inline styles**: Bug-prone, hard to maintain, harder to override

### Decision 3: Single Form vs Multiple Forms

**Chosen**: Single form with show/hide sections

**Rationale**:
- Cleaner DOM structure
- Single submit button
- Common settings shared (no duplication)
- Easier form validation

**Rejected Alternative**:
- **Multiple forms**: Confusing UX, duplicate settings, harder validation

## Migration Impact

### Breaking Changes
- **None**: This is purely a frontend refactor
- Backend API endpoints unchanged
- Existing simple mode functionality preserved

### Database Changes
- **None**: No schema changes required

### Backward Compatibility
- **Full**: Existing "simple optimization" (current AI formatting) works exactly as before

## Future Extensibility

### Adding New Modes

To add a fourth mode (e.g., "Translation Mode"):

1. **Frontend**:
   - Add option to dropdown: `<option value="translate">翻译模式</option>`
   - Add show/hide section: `<div id="translateSection" class="mode-specific-section">`
   - Add show/hide logic: `if (mode === 'translate') showSection('translateSection')`

2. **Backend**:
   - Add handler: `handle_translate_optimization()`
   - Add routing: `elif mode == 'translate': return handle_translate_optimization(...)`

### Adding Settings

To add a new common setting (e.g., "Language"):

1. **Frontend**: Add to common settings section (always visible)
2. **Backend**: Extract from POST in all mode handlers
3. **Validation**: Add to validation logic (common to all modes)

## Performance Considerations

### Frontend Performance

- **Show/Hide**: O(1) operation, negligible performance impact
- **Template Cards**: 10 cards × minimal DOM = fast rendering
- **JavaScript**: Minimal event handlers, no heavy computation

### Backend Performance

- **Simple Mode**: No performance change (existing logic)
- **Template Mode**: +1 AI API call (template generation) - acceptable
- **Custom Mode**: +N AI calls (N = number of custom sections) - could be slow

**Optimization for Custom Mode**:
- Limit custom sections to 10-15 maximum
- Batch AI calls if possible
- Consider caching extraction results

## Security Considerations

### Input Validation

**Frontend**:
- File type validation (`.docx` only)
- File size validation (existing limits apply)
- Required field validation (HTML5 + JavaScript)

**Backend**:
- Re-validate all inputs (never trust frontend)
- Sanitize AI prompts (prevent injection attacks)
- Validate template IDs (whitelist check)

### AI Prompt Security

**Template Mode**:
```python
# Safe: predefined template structure
prompt = f"根据模板 {template.name} 组织内容..."
# ✅ Controlled, predefined structure

# Dangerous: arbitrary user input in prompt
prompt = f"按照用户要求重新组织: {user_unsanitized_input}"
# ❌ Risk of prompt injection
```

**Solution**: Always use predefined template structures, only extract from user input

## Testing Strategy

### Unit Tests Needed

```python
# tests/test_optimization_modes.py

def test_simple_mode_extracts_correctly():
    """Test simple mode uses existing formatter"""

def test_template_mode_reorganizes_content():
    """Test template mode restructures document"""

def test_custom_mode_follows_structure():
    """Test custom mode organizes by user structure"""

def test_mode_switching_resets_state():
    """Test switching modes clears previous selections"""
```

### Integration Tests Needed

```python
def test_full_simple_mode_workflow():
    """Test complete simple mode flow"""

def test_full_template_mode_workflow():
    """Test complete template mode flow"""

def test_full_custom_mode_workflow():
    """Test complete custom mode flow"""
```

### Manual Testing Checklist

- [ ] All three modes produce valid output
- [ ] Mode switching doesn't pollute state
- [ ] Template selection bug is fixed
- [ ] Form validation catches all error cases
- [ ] Tone and style apply correctly in all modes
- [ ] File upload works in all modes
- [ ] Mobile responsive design works

## Rollback Plan

If issues arise during deployment:

1. **Immediate Rollback**:
   - Revert `upload_word_ai.html` to backup
   - Revert `views.py` to backup
   - System returns to pre-refactor state

2. **Partial Rollback**:
   - Keep frontend changes
   - Revert backend changes
   - System shows new UI but modes don't work (display only)

3. **Database Rollback**:
   - Not needed (no schema changes)
