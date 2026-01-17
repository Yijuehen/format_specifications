# Proposal: Add Custom Word Style Configuration

## Change ID
`add-custom-style-configuration`

## Summary
Add customizable Word document styling options to the web interface, allowing users to choose between predefined style templates (Academic, Business, Casual) and configure individual style parameters including font types, font sizes, line spacing, and image dimensions. Users select from dropdown menus rather than manually inputting values.

## Motivation
Currently, the Word formatter applies hardcoded styles (黑体/SimHei for headings at 22pt, 宋体/SimSun for body at 12pt, 1.5 line spacing, fixed image dimensions). Users need the flexibility to:
- **Match organizational standards**: Different organizations require different document styles
- **Adapt to document types**: Academic papers need different formatting than business reports
- **Personal preferences**: Users may prefer specific font combinations or spacing
- **Cultural requirements**: Different contexts may call for more formal or casual presentation

This feature enhances the tool's versatility while maintaining ease of use through dropdown selections rather than manual input.

## Proposed Solution

### 1. Style Template System
**Predefined Templates** (quick-select option):
- **Academic (学术)**: 黑体标题 18pt + 宋体正文 11pt + 2.0 line spacing + standard images
- **Business (商务)**: 黑体标题 22pt + 宋体正文 12pt + 1.5 line spacing + standard images
- **Casual (休闲)**: 微软雅黑标题 16pt + 微软雅黑正文 11pt + 1.15 line spacing + larger images

### 2. Custom Style Controls
**Individual Parameters** (advanced configuration):
- **Font Type (Heading)**: 黑体, 宋体, 楷体, 仿宋
- **Font Size (Heading)**: 16pt, 18pt, 20pt, 22pt, 24pt
- **Font Type (Body)**: 宋体, 黑体, 楷体, 仿宋
- **Font Size (Body)**: 10pt, 11pt, 12pt, 14pt
- **Line Spacing**: 1.0, 1.15, 1.5, 2.0, 2.5, 3.0
- **Image Width**: 4英寸, 5英寸, 5.91英寸(标准), 6英寸
- **Image Height**: 3英寸, 4英寸, 4.43英寸(标准), 5英寸

### 3. UI Design
- **Template Selector**: Radio buttons or dropdown at the top
- **Custom Section**: Collapsible or separate section below
- **Auto-fill**: Selecting a template auto-fills custom values (can be overridden)
- **Default Behavior**: Uses existing hardcoded styles when nothing selected

## User Impact
- **Positive**: Users can customize document output to match specific requirements
- **Breaking Changes**: None - existing behavior maintained as default
- **Migration**: Not applicable (stateless system)

## Dependencies
- Existing `AIWordFormatter` class in `word_formatter.py`
- `_set_text_paragraph_style()` method
- Image dimension properties (`image_width`, `image_height`)

## Alternatives Considered
1. **User-defined free text input**: Rejected - error-prone, validation complexity
2. **Database-stored user preferences**: Rejected - over-engineering for stateless system
3. **Only custom controls (no templates)**: Rejected - templates provide convenience

## Open Questions
None - requirements are clear based on user answers.

## Success Criteria
- [x] UI displays 3 predefined style templates (Academic, Business, Casual)
- [x] UI displays individual style controls (fonts, sizes, spacing, images)
- [x] Selecting a template auto-fills all custom controls
- [x] Users can override template values with custom selections
- [x] Default behavior matches existing hardcoded styles
- [x] All controls use dropdowns (no manual text input)
- [x] Font options include 黑体, 宋体, 楷体, 仿宋
