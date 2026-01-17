# Tasks: Add AI Polishing to Custom Structure Mode

## Summary

Add AI text polishing to custom structure optimization mode to match the behavior of simple and template optimization modes.

## Phase 1: Implementation

### Task 1.1: Update `generate_with_custom_structure()` Function ✅
**File**: `format_specifications/views.py`
**Line**: 588-612
**Effort**: 10 minutes

**Steps**:
1. Add polishing step after extraction
2. Call `processor.process_text()` on extracted content
3. Handle empty content gracefully

**Code Change**:
```python
def generate_with_custom_structure(processor, source_text, structure_sections):
    """
    Generate document content organized by custom structure
    """
    generated_content = {}

    for section in structure_sections:
        # Extract content relevant to this section
        extracted = processor.extract_section_for_structure(
            source_text,
            section['title']
        )
        logger.info(f"Extracted {len(extracted) if extracted else 0} chars for section: {section['title']}")

        # Polish the extracted content
        if extracted and extracted.strip() and len(extracted.strip()) > 10:
            logger.info(f"Polishing content for section: {section['title']}")
            polished = processor.process_text(extracted)
            generated_content[section['title']] = polished
            logger.info(f"Polished content: {len(polished)} chars")
        else:
            logger.warning(f"Section {section['title']} has no meaningful content, skipping polishing")
            generated_content[section['title']] = ""

    return generated_content
```

**Validation**:
- ✅ Logs show "Polishing content for section: [name]"
- ✅ Logs show "Polished content: X chars"

---

### Task 1.2: Test with Simple Custom Structure
**Effort**: 5 minutes

**Steps**:
1. Create test document with basic content
2. Use custom structure: "工作内容\n遇到的问题\n解决方案"
3. Upload and process
4. Check output document

**Expected**:
- Content is polished and reorganized
- No raw/unpolished text
- Logs show polishing calls

---

### Task 1.3: Test with Complex Custom Structure
**Effort**: 5 minutes

**Steps**:
1. Create test document with detailed content
2. Use custom structure with 8+ sections
3. Upload and process
4. Check output document

**Expected**:
- All sections polished
- No sections skipped unless empty
- Processing completes in reasonable time

---

## Phase 2: Verification

### Task 2.1: Compare Output Quality
**Effort**: 10 minutes

**Steps**:
1. Process same document with simple mode
2. Process same document with custom structure mode (use same structure as simple output)
3. Compare output documents side by side

**Expected**:
- Similar quality of polishing
- Both have improved wording
- Both have better structure

---

### Task 2.2: Verify Tone Settings
**Effort**: 5 minutes

**Steps**:
1. Select custom structure mode
2. Choose different tone (e.g., "正式")
3. Upload and process document
4. Check output uses formal tone

**Expected**:
- Output respects tone setting
- Polished content matches selected tone

---

### Task 2.3: Check Performance
**Effort**: 5 minutes

**Steps**:
1. Test with document with 10 custom sections
2. Measure total processing time
3. Check logs for AI call count

**Expected**:
- 1 AI call per section (extraction)
- 1 AI call per section (polishing)
- Total time reasonable (<2 minutes for typical use)

---

## Summary

**Total Tasks**: 6
**Estimated Time**: 40 minutes
**Priority**: Medium

**Dependencies**:
- None (standalone improvement)

**Parallelizable**:
- Tasks 1.2 and 1.3 can be done in parallel after Task 1.1
- Tasks 2.1, 2.2, 2.3 can be done in parallel after implementation
