# Proposal: Refactor Homepage with Unified Optimization Modes

## Summary

Refactor the homepage to support three distinct document optimization modes through a unified interface:
1. **Simple Optimization** - Basic formatting with AI polishing
2. **Template-Based Optimization** - Use predefined templates to structure content
3. **Custom Structure Optimization** - User provides custom structure points

All modes will share common settings (tone, style) that are always visible and required.

## Problem Statement

### Current Issues

1. **Separated Sections**: The homepage currently has two independent sections (Document Formatting and Template Generation) which confuses users about which to use
2. **Unclear Template Selection**: Template cards have visual feedback issues - some cards stay highlighted when they shouldn't
3. **Missing Custom Structure Mode**: Users cannot provide their own custom structure/outline without using a predefined template
4. **Inconsistent Settings**: Tone and style settings are only available in some modes, not all

### User Requirements (from feedback)

**Original Chinese:**
"不要分成两个独立板块，意思是我上传一个没有规范好格式的文档，可以选择简单优化，现有通用模板规范优化，还有输入自定义结构要点规范优化，这三种模式。而语气，样式是必须有的。"

**Translation:**
"Don't split into two independent sections. I mean after uploading a poorly formatted document, I can choose from three optimization modes: simple optimization, template-based optimization using existing templates, or custom structure points optimization. Tone and style settings must be available in all modes."

**Template Selection Issue:**
"选择模板 (Select Template):有一点问题，点了这个一个模板，应该只有这个模板亮，而现实是，这个一些一直亮，一些一直不亮"

**Translation:**
"Template selection has an issue - when I click one template, only that template should be highlighted, but currently some stay highlighted and some don't highlight at all"

### Root Causes

1. **JavaScript Event Handler Bug**: Template card selection logic doesn't properly reset all cards before highlighting the selected one
2. **No Mode Selection UI**: Missing a clear way to choose between the three optimization modes
3. **Form Structure**: Two separate forms instead of one unified form that adapts based on mode selection

## Proposed Solution

### Architecture: Single Unified Form with Mode Selection

```
┌─────────────────────────────────────────────────────────┐
│  AI 辅助 Word 格式化工具                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  选择优化模式 (Select Optimization Mode):               │
│  [简单优化] [模板优化] [自定义结构]                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  上传文档 (Upload Document) - ALWAYS VISIBLE              │
│  [Browse/Choose File]                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  COMMON SETTINGS - ALWAYS VISIBLE                        │
│  - 语气 (Tone) [REQUIRED]                               │
│  - 样式模板 (Style Template) [REQUIRED]                  │
│  - 字体、字号、行间距等样式配置                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  MODE-SPECIFIC SETTINGS - Changes based on mode          │
│                                                          │
│  Mode 1: 简单优化 (Simple Optimization)                  │
│  - No additional fields needed                           │
│  - Just uses uploaded doc + common settings              │
│                                                          │
│  Mode 2: 模板优化 (Template Optimization)               │
│  - Template grid appears here                            │
│  - Template details preview                             │
│                                                          │
│  Mode 3: 自定义结构 (Custom Structure)                  │
│  - Custom structure/outline textarea                    │
│  - Optional: Reference template (for structure only)    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  [开始优化文档] - Single submit button                   │
└─────────────────────────────────────────────────────────┘
```

### Mode Descriptions

#### Mode 1: 简单优化 (Simple Optimization)
- **Purpose**: Quick formatting improvement with AI polishing
- **Use Case**: User wants better formatting but no specific structure requirements
- **Behavior**: Same as current AI formatting feature
- **Inputs**: Document + Tone + Style settings

#### Mode 2: 模板优化 (Template Optimization)
- **Purpose**: Restructure document according to predefined template
- **Use Case**: User wants document to follow a specific template structure (e.g., 年度工作总结)
- **Behavior**: AI extracts content and reorganizes it into template structure
- **Inputs**: Document + Template Selection + Tone + Style settings
- **Template Selection Fix**: Only highlight currently selected card

#### Mode 3: 自定义结构 (Custom Structure)
- **Purpose**: User provides their own structure/outline for AI to follow
- **Use Case**: User has specific structure requirements not covered by templates
- **Behavior**: AI reorganizes content according to user's structure points
- **Inputs**: Document + Custom Structure/Outline + Tone + Style settings

## Technical Changes

### 1. Frontend Changes (`upload_word_ai.html`)

#### Add Mode Selector
```html
<!-- Mode Selection Dropdown -->
<div class="form-group">
    <label for="optimizationMode">优化模式 (Optimization Mode):</label>
    <select id="optimizationMode" name="optimization_mode" required>
        <option value="simple">简单优化 - 基础格式化和AI润色</option>
        <option value="template">模板优化 - 按预设模板重新组织内容</option>
        <option value="custom">自定义结构 - 按自定义结构点组织</option>
    </select>
</div>
```

#### Refactor Form Structure
- **Remove**: Visual separator and separate "Template Generation" form
- **Keep**: Single unified form
- **Add**: Mode-specific sections that show/hide based on dropdown selection

#### Fix Template Card Selection Bug
```javascript
// Current bug: doesn't reset all cards properly
// Fix: Clear all inline styles first, then apply selection
function selectTemplateCard(card) {
    // Reset ALL cards to default state
    document.querySelectorAll('.template-card').forEach(c => {
        c.style.removeProperty('border-color');
        c.style.removeProperty('background');
        c.style.removeProperty('box-shadow');
    });

    // Apply selection styles to clicked card
    card.style.borderColor = '#667eea';
    card.style.background = '#f8f9fa';
    card.style.boxShadow = '0 5px 15px rgba(102, 126, 234, 0.2)';
}
```

#### Show/Hide Logic
```javascript
document.getElementById('optimizationMode').addEventListener('change', function() {
    const mode = this.value;

    // Hide all mode-specific sections first
    document.getElementById('templateSelectionSection').style.display = 'none';
    document.getElementById('customStructureSection').style.display = 'none';

    // Show relevant section
    if (mode === 'template') {
        document.getElementById('templateSelectionSection').style.display = 'block';
    } else if (mode === 'custom') {
        document.getElementById('customStructureSection').style.display = 'block';
    }
    // mode === 'simple' shows nothing extra
});
```

### 2. Backend Changes (`views.py`)

#### Modify `ai_format_word()` View
- Add `optimization_mode` parameter handling
- Route to different processing logic based on mode:
  - `simple`: Use existing `AIWordFormatter` logic
  - `template`: Use `generate_from_template()` logic
  - `custom`: New custom structure processing logic

#### New Custom Structure Processing
```python
def process_with_custom_structure(document_text, structure_points, tone, style_config):
    """
    Reorganize document content according to user-provided structure

    Args:
        document_text: Full text from uploaded document
        structure_points: User's custom structure/outline
        tone: Document tone
        style_config: Style configuration

    Returns:
        Formatted document following custom structure
    """
    processor = AITextProcessor(tone=tone)

    # Parse structure points (one per line or numbered list)
    structure_sections = parse_structure_points(structure_points)

    # Extract and organize content for each section
    organized_content = {}
    for section in structure_sections:
        content = processor.extract_section_for_structure(
            document_text,
            section
        )
        organized_content[section] = content

    # Build document with custom structure
    return build_custom_structure_document(organized_content, style_config)
```

### 3. URL Changes (`urls.py`)

**No changes needed** - All routing handled by existing `/ai_format/` endpoint

## Implementation Tasks

See `tasks.md` for detailed breakdown.

## Success Criteria

- [ ] Homepage has single unified form (not two separate sections)
- [ ] Mode selector dropdown with three options visible at top
- [ ] Document upload always visible (in all modes)
- [ ] Tone and style settings always visible (in all modes)
- [ ] Template cards only visible in "Template Optimization" mode
- [ ] Custom structure textarea only visible in "Custom Structure" mode
- [ ] Template card selection bug fixed (only clicked card highlights)
- [ ] Form validates correctly for each mode
- [ ] All three modes produce correct output documents

## Risks and Mitigations

### Risk 1: Breaking Existing Functionality
- **Mitigation**: Keep existing AI formatting logic intact for "Simple Optimization" mode
- **Testing**: Comprehensive testing of all three modes before deployment

### Risk 2: User Confusion About Modes
- **Mitigation**: Clear, descriptive dropdown options with explanations
- **Testing**: User testing to verify mode descriptions are clear

### Risk 3: Complex Form State Management
- **Mitigation**: Simple show/hide logic based on single dropdown value
- **Testing**: Manual testing of mode switching interactions

## Migration Path

### Phase 1: Frontend Refactor (1-2 hours)
1. Add mode selector dropdown
2. Refactor template selection into show/hide section
3. Add custom structure section
4. Fix template card selection bug
5. Update show/hide JavaScript

### Phase 2: Backend Logic (2-3 hours)
1. Modify `ai_format_word()` to handle three modes
2. Implement custom structure processing logic
3. Update form validation
4. Error handling for each mode

### Phase 3: Testing (1 hour)
1. Test Simple Optimization mode
2. Test Template Optimization mode (with all templates)
3. Test Custom Structure mode
4. Test mode switching
5. Test edge cases (missing inputs, invalid files, etc.)

**Total Estimated Time**: 4-6 hours

## Alternatives Considered

### Alternative A: Three Separate Pages
- **Pros**: Clear separation, simpler implementation
- **Cons**: Poor UX, harder to switch between modes, redundant code
- **Rejected**: User explicitly requested single unified interface

### Alternative B: Tabs Instead of Dropdown
- **Pros**: Visual mode switching
- **Cons**: Takes more space, less mobile-friendly
- **Rejected**: User preferred dropdown for compactness

### Alternative C: Keep Two Separate Forms
- **Pros**: No refactoring needed
- **Cons**: Confusing UX, violates user requirement
- **Rejected**: User explicitly asked not to have two independent sections
