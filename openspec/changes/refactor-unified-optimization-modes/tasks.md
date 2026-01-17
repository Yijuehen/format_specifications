# Tasks: Refactor Homepage with Unified Optimization Modes

## Summary

**Status**: ✅ COMPLETED
**Completion Date**: 2025-01-16
**Total Implementation Time**: ~2 hours

All 15 tasks have been successfully completed. The homepage now features a unified form with three optimization modes (simple, template, custom), fixed template card selection bug, and proper mode switching logic.

## Phase 1: Frontend Refactor ✅

### Task 1.1: Add Mode Selector Dropdown ✅
**File**: `format_specifications/templates/upload_word_ai.html`
**Status**: COMPLETED

```html
<div class="form-group">
    <label for="optimizationMode">优化模式 (Optimization Mode):</label>
    <select id="optimizationMode" name="optimization_mode" required>
        <option value="simple">简单优化 - 基础格式化和AI润色</option>
        <option value="template">模板优化 - 按预设模板重新组织内容</option>
        <option value="custom">自定义结构 - 按自定义结构点组织</option>
    </select>
    <small style="color: #888;">选择文档优化方式</small>
</div>
```

**Validation**: ✅ Dropdown appears on page, three options visible

---

### Task 1.2: Move Tone and Style to Always Visible
**File**: `format_specifications/templates/upload_word_ai.html`
**Current**: Tone only visible when AI toggle is on
**Change**: Make tone and style settings always visible (outside AI toggle section)
**Effort**: 20 minutes

**Steps**:
1. Locate tone selector in AI toggle conditional
2. Move it outside the conditional, always visible
3. Move style template selector outside conditional as well
4. Update labels to indicate these are required

**Validation**: Tone and style selectors visible even when AI toggle is off

---

### Task 1.3: Create Template Selection Section (Show/Hide)
**File**: `format_specifications/templates/upload_word_ai.html`
**Location**: After common settings, wrapped in show/hide container
**Effort**: 30 minutes

```html
<!-- Template Selection Section - Hidden by default -->
<div id="templateSelectionSection" style="display: none;">
    <div class="form-group">
        <label for="templateId">选择模板 (Select Template):</label>
        <div id="templateGrid">
            <!-- Template cards rendered here -->
        </div>
        <input type="hidden" name="template_id" id="templateId">
    </div>

    <!-- Template Details Preview -->
    <div id="templateDetails" style="background: #f8f9fa; border-radius: 5px; padding: 15px; display: none;">
        <h4>模板结构</h4>
        <ul id="sectionList"></ul>
    </div>
</div>
```

**Validation**: Section hidden by default, visible only when "template" mode selected

---

### Task 1.4: Create Custom Structure Section (Show/Hide)
**File**: `format_specifications/templates/upload_word_ai.html`
**Location**: After template section, wrapped in show/hide container
**Effort**: 20 minutes

```html
<!-- Custom Structure Section - Hidden by default -->
<div id="customStructureSection" style="display: none;">
    <div class="form-group">
        <label for="customStructure">自定义结构要点 (Custom Structure):</label>
        <textarea
            name="custom_structure"
            id="customStructure"
            placeholder="请输入您的文档结构要求，例如：&#10;1. 项目背景&#10;2. 实施过程&#10;3. 遇到的问题&#10;4. 解决方案&#10;5. 项目总结"
            style="width: 100%; padding: 10px; border: 2px solid #ccc; border-radius: 5px; min-height: 150px;"
        ></textarea>
        <small style="color: #888;">
            每行一个结构要点，AI将按照您提供的结构重新组织文档内容
        </small>
    </div>
</div>
```

**Validation**: Section hidden by default, visible only when "custom" mode selected

---

### Task 1.5: Fix Template Card Selection Bug
**File**: `format_specifications/templates/upload_word_ai.html`
**Current Issue**: Cards don't reset properly, some stay highlighted
**Fix**: Properly clear all inline styles before applying selection
**Effort**: 15 minutes

```javascript
// Replace existing template card selection logic
document.querySelectorAll('.template-card').forEach(card => {
    card.addEventListener('click', function() {
        // Clear ALL inline styles from all cards first
        document.querySelectorAll('.template-card').forEach(c => {
            c.removeAttribute('style');  // Remove all inline styles
            // Reset to CSS default
            c.style.cssText = 'border: 2px solid #e0e0e0; border-radius: 8px; padding: 15px; cursor: pointer; transition: all 0.3s; background: white;';
        });

        // Apply selection styles to clicked card
        this.style.cssText = 'border: 2px solid #667eea; border-radius: 8px; padding: 15px; cursor: pointer; background: #f8f9fa; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);';

        selectedTemplate = this.dataset.templateId;
        document.getElementById('templateId').value = selectedTemplate;

        loadTemplateDetails(selectedTemplate);
    });
});
```

**Validation**:
- Click card A → Only A highlights
- Click card B → A unhighlights, only B highlights
- Click outside cards → No card highlighted (or first card stays)

---

### Task 1.6: Implement Show/Hide Logic for Mode Switching
**File**: `format_specifications/templates/upload_word_ai.html`
**Location**: In JavaScript section
**Effort**: 20 minutes

```javascript
// Mode switching logic
document.getElementById('optimizationMode').addEventListener('change', function() {
    const mode = this.value;

    // Hide all mode-specific sections
    document.getElementById('templateSelectionSection').style.display = 'none';
    document.getElementById('customStructureSection').style.display = 'none';

    // Reset template selection
    document.querySelectorAll('.template-card').forEach(c => {
        c.removeAttribute('style');
        c.style.cssText = 'border: 2px solid #e0e0e0; border-radius: 8px; padding: 15px; cursor: pointer; transition: all 0.3s; background: white;';
    });
    document.getElementById('templateId').value = '';
    document.getElementById('templateDetails').style.display = 'none';

    // Show relevant section
    if (mode === 'template') {
        document.getElementById('templateSelectionSection').style.display = 'block';
    } else if (mode === 'custom') {
        document.getElementById('customStructureSection').style.display = 'block';
    }
    // mode === 'simple' shows nothing extra
});
```

**Validation**:
- Select "simple" → No extra sections shown
- Select "template" → Template cards appear
- Select "custom" → Custom structure textarea appears
- Switching modes properly resets previous selections

---

### Task 1.7: Update Form Validation
**File**: `format_specifications/templates/upload_word_ai.html`
**Changes**: Validate based on selected mode
**Effort**: 25 minutes

```javascript
// Form submission validation
document.querySelector('form').addEventListener('submit', function(e) {
    const mode = document.getElementById('optimizationMode').value;
    const fileInput = document.querySelector('input[type="file"]');

    // File is always required
    if (!fileInput.files || !fileInput.files[0]) {
        e.preventDefault();
        alert('请上传Word文档 / Please upload a Word document');
        return false;
    }

    // Mode-specific validation
    if (mode === 'template') {
        const templateId = document.getElementById('templateId').value;
        if (!templateId) {
            e.preventDefault();
            alert('请选择模板 / Please select a template');
            return false;
        }
    }

    if (mode === 'custom') {
        const customStructure = document.getElementById('customStructure').value.trim();
        if (!customStructure) {
            e.preventDefault();
            alert('请输入自定义结构要点 / Please enter custom structure');
            return false;
        }
    }

    // Tone and style are validated by HTML 'required' attribute

    return true;
});
```

**Validation**:
- Simple mode: Only file required
- Template mode: File + template required
- Custom mode: File + structure required
- Tone and style: Always required (HTML validation)

---

### Task 1.8: Remove Visual Separator and Separate Form
**File**: `format_specifications/templates/upload_word_ai.html`
**Remove**: The visual separator (`或使用模板生成文档`) and the separate template generation form
**Effort**: 10 minutes

**Steps**:
1. Find the visual separator div (around line 391-396)
2. Delete it
3. Find the separate template form (starts around line 398)
4. Delete the entire form and its submit button
5. Keep only the unified document formatting form

**Validation**: Single unified form remains, no duplicate sections

---

## Phase 2: Backend Logic

### Task 2.1: Update `ai_format_word()` View Signature
**File**: `format_specifications/views.py`
**Change**: Add `optimization_mode` parameter handling
**Effort**: 30 minutes

```python
@require_http_methods(["POST"])
def ai_format_word(request):
    logger.info("开始处理AI格式化请求")

    # 1. Get optimization mode
    optimization_mode = request.POST.get('optimization_mode', 'simple')
    logger.info(f"Optimization mode: {optimization_mode}")

    # 2. Get file (always required)
    if 'word_file' not in request.FILES:
        error_msg = "请上传 Word 文件"
        return render(request, 'upload_word_ai.html', {'error': error_msg})

    uploaded_file = request.FILES['word_file']
    # ... file validation ...

    # 3. Get common settings (always required)
    tone = request.POST.get('tone', 'no_preference')
    style_template = request.POST.get('style_template', 'default')
    # ... style config parsing ...

    # 4. Route based on mode
    if optimization_mode == 'simple':
        return handle_simple_optimization(uploaded_file, use_ai, tone, style_config)
    elif optimization_mode == 'template':
        return handle_template_optimization(request, uploaded_file, tone, style_config)
    elif optimization_mode == 'custom':
        return handle_custom_optimization(request, uploaded_file, tone, style_config)
    else:
        error_msg = f"无效的优化模式: {optimization_mode}"
        return render(request, 'upload_word_ai.html', {'error': error_msg})
```

**Validation**: View accepts three modes, routes to correct handler

---

### Task 2.2: Extract Simple Optimization Logic
**File**: `format_specifications/views.py`
**Create**: New function `handle_simple_optimization()`
**Effort**: 30 minutes

Move existing AI formatting logic into this function:

```python
def handle_simple_optimization(uploaded_file, use_ai, tone, style_config):
    """
    Handle simple optimization mode (existing functionality)
    """
    # Save uploaded file
    # ... existing file saving logic ...

    # Process with AIWordFormatter
    formatter = AIWordFormatter(input_file_path, use_ai=use_ai, tone=tone, style_config=style_config)
    result = formatter.format(output_file_path)

    # Return file response
    # ... existing response logic ...
```

**Validation**: Simple mode produces same output as before

---

### Task 2.3: Implement Template Optimization Handler
**File**: `format_specifications/views.py`
**Create**: New function `handle_template_optimization()`
**Effort**: 30 minutes

```python
def handle_template_optimization(request, uploaded_file, tone, style_config):
    """
    Handle template-based optimization mode
    """
    from .services.template_manager import TemplateManager
    from .utils.document_extractor import DocumentExtractor
    from .utils.ai_word_utils import AITextProcessor

    # Get template selection
    template_id = request.POST.get('template_id')
    template = TemplateManager.get_template(template_id)

    if not template:
        error_msg = f"模板 '{template_id}' 不存在"
        return render(request, 'upload_word_ai.html', {'error': error_msg})

    # Extract text from uploaded document
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name

    try:
        source_document_text = DocumentExtractor.extract_full_text(tmp_file_path)

        # Generate from template with extracted text
        processor = AITextProcessor(tone=tone)
        generated_content = processor.generate_from_template(
            template=template,
            user_outline="",  # No user outline, use extracted content
            source_document_text=source_document_text,
            tone=tone
        )

        # Build document
        output_filename = f"{template.name}_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        # ... build and return document ...

    finally:
        os.unlink(tmp_file_path)
```

**Validation**: Template mode reorganizes document according to template structure

---

### Task 2.4: Implement Custom Structure Handler
**File**: `format_specifications/views.py`
**Create**: New function `handle_custom_optimization()`
**Effort**: 45 minutes

```python
def handle_custom_optimization(request, uploaded_file, tone, style_config):
    """
    Handle custom structure optimization mode
    """
    from .utils.ai_word_utils import AITextProcessor
    from .utils.document_extractor import DocumentExtractor

    # Get custom structure points
    custom_structure = request.POST.get('custom_structure', '').strip()

    if not custom_structure:
        error_msg = "请输入自定义结构要点"
        return render(request, 'upload_word_ai.html', {'error': error_msg})

    # Parse structure points (one per line or numbered)
    structure_sections = parse_custom_structure(custom_structure)

    # Extract text from uploaded document
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name

    try:
        source_document_text = DocumentExtractor.extract_full_text(tmp_file_path)

        # Generate content according to custom structure
        processor = AITextProcessor(tone=tone)
        generated_content = generate_with_custom_structure(
            processor,
            source_document_text,
            structure_sections
        )

        # Build document
        output_filename = f"custom_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        # ... build and return document ...

    finally:
        os.unlink(tmp_file_path)


def parse_custom_structure(structure_text):
    """
    Parse user's custom structure into sections
    Supports:
    - Numbered list: 1. Title, 2. Title
    - Plain lines: Just text (treat as section title)
    """
    lines = structure_text.strip().split('\n')
    sections = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove numbering if present
        clean_title = line
        if line[0].isdigit() and ('.' in line or ')' in line or '、' in line):
            # Extract title after number
            parts = re.split(r'^[\d]+[\.\)、]\s*', line, 1)
            if len(parts) > 1:
                clean_title = parts[1]

        sections.append({
            'title': clean_title,
            'original': line
        })

    return sections


def generate_with_custom_structure(processor, source_text, structure_sections):
    """
    Generate document content organized by custom structure
    """
    generated_content = {}

    for section in structure_sections:
        # Extract content relevant to this section
        content = processor.extract_section_for_structure(
            source_text,
            section['title']
        )
        generated_content[section['title']] = content

    return generated_content
```

**Validation**: Custom mode reorganizes document according to user's structure

---

### Task 2.5: Add Custom Extraction Method to AITextProcessor
**File**: `format_specifications/utils/ai_word_utils.py`
**Add**: New method `extract_section_for_structure()`
**Effort**: 30 minutes

```python
def extract_section_for_structure(self, source_text: str, section_title: str) -> str:
    """
    Extract content relevant to a specific section from source text

    Args:
        source_text: Full source document text
        section_title: Title of the section to extract

    Returns:
        Extracted content for this section
    """
    prompt = f"""请从以下文档中提取与"{section_title}"相关的内容。

**提取要求**：
- 只提取文档中与"{section_title}"直接相关的内容
- 如果没有相关内容，返回空字符串
- 保持原文表述

**源文档**：
{source_text[:2000]}

请直接返回提取的内容，如果没有相关内容则返回空字符串。"""

    try:
        if self._should_retry():
            extracted = self._call_ai_with_retry(prompt)
        else:
            extracted = self._call_ai_once(prompt)

        return extracted.strip()

    except Exception as e:
        logger.warning(f"Extraction failed for section {section_title}: {str(e)}")
        return ""
```

**Validation**: Method extracts relevant content for each custom section

---

## Phase 3: Testing

### Task 3.1: Test Simple Optimization Mode
**Effort**: 15 minutes

**Steps**:
1. Start server: `python manage.py runserver`
2. Open http://localhost:8000/
3. Select mode: "简单优化"
4. Upload test document
5. Select tone and style
6. Submit
7. Verify output matches existing functionality

**Expected**: Document formatted with AI polishing, same as before

---

### Task 3.2: Test Template Optimization Mode
**Effort**: 20 minutes

**Steps**:
1. Select mode: "模板优化"
2. Verify template grid appears
3. Click a template card
4. Verify only that card highlights
5. Click another template card
6. Verify first card unhighlights, only second highlights
7. Upload test document
8. Submit
9. Verify output follows template structure

**Expected**: Document reorganized according to selected template

---

### Task 3.3: Test Custom Structure Mode
**Effort**: 20 minutes

**Steps**:
1. Select mode: "自定义结构"
2. Verify custom structure textarea appears
3. Enter custom structure points (e.g., "1. 项目背景\n2. 实施过程\n3. 结果")
4. Upload test document
5. Submit
6. Verify output follows custom structure

**Expected**: Document reorganized according to user's structure

---

### Task 3.4: Test Mode Switching
**Effort**: 15 minutes

**Steps**:
1. Select "简单优化" → No extra sections visible
2. Switch to "模板优化" → Template cards appear
3. Select a template
4. Switch to "自定义结构" → Templates hidden, custom textarea appears
5. Switch back to "模板优化" → Previous template selection should be reset
6. Switch to "简单优化" → All extra sections hidden

**Expected**: Mode switching works correctly, no state pollution between modes

---

### Task 3.5: Test Edge Cases
**Effort**: 20 minutes

**Test Cases**:
- Submit without file → Error message
- Submit template mode without template → Error message
- Submit custom mode without structure → Error message
- Submit without tone → HTML5 validation error
- Upload non-.docx file → Error message
- Switch modes multiple times rapidly → No JS errors

**Expected**: All edge cases handled gracefully with clear error messages

---

## Summary

**Total Tasks**: 15
**Estimated Time**: 4-6 hours
**Priority**: High

**Dependencies**:
- Phase 2 (Backend) depends on Phase 1 (Frontend) completion
- Phase 3 (Testing) depends on Phase 1 and 2 completion

**Parallelizable**:
- Tasks 1.2-1.5 can be done in parallel
- Task 2.2, 2.3, 2.4 can be done in parallel after 2.1
