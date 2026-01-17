# UI Specification: Unified Optimization Modes

## ADDED Requirements

### Requirement: Mode Selector Dropdown

The homepage MUST provide a dropdown selector that allows users to choose between three document optimization modes: simple, template, and custom structure.

#### Scenario: User selects simple optimization mode
- Given the user is on the homepage (`http://localhost:8000/`)
- When the user views the form
- Then a dropdown with id `optimizationMode` MUST be visible
- And the dropdown MUST have three options:
  - `simple`: "简单优化 - 基础格式化和AI润色"
  - `template`: "模板优化 - 按预设模板重新组织内容"
  - `custom`: "自定义结构 - 按自定义结构点组织"
- And the dropdown MUST have the name attribute `optimization_mode`
- And the dropdown MUST be marked as `required`

#### Scenario: User selects template optimization mode
- Given the user is on the homepage
- When the user selects "模板优化" from the optimization mode dropdown
- Then the template selection section MUST become visible
- And the custom structure section MUST be hidden
- And the document upload field MUST remain visible
- And the tone selector MUST remain visible
- And the style settings MUST remain visible

#### Scenario: User selects custom structure mode
- Given the user is on the homepage
- When the user selects "自定义结构" from the optimization mode dropdown
- Then the custom structure textarea MUST become visible
- And the template selection section MUST be hidden
- And the document upload field MUST remain visible
- And the tone selector MUST remain visible
- And the style settings MUST remain visible

### Requirement: Always-Visible Common Settings

The homepage MUST display tone and style settings at all times, regardless of the selected optimization mode.

#### Scenario: Common settings visible in simple mode
- Given the user has selected "简单优化" mode
- When the user views the form
- Then the tone selector (id: `tone`) MUST be visible
- And the tone selector MUST be marked as `required`
- And the style template selector (id: `styleTemplate`) MUST be visible
- And the style template selector MUST be marked as `required`
- And all style configuration options (font, size, spacing, etc.) MUST be visible

#### Scenario: Common settings visible in template mode
- Given the user has selected "模板优化" mode
- When the user views the form
- Then the tone selector MUST be visible and required
- And the style template selector MUST be visible and required
- And the template grid MUST be visible below the common settings

#### Scenario: Common settings visible in custom mode
- Given the user has selected "自定义结构" mode
- When the user views the form
- Then the tone selector MUST be visible and required
- And the style template selector MUST be visible and required
- And the custom structure textarea MUST be visible below the common settings

### Requirement: Show/Hide Mode-Specific Sections

The homepage MUST show or hide mode-specific sections based on the selected optimization mode.

#### Scenario: Template selection section show/hide
- Given the user is on the homepage
- When the user selects "模板优化" mode
- Then the element with id `templateSelectionSection` MUST have `display: block`
- When the user switches to "简单优化" mode
- Then the element with id `templateSelectionSection` MUST have `display: none`
- When the user switches to "自定义结构" mode
- Then the element with id `templateSelectionSection` MUST have `display: none`

#### Scenario: Custom structure section show/hide
- Given the user is on the homepage
- When the user selects "自定义结构" mode
- Then the element with id `customStructureSection` MUST have `display: block`
- When the user switches to "简单优化" mode
- Then the element with id `customStructureSection` MUST have `display: none`
- When the user switches to "模板优化" mode
- Then the element with id `customStructureSection` MUST have `display: none`

#### Scenario: Mode switching resets previous selections
- Given the user has selected "模板优化" mode
- And the user has clicked template card "年度工作总结"
- When the user switches to "自定义结构" mode
- Then the template card selection MUST be cleared
- And the hidden input `templateId` MUST be empty
- When the user switches back to "模板优化" mode
- Then no template card MUST be selected
- And the template details preview MUST be hidden

### Requirement: Template Card Selection Without State Pollution

Template cards MUST properly highlight only the selected card, with no residual highlighting from previous selections.

#### Scenario: Single card highlights on click
- Given the user is in "模板优化" mode
- And the template grid displays 10 template cards
- When the user clicks template card "年度工作总结"
- Then ONLY the "年度工作总结" card MUST have a blue border (#667eea)
- And ONLY the "年度工作总结" card MUST have a light gray background (#f8f9fa)
- And ONLY the "年度工作总结" card MUST have a box shadow
- And all other 9 cards MUST have the default gray border (#e0e0e0)
- And all other 9 cards MUST have a white background
- And all other 9 cards MUST NOT have a box shadow

#### Scenario: Switching selected card
- Given the user has clicked "年度工作总结" card (it is highlighted)
- When the user clicks "项目报告" card
- Then "年度工作总结" card MUST lose its highlighting (return to default)
- And ONLY "项目报告" card MUST be highlighted
- And the hidden input `templateId` MUST contain "项目报告"

#### Scenario: Clicking outside cards does not highlight
- Given the user is in "模板优化" mode
- And no template card is currently selected
- When the user clicks outside the template grid
- Then no template card MUST be highlighted
- And the hidden input `templateId` MUST be empty

## MODIFIED Requirements

### Requirement: Unified Form Structure

The homepage MUST use a single unified form instead of two separate forms for document optimization.

#### Scenario: Single submit button for all modes
- Given the user is on the homepage
- When the user views the form
- Then there MUST be exactly ONE form element
- And the form MUST submit to `/ai_format/` via POST
- And there MUST be exactly ONE submit button
- And the submit button text MUST be "开始优化文档" or equivalent
- And the visual separator "或使用模板生成文档" MUST NOT exist
- And the separate template generation form MUST NOT exist

#### Scenario: Form submission includes mode parameter
- Given the user has filled out the form
- And the user has selected an optimization mode
- When the user clicks the submit button
- Then the form MUST include a POST parameter `optimization_mode` with the selected mode value
- And the form MUST include the uploaded word file
- And the form MUST include the tone selection
- And the form MUST include the style template selection
- And if mode is "template", the form MUST include `template_id`
- And if mode is "custom", the form MUST include `custom_structure` text

#### Scenario: Mode-specific validation before submission
- Given the user has selected "模板优化" mode
- And the user has NOT selected a template
- When the user clicks the submit button
- Then the form MUST prevent submission
- And an error message MUST display: "请选择模板 / Please select a template"
- Given the user has selected "自定义结构" mode
- And the user has NOT entered custom structure text
- When the user clicks the submit button
- Then the form MUST prevent submission
- And an error message MUST display: "请输入自定义结构要点 / Please enter custom structure"

### Requirement: Custom Structure Input

The homepage MUST provide a textarea for users to input their custom structure when in custom structure mode.

#### Scenario: Custom structure textarea appears in custom mode
- Given the user has selected "自定义结构" mode
- When the user views the form
- Then a textarea with id `customStructure` MUST be visible
- And the textarea MUST have the name attribute `custom_structure`
- And the textarea MUST have a placeholder with example structure
- And the textarea MUST recommend one structure point per line
- And the textarea MUST have a minimum height of 150px
- And a helper text MUST explain: "每行一个结构要点，AI将按照您提供的结构重新组织文档内容"

#### Scenario: Custom structure validation
- Given the user has selected "自定义结构" mode
- And the user has entered only whitespace in the custom structure textarea
- When the user attempts to submit the form
- Then the form MUST prevent submission
- And an error message MUST indicate custom structure is required
