# Proposal: Add AI Polishing to Custom Structure Mode

## Metadata
- **Change ID**: add-polish-to-custom-structure-ef19eba3
- **Status**: Proposed
- **Created**: 2025-01-17
- **Author**: Claude

## Problem Statement

When users select "自定义结构" (Custom Structure) optimization mode, the content is **not polished/refined by AI**. The content appears exactly as extracted from the source document, without the AI enhancement that users expect.

### User Report
"when use the custom template ,the content was not polish, why ?"

### Current Behavior
In `handle_custom_optimization()` (views.py line 450-510):
1. Extracts content from source document using `extract_section_for_structure()`
2. The method only **extracts** content with prompt: "保持原文表述" (keep original wording)
3. **NO AI polishing/refinement is applied**

### Expected Behavior
Custom structure mode should polish/refine content just like:
- **Simple optimization mode**: Uses `AIWordFormatter._process_with_ai()` → `process_text()` to polish
- **Template optimization mode**: Uses `_refine_extracted_content()` to polish extracted content

### Impact
- Users get unpolished, raw content in custom structure mode
- Inconsistent behavior across optimization modes
- Custom structure mode is less useful than other modes

## Root Cause

**File**: `format_specifications/views.py`
**Function**: `generate_with_custom_structure()` (line 588-602)

**Current Implementation**:
```python
def generate_with_custom_structure(processor, source_text, structure_sections):
    """Generate document content organized by custom structure"""
    generated_content = {}

    for section in structure_sections:
        # Extract content relevant to this section
        content = processor.extract_section_for_structure(
            source_text,
            section['title']
        )
        generated_content[section['title']] = content  # ❌ No polishing!

    return generated_content
```

**Problem**:
- `extract_section_for_structure()` only extracts, doesn't polish
- No call to `process_text()` or `_refine_extracted_content()`
- Content is written directly to document without AI enhancement

## Proposed Solution

### Option 1: Polish After Extraction (Recommended)
After extracting content for each section, polish it using `process_text()`:

```python
def generate_with_custom_structure(processor, source_text, structure_sections):
    """Generate document content organized by custom structure"""
    generated_content = {}

    for section in structure_sections:
        # Extract content relevant to this section
        extracted = processor.extract_section_for_structure(
            source_text,
            section['title']
        )

        # Polish the extracted content
        if extracted and extracted.strip():
            polished = processor.process_text(extracted)
            generated_content[section['title']] = polished
        else:
            generated_content[section['title']] = ""

    return generated_content
```

**Pros**:
- Minimal change
- Consistent with simple optimization mode
- Preserves tone/style settings

**Cons**:
- One additional AI call per section (could be slow for many sections)

### Option 2: Polish Entire Document at End
After generating all sections, polish the entire document using `AIWordFormatter`:

```python
# In handle_custom_optimization(), after building document:
output_doc = Document()
# ... build document with custom structure ...

# Apply AI polishing to the entire document
formatter = AIWordFormatter(
    input_file_path=tmp_file_path,
    use_ai=True,
    tone=tone,
    style_config=style_config
)
formatted_doc = formatter.format(output_file_path)
```

**Pros**:
- Reuses existing polish logic
- Only one AI call for entire document
- Consistent with simple mode

**Cons**:
- May reorganize custom structure
- Harder to control section boundaries

### Option 3: Update Extraction Prompt to Polish
Change `extract_section_for_structure()` prompt to include polishing instructions:

```python
prompt = f"""请从以下文档中提取与"{section_title}"相关的内容，并进行润色优化。

**要求**：
- 提取文档中与"{section_title}"直接相关的内容
- 对提取的内容进行润色：改进措辞、优化分段、统一样式
- 保持原文表述的核心意思
- 使用{tone}语调

**源文档**：
{source_text[:3000]}
"""
```

**Pros**:
- Single AI call per section
- Simpler code flow

**Cons**:
- Changes contract of `extract_section_for_structure()`
- May affect template optimization mode

## Recommendation

**Go with Option 1**: Polish after extraction using `process_text()`.

### Rationale
1. **Clear separation**: Extraction and polishing are separate concerns
2. **Consistency**: Uses same `process_text()` method as simple optimization
3. **Predictable**: One AI call per section for extraction, one for polishing
4. **Maintainable**: Easy to understand and debug

### Implementation
1. Update `generate_with_custom_structure()` in views.py
2. Add polishing step after extraction
3. Add logging to track polishing calls
4. Test with custom structure input

## Alternatives Considered

### Alternative: Don't Polish in Custom Mode
Users might want raw extraction in custom mode.

**Counter-argument**:
- Other modes all polish by default
- Users expect consistency
- Can add "AI toggle" option later if needed

## Related Changes

None - this is a standalone improvement.

## Success Criteria

- [ ] Custom structure mode output is polished/refined
- [ ] Content uses improved wording and better structure
- [ ] Tone/style settings are respected
- [ ] Performance acceptable (<2 minutes for typical use)
- [ ] Logs show polishing calls

## Testing

**Test Case 1: Custom Structure with Short Content**
- Input: Document with basic bullet points
- Custom structure: "项目背景\n实施过程\n结果"
- Expected: Extracted content is polished and reorganized

**Test Case 2: Custom Structure with Long Content**
- Input: Document with multiple paragraphs
- Custom structure: Complex structure with 8+ sections
- Expected: All sections polished and organized correctly

**Test Case 3: Compare with Simple Mode**
- Same document processed with simple mode vs custom structure mode
- Expected: Similar quality of polishing
