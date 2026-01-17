# Design: Add Custom Word Style Configuration

## Architecture Overview

This feature adds a style configuration layer to the document formatting pipeline. Users can select predefined templates or customize individual parameters through dropdown controls.

```
[UI] → [View] → [Formatter] → [Apply Styles]
  ↓       ↓          ↓
Style  Extract    Use style
Select from POST  config
```

## Component Changes

### 1. Style Configuration Data Structure

**Style Template Dictionary**:
```python
STYLE_TEMPLATES = {
    'academic': {
        'heading_font': '黑体',
        'heading_size': 18,
        'body_font': '宋体',
        'body_size': 11,
        'line_spacing': 2.0,
        'image_width': 5.91,
        'image_height': 4.43
    },
    'business': {
        'heading_font': '黑体',
        'heading_size': 22,
        'body_font': '宋体',
        'body_size': 12,
        'line_spacing': 1.5,
        'image_width': 5.91,
        'image_height': 4.43
    },
    'casual': {
        'heading_font': '微软雅黑',
        'heading_size': 16,
        'body_font': '微软雅黑',
        'body_size': 11,
        'line_spacing': 1.15,
        'image_width': 6.0,
        'image_height': 5.0
    },
    'default': {
        'heading_font': '黑体',
        'heading_size': 22,
        'body_font': '宋体',
        'body_size': 12,
        'line_spacing': 1.5,
        'image_width': 5.91,
        'image_height': 4.43
    }
}
```

### 2. AIWordFormatter (word_formatter.py)

**Modified Constructor**:
```python
def __init__(self, input_file_path, use_ai=True, tone='no_preference',
             style_config=None):
    # ... existing code ...

    # Apply style configuration
    if style_config:
        self.style_config = self._validate_style_config(style_config)
    else:
        self.style_config = STYLE_TEMPLATES['default'].copy()

    # Set image dimensions from config
    self.image_width = Inches(self.style_config['image_width'])
    self.image_height = Inches(self.style_config['image_height'])
```

**New Method**: `_validate_style_config(config)`
- Validates all config keys exist
- Validates values are in allowed ranges
- Falls back to defaults for invalid values
- Returns cleaned config dictionary

**Modified Method**: `_set_text_paragraph_style(para)`
- Uses `self.style_config['heading_font']` for headings
- Uses `self.style_config['heading_size']` for heading size
- Uses `self.style_config['body_font']` for body
- Uses `self.style_config['body_size']` for body size
- Uses `self.style_config['line_spacing']` for spacing

### 3. View Layer (views.py)

**Modified Function**: `ai_format_word(request)`
```python
# Extract style configuration
style_template = request.POST.get('style_template', 'default')

# Extract custom values (if provided)
custom_config = {
    'heading_font': request.POST.get('heading_font'),
    'heading_size': int(request.POST.get('heading_size', 0)) or None,
    'body_font': request.POST.get('body_font'),
    'body_size': int(request.POST.get('body_size', 0)) or None,
    'line_spacing': float(request.POST.get('line_spacing', 0)) or None,
    'image_width': float(request.POST.get('image_width', 0)) or None,
    'image_height': float(request.POST.get('image_height', 0)) or None,
}

# Merge template with custom overrides
style_config = STYLE_TEMPLATES[style_template].copy()
for key, value in custom_config.items():
    if value is not None:
        style_config[key] = value

# Pass to formatter
formatter = AIWordFormatter(input_file_path, use_ai=use_ai,
                           tone=tone, style_config=style_config)
```

### 4. UI Layer (upload_word_ai.html)

**Section 1: Template Selector**
```html
<div class="form-group">
    <label>快速选择样式模板 (Style Template):</label>
    <div class="template-options">
        <label class="radio-option">
            <input type="radio" name="style_template" value="default" checked>
            <span>默认样式 (Default) - 现有标准样式</span>
        </label>
        <label class="radio-option">
            <input type="radio" name="style_template" value="academic">
            <span>学术样式 (Academic) - 适合论文和报告</span>
        </label>
        <label class="radio-option">
            <input type="radio" name="style_template" value="business">
            <span>商务样式 (Business) - 适合商务文档</span>
        </label>
        <label class="radio-option">
            <input type="radio" name="style_template" value="casual">
            <span>休闲样式 (Casual) - 适合非正式文档</span>
        </label>
    </div>
</div>
```

**Section 2: Custom Controls (Collapsible)**
```html
<div class="form-group">
    <label>
        <input type="checkbox" id="show_custom_styles">
        自定义样式 (Custom Styles) - 覆盖模板设置
    </label>

    <div id="custom_styles_section" style="display: none;">
        <!-- Heading Font -->
        <div class="sub-group">
            <label for="heading_font">标题字体 (Heading Font):</label>
            <select id="heading_font" name="heading_font">
                <option value="">使用模板默认</option>
                <option value="黑体">黑体 (SimHei)</option>
                <option value="宋体">宋体 (SimSun)</option>
                <option value="楷体">楷体 (KaiTi)</option>
                <option value="仿宋">仿宋 (FangSong)</option>
            </select>
        </div>

        <!-- Heading Size -->
        <div class="sub-group">
            <label for="heading_size">标题字号 (Heading Size):</label>
            <select id="heading_size" name="heading_size">
                <option value="">使用模板默认</option>
                <option value="16">16 pt</option>
                <option value="18">18 pt</option>
                <option value="20">20 pt</option>
                <option value="22">22 pt</option>
                <option value="24">24 pt</option>
            </select>
        </div>

        <!-- Body Font -->
        <div class="sub-group">
            <label for="body_font">正文字体 (Body Font):</label>
            <select id="body_font" name="body_font">
                <option value="">使用模板默认</option>
                <option value="宋体">宋体 (SimSun)</option>
                <option value="黑体">黑体 (SimHei)</option>
                <option value="楷体">楷体 (KaiTi)</option>
                <option value="仿宋">仿宋 (FangSong)</option>
            </select>
        </div>

        <!-- Body Size -->
        <div class="sub-group">
            <label for="body_size">正文字号 (Body Size):</label>
            <select id="body_size" name="body_size">
                <option value="">使用模板默认</option>
                <option value="10">10 pt</option>
                <option value="11">11 pt</option>
                <option value="12">12 pt</option>
                <option value="14">14 pt</option>
            </select>
        </div>

        <!-- Line Spacing -->
        <div class="sub-group">
            <label for="line_spacing">行间距 (Line Spacing):</label>
            <select id="line_spacing" name="line_spacing">
                <option value="">使用模板默认</option>
                <option value="1.0">1.0 (单倍行距)</option>
                <option value="1.15">1.15 (Word默认)</option>
                <option value="1.5">1.5 (1.5倍行距)</option>
                <option value="2.0">2.0 (双倍行距)</option>
                <option value="2.5">2.5 (2.5倍行距)</option>
                <option value="3.0">3.0 (3倍行距)</option>
            </select>
        </div>

        <!-- Image Width -->
        <div class="sub-group">
            <label for="image_width">图片宽度 (Image Width):</label>
            <select id="image_width" name="image_width">
                <option value="">使用模板默认</option>
                <option value="4">4 英寸</option>
                <option value="5">5 英寸</option>
                <option value="5.91">5.91 英寸 (标准)</option>
                <option value="6">6 英寸</option>
            </select>
        </div>

        <!-- Image Height -->
        <div class="sub-group">
            <label for="image_height">图片高度 (Image Height):</label>
            <select id="image_height" name="image_height">
                <option value="">使用模板默认</option>
                <option value="3">3 英寸</option>
                <option value="4">4 英寸</option>
                <option value="4.43">4.43 英寸 (标准)</option>
                <option value="5">5 英寸</option>
            </select>
        </div>
    </div>
</div>
```

**JavaScript: Template Auto-fill Logic**
```javascript
const TEMPLATE_CONFIGS = {
    'default': {
        heading_font: '黑体',
        heading_size: '22',
        body_font: '宋体',
        body_size: '12',
        line_spacing: '1.5',
        image_width: '5.91',
        image_height: '4.43'
    },
    'academic': {
        heading_font: '黑体',
        heading_size: '18',
        body_font: '宋体',
        body_size: '11',
        line_spacing: '2.0',
        image_width: '5.91',
        image_height: '4.43'
    },
    'business': {
        heading_font: '黑体',
        heading_size: '22',
        body_font: '宋体',
        body_size: '12',
        line_spacing: '1.5',
        image_width: '5.91',
        image_height: '4.43'
    },
    'casual': {
        heading_font: '微软雅黑',
        heading_size: '16',
        body_font: '微软雅黑',
        body_size: '11',
        line_spacing: '1.15',
        image_width: '6',
        image_height: '5'
    }
};

// Auto-fill custom controls when template changes
document.querySelectorAll('input[name="style_template"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const config = TEMPLATE_CONFIGS[e.target.value];
        if (config) {
            // Only fill if user hasn't manually changed custom controls
            // (track with data-manually-changed attribute)
            for (const [key, value] of Object.entries(config)) {
                const select = document.getElementById(key);
                if (select && !select.dataset.manuallyChanged) {
                    select.value = value;
                }
            }
        }
    });
});

// Track manual changes to custom controls
document.querySelectorAll('#custom_styles_section select').forEach(select => {
    select.addEventListener('change', (e) => {
        e.target.dataset.manuallyChanged = 'true';
    });
});
```

## Data Flow

### Template Selection Flow
1. User selects "Academic" template
2. JavaScript auto-fills all custom dropdowns with Academic values
3. User submits form
4. View extracts template + any custom overrides
5. View merges template defaults with overrides
6. Formatter uses merged configuration

### Custom Override Flow
1. User selects "Academic" template
2. JavaScript auto-fills dropdowns
3. User manually changes heading size to 24pt
4. JavaScript marks heading_size as "manually changed"
5. If user changes template again, heading_size stays at 24pt
6. Form submission sends template='academic' + heading_size='24'
7. View merges: Academic defaults + heading_size=24
8. Formatter uses merged config

### Default Behavior Flow
1. User doesn't touch style section
2. Template defaults to 'default' (selected)
3. All custom controls show "使用模板默认" (empty value)
4. View uses STYLE_TEMPLATES['default']
5. Formatter applies existing hardcoded styles (黑体22/宋体12/1.5)

## Trade-offs and Decisions

### Decision 1: Template + Custom vs Just Custom
**Choice**: Hybrid approach (templates + individual controls)
**Rationale**:
- Templates provide convenience for common use cases
- Custom controls allow fine-tuning when needed
- Auto-fill bridges the gap (shows users what templates do)
- Best of both worlds

**Trade-off**: More complex UI, but worth it for usability

### Decision 2: Collapsible Custom Section vs Always Visible
**Choice**: Collapsible with checkbox
**Rationale**:
- Reduces initial visual complexity
- Advanced users can expand when needed
- Casual users can just use templates
- Progressive disclosure pattern

**Trade-off**: One more click to access features, but cleaner interface

### Decision 3: Empty Value for "Use Template Default"
**Choice**: Empty string means "use template default"
**Rationale**:
- Clear intent in UI ("使用模板默认")
- Easy to detect in backend (if not value)
- Allows selective overrides (change just font, not size)
- Aligns with form conventions

**Trade-off**: Requires special handling, but simpler for users

### Decision 4: Limited Font Options
**Choice**: Only 黑体, 宋体, 楷体, 仿宋 (+ 微软雅黑 for casual)
**Rationale**:
- These are standard Chinese fonts available everywhere
- Avoids font compatibility issues
- Meets user requirements
- Sufficient for most documents

**Trade-off**: Limited variety, but ensures consistent rendering

## Font Mapping Considerations

**Important**: python-docx requires setting both `font.name` and `rPr.rFonts`:
```python
run.font.name = '黑体'  # Western font name
run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')  # East Asian font
```

**Available Fonts**:
- 黑体 (SimHei) - Standard heading font
- 宋体 (SimSun) - Standard body font
- 楷体 (KaiTi) - Formal, calligraphic
- 仿宋 (FangSong) - Official documents
- 微软雅黑 (Microsoft YaHei) - Modern, screen-optimized

## Testing Strategy

### Unit Tests
- Test `_validate_style_config()` with valid/invalid inputs
- Test template merging logic
- Test fallback to defaults for missing values
- Test image dimension conversion

### Integration Tests
- Test full flow: UI → View → Formatter → Output
- Test each template produces correct styles
- Test custom overrides merge correctly
- Test default behavior unchanged

### Manual Testing
- Process document with each template
- Verify font, size, spacing match template
- Process document with custom overrides
- Verify overrides apply correctly
- Verify existing functionality unchanged

## Security Considerations
- All values are from predefined dropdowns (no user input)
- Server-side validation ensures values in allowed ranges
- No risk of injection or malformed data
- Fallback to defaults on any error

## Performance Impact
- Minimal: Dictionary lookups for style config
- No additional API calls or file operations
- Same processing time as existing implementation
- Style config stored in memory (negligible footprint)

## Migration Notes
- No database changes required
- No configuration changes required
- No breaking changes to existing API
- Backward compatible: defaults to existing behavior
- Feature flag not needed (can be deployed directly)
