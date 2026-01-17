# Spec: Custom Structure Polishing

## Requirements

### Requirement: Custom structure mode must polish extracted content

In the custom structure optimization mode, after extracting content relevant to each user-defined section, the system MUST apply AI text polishing to improve wording, structure, and readability.

**Rationale**: Users expect consistent AI enhancement across all optimization modes. The custom structure mode currently only extracts content without polishing, resulting in inferior output compared to simple and template modes.

**Priority**: High

#### Scenario: Custom structure with short content

**Given** a user uploads a document with basic bullet points
**And** the user selects "自定义结构" (Custom Structure) optimization mode
**And** the user enters custom structure: "工作内容\n遇到的问题\n解决方案"
**When** the system processes the document
**Then** each section should contain polished, well-written content
**And** the content should NOT be raw extraction from the source
**And** the logs should show: "Polishing content for section: [section name]"

#### Scenario: Custom structure respects tone settings

**Given** a user uploads a document
**And** the user selects "自定义结构" optimization mode
**And** the user selects "正式" (Formal) tone
**And** the user enters custom structure points
**When** the system processes the document
**Then** the polished content should use formal language
**And** the wording should be appropriate for formal documents
**And** the tone should match the selected setting

#### Scenario: Custom structure handles empty sections gracefully

**Given** a user uploads a document
**And** the user selects "自定义结构" optimization mode
**And** the user enters custom structure with sections that don't exist in the source
**When** the system processes the document
**Then** sections with no relevant content should be skipped entirely (no title, no content)
**And** the logs should show: "Section [name] has no meaningful content, skipping polishing"
**And** no polishing AI call should be made for empty sections

#### Scenario: Custom structure performance is acceptable

**Given** a user uploads a document with 500 characters
**And** the user selects "自定义结构" optimization mode
**And** the user enters custom structure with 5 sections
**When** the system processes the document
**Then** processing should complete in less than 2 minutes
**And** there should be exactly 10 AI calls (5 for extraction + 5 for polishing)
**And** the logs should show each extraction and polishing call

---

### Requirement: Polishing quality must match other optimization modes

The AI polishing applied in custom structure mode must produce content of similar quality to the simple and template optimization modes.

**Rationale**: Inconsistent quality across modes confuses users and makes custom structure mode seem inferior or broken.

**Priority**: High

#### Scenario: Compare simple mode vs custom structure mode

**Given** a user uploads the same document twice
**And** first time, the user selects "简单优化" mode
**And** second time, the user selects "自定义结构" mode with similar structure to simple output
**When** comparing the two output documents
**Then** both should have improved wording
**And** both should have better structure
**And** the quality difference should be minimal
**And** both should respect the same tone/style settings

#### Scenario: Polishing preserves section meaning

**Given** a user uploads a document about a software project
**And** the user selects "自定义结构" optimization mode
**And** the user enters structure: "技术栈\n开发过程\n测试结果"
**When** the system extracts and polishes content for "技术栈" section
**Then** the polished content must still describe the technology stack
**And** key technical terms must be preserved
**And** the core meaning must not be altered
**And** only the wording and structure should be improved

---

## Related Requirements

- **Text Segmentation Spec**: Defines how content is extracted and organized into sections
- **Simple Optimization Spec**: Defines baseline AI polishing behavior
- **Template Optimization Spec**: Shows how template mode polishes extracted content
