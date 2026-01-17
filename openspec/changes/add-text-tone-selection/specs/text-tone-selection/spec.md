# Spec: Text Tone Selection

## ADDED Requirements

### Requirement: Tone Selection UI
The web interface SHALL provide a tone selection control that allows users to choose from predefined text tones.

#### Scenario: User sees tone options
- **Given** a user visits the upload page
- **When** the page loads
- **Then** the following tone options SHALL be displayed:
  - Rigorous (严格) - To prove/inform
  - Cold/Sharp (冷酷/尖锐) - Authoritative
  - Humorous (幽默) - To engage
  - Empathetic (同理心) - To comfort
  - Direct (直接) - To act
  - Inspirational (鼓舞人心) - To motivate
  - No preference (无偏好) - Default neutral tone

#### Scenario: Tone selector is conditionally enabled
- **Given** a user is on the upload page
- **When** the "Enable AI" checkbox is unchecked
- **Then** the tone selector SHALL be disabled
- **And** a tooltip SHALL indicate "Tone selection requires AI processing"
- **When** the user checks "Enable AI"
- **Then** the tone selector SHALL become enabled

### Requirement: Tone-Aware AI Processing
The AITextProcessor SHALL accept a tone parameter and adjust the AI system prompt accordingly.

#### Scenario: Process text with Rigorous tone
- **Given** AI processing is enabled
- **And** "Rigorous" tone is selected
- **When** the system processes document text
- **Then** the AI system prompt SHALL emphasize formal, precise, evidence-based language
- **And** the output SHALL use structured, analytical language
- **And** the output SHALL avoid colloquialisms

#### Scenario: Process text with Humorous tone
- **Given** AI processing is enabled
- **And** "Humorous" tone is selected
- **When** the system processes document text
- **Then** the AI system prompt SHALL encourage light, engaging language
- **And** the output MAY include appropriate humor or wit
- **And** the output SHALL maintain clarity despite informal elements

#### Scenario: Process text with No preference
- **Given** AI processing is enabled
- **And** "No preference" tone is selected (default)
- **When** the system processes document text
- **Then** the AI SHALL use the current neutral/polite system prompt
- **And** the output SHALL match pre-change behavior exactly

### Requirement: Tone Parameter Validation
The system SHALL validate tone selection and gracefully handle invalid inputs.

#### Scenario: Invalid tone falls back to default
- **Given** AI processing is enabled
- **When** the system receives an invalid or missing tone parameter
- **Then** the system SHALL log a warning
- **And** the system SHALL default to "No preference" tone
- **And** processing SHALL continue without error

#### Scenario: Tone parameter passed through layers
- **Given** a user uploads a document with tone selected
- **When** the form is submitted
- **Then** the view SHALL extract the tone from POST data
- **And** the view SHALL pass tone to AIWordFormatter
- **And** AIWordFormatter SHALL pass tone to AITextProcessor
- **And** AITextProcessor SHALL apply tone-specific prompts

## MODIFIED Requirements

### Requirement: AI Text Processing (Extended)
The existing `process_text()` method SHALL accept an optional tone parameter.

#### Scenario: Backward compatibility
- **Given** existing code calls `process_text(raw_text)` without tone
- **When** the method is called
- **Then** it SHALL default to "No preference" tone
- **And** existing behavior SHALL be preserved
- **And** no breaking changes SHALL occur

## REMOVED Requirements
None - this is a pure additive feature with backward compatibility.
