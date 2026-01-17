# Tasks: Add Custom Word Style Configuration

## Implementation Tasks

### 1. Backend: Add Style Configuration to AIWordFormatter
**Priority**: High
**Effort**: Medium
- [x] Add `style_config` parameter to `AIWordFormatter.__init__()` with defaults
- [x] Create style template dictionary (Academic, Business, Casual)
- [x] Update `image_width` and `image_height` to use config values
- [x] Update `_set_text_paragraph_style()` to use config fonts and sizes
- [x] Add validation for style configuration values

### 2. UI: Add Style Template Selector
**Priority**: High
**Effort**: Medium
- [x] Add template radio buttons/dropdown to `upload_word_ai.html`
- [x] Position template selector above custom controls
- [x] Add labels and descriptions for each template
- [x] Style to match existing UI design

### 3. UI: Add Custom Style Controls
**Priority**: High
**Effort**: Medium
- [x] Add dropdown for heading font type (黑体, 宋体, 楷体, 仿宋)
- [x] Add dropdown for heading font size (16, 18, 20, 22, 24 pt)
- [x] Add dropdown for body font type (宋体, 黑体, 楷体, 仿宋)
- [x] Add dropdown for body font size (10, 11, 12, 14 pt)
- [x] Add dropdown for line spacing (1.0, 1.15, 1.5, 2.0, 2.5, 3.0)
- [x] Add dropdown for image width (4, 5, 5.91, 6 inches)
- [x] Add dropdown for image height (3, 4, 4.43, 5 inches)
- [x] Group controls in collapsible or labeled section

### 4. Frontend Logic: Template Auto-fill
**Priority**: High
**Effort**: Medium
- [x] Add JavaScript to listen for template selection changes
- [x] Implement auto-fill function for each template
- [x] Allow custom controls to override template values
- [x] Add visual feedback when template is selected

### 5. View Layer: Extract Style Configuration
**Priority**: High
**Effort**: Small
- [x] Update `ai_format_word()` view to extract style config from POST
- [x] Extract template selection OR individual custom values
- [x] Merge template defaults with custom overrides
- [x] Pass merged config to `AIWordFormatter`
- [x] Add logging for style configuration

### 6. Testing & Validation
**Priority**: Medium
**Effort**: Medium
- [ ] Test each template produces correct output
- [ ] Test custom controls override template values
- [ ] Test default behavior matches existing styles
- [ ] Test all font combinations render correctly
- [ ] Test line spacing values apply correctly
- [ ] Test image dimensions apply correctly

## Dependencies & Ordering
1. Task 1 (Backend) must be completed before Task 5 (View)
2. Tasks 2, 3, 4 (UI) can be done in parallel
3. Task 5 depends on Task 1
4. Task 6 (Testing) depends on all previous tasks

## Parallelizable Work
- Task 1 (Backend) and Tasks 2, 3, 4 (UI) can be done in parallel
- Task 4 (Frontend logic) can use mock data before backend is ready
- Task 6 (Testing) can have test cases written during implementation

## Validation Checklist
- [x] All 3 templates appear and are selectable
- [x] All custom controls use dropdowns (no text input)
- [x] Selecting template auto-fills all custom controls
- [x] Custom controls can override template values
- [x] Default behavior matches existing hardcoded styles
- [x] Font options include only 黑体, 宋体, 楷体, 仿宋
- [ ] Generated documents reflect selected styles (requires manual testing)
- [ ] No errors when processing with any configuration (requires manual testing)
