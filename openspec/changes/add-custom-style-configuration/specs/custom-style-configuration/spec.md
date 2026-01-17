# Spec: Custom Word Style Configuration

## ADDED Requirements

### Requirement: Style Template Selection
The web interface SHALL provide a style template selector that allows users to choose from predefined document style templates.

#### Scenario: User sees style template options
- **Given** a user visits the upload page
- **When** the page loads
- **Then** the following template options SHALL be displayed:
  - 默认样式 (Default) - Existing standard styles
  - 学术样式 (Academic) - For papers and reports
  - 商务样式 (Business) - For business documents
  - 休闲样式 (Casual) - For informal documents

#### Scenario: User selects a template
- **Given** a user is on the upload page
- **When** the user selects the "Academic" template
- **Then** all custom style controls SHALL be auto-filled with Academic values
- **And** the user SHALL see the values reflect Academic settings (18pt heading, 11pt body, 2.0 spacing)

#### Scenario: Template styles apply to document
- **Given** a user selects "Business" template
- **And** uploads a document
- **When** the document is processed
- **Then** headings SHALL use 黑体 at 22pt
- **And** body text SHALL use 宋体 at 12pt
- **And** line spacing SHALL be 1.5
- **And** images SHALL be 5.91" x 4.43"

### Requirement: Custom Style Controls
The web interface SHALL provide individual dropdown controls for customizing document styles, allowing users to override template defaults.

#### Scenario: Custom controls use dropdowns only
- **Given** a user views the custom style section
- **When** the user expands the section
- **Then** all style controls SHALL be dropdown selects (not text input)
- **And** a "使用模板默认" (Use Template Default) option SHALL be available for each control

#### Scenario: User customizes heading font
- **Given** a user has selected a template
- **When** the user changes "Heading Font" to "楷体"
- **And** submits the form
- **Then** the processed document SHALL use 楷体 for headings
- **And** all other settings SHALL follow the selected template

#### Scenario: User customizes multiple parameters
- **Given** a user has selected "Academic" template
- **When** the user sets:
  - Heading Size to "24 pt"
  - Body Font to "黑体"
  - Line Spacing to "1.5"
- **And** submits the form
- **Then** the document SHALL use:
  - Academic template defaults for non-customized values
  - 24pt for heading size
  - 黑体 for body font
  - 1.5 for line spacing

### Requirement: Font Options
The system SHALL provide standard Chinese fonts as dropdown options for both heading and body text.

#### Scenario: Heading font options
- **Given** a user views the heading font dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 黑体 (SimHei)
  - 宋体 (SimSun)
  - 楷体 (KaiTi)
  - 仿宋 (FangSong)

#### Scenario: Body font options
- **Given** a user views the body font dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 宋体 (SimSun)
  - 黑体 (SimHei)
  - 楷体 (KaiTi)
  - 仿宋 (FangSong)

#### Scenario: Casual template uses Microsoft YaHei
- **Given** a user selects the "Casual" template
- **When** the template auto-fills custom controls
- **Then** both heading and body font SHALL be set to "微软雅黑"
- **And** the 微软雅黑 font SHALL be available in dropdowns

### Requirement: Font Size Options
The system SHALL provide common font sizes as dropdown options for both heading and body text.

#### Scenario: Heading size options
- **Given** a user views the heading size dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 16 pt
  - 18 pt
  - 20 pt
  - 22 pt
  - 24 pt

#### Scenario: Body size options
- **Given** a user views the body size dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 10 pt
  - 11 pt
  - 12 pt
  - 14 pt

### Requirement: Line Spacing Options
The system SHALL provide common line spacing values as a dropdown option.

#### Scenario: Line spacing options
- **Given** a user views the line spacing dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 1.0 (单倍行距)
  - 1.15 (Word默认)
  - 1.5 (1.5倍行距)
  - 2.0 (双倍行距)
  - 2.5 (2.5倍行距)
  - 3.0 (3倍行距)

#### Scenario: Line spacing applies correctly
- **Given** a user selects "2.0" for line spacing
- **When** the document is processed
- **Then** all body paragraphs SHALL have double line spacing
- **And** the spacing SHALL be consistent throughout the document

### Requirement: Image Size Options
The system SHALL provide common image dimensions as dropdown options for width and height.

#### Scenario: Image width options
- **Given** a user views the image width dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 4 英寸
  - 5 英寸
  - 5.91 英寸 (标准)
  - 6 英寸

#### Scenario: Image height options
- **Given** a user views the image height dropdown
- **When** the dropdown is expanded
- **Then** the following options SHALL be available:
  - 3 英寸
  - 4 英寸
  - 4.43 英寸 (标准)
  - 5 英寸

#### Scenario: Custom image sizes apply
- **Given** a user sets image width to "6" and height to "5"
- **When** a document with images is processed
- **Then** all images SHALL be resized to 6" x 5"
- **And** images SHALL maintain aspect ratio if only one dimension is specified

### Requirement: Template Auto-fill Logic
The system SHALL automatically fill custom controls when a template is selected, while preserving manual overrides.

#### Scenario: Template selection auto-fills controls
- **Given** a user has not manually changed any custom controls
- **When** the user selects "Academic" template
- **Then** all custom controls SHALL be updated to Academic values
- **And** the controls SHALL display: 黑体/18pt (heading), 宋体/11pt (body), 2.0 spacing

#### Scenario: Manual changes override template auto-fill
- **Given** a user selected "Academic" template
- **And** manually changed heading size to "24 pt"
- **When** the user switches to "Business" template
- **Then** heading size SHALL remain at "24 pt"
- **And** all other controls SHALL update to Business values

### Requirement: Default Behavior
The system SHALL maintain existing hardcoded style behavior when no template or custom values are selected.

#### Scenario: No selection uses existing defaults
- **Given** a user uploads a document without changing style settings
- **When** the document is processed
- **Then** the "Default" template SHALL be applied
- **And** styles SHALL match pre-change behavior:
  - 黑体 22pt for headings
  - 宋体 12pt for body
  - 1.5 line spacing
  - 5.91" x 4.43" images

## MODIFIED Requirements

### Requirement: AIWordFormatter Style Application (Extended)
The existing `_set_text_paragraph_style()` method SHALL use configurable style parameters instead of hardcoded values.

#### Scenario: Backward compatibility
- **Given** existing code calls `AIWordFormatter` without style_config
- **When** the formatter processes a document
- **Then** it SHALL use default style configuration
- **And** existing behavior SHALL be preserved
- **And** no breaking changes SHALL occur

#### Scenario: Style config applies to headings
- **Given** a formatter is configured with heading_font='楷体', heading_size=18
- **When** a paragraph starting with "第" is processed
- **Then** the paragraph SHALL use 楷体 font at 18pt
- **And** the paragraph SHALL be centered and bold

#### Scenario: Style config applies to body text
- **Given** a formatter is configured with body_font='黑体', body_size=14, line_spacing=2.0
- **When** a body paragraph is processed
- **Then** the paragraph SHALL use 黑体 font at 14pt
- **And** line spacing SHALL be 2.0
- **And** first line indent SHALL be applied

## REMOVED Requirements
None - this is a pure additive feature with backward compatibility.
