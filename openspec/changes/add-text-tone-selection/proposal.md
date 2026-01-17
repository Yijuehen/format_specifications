# Proposal: Add Text Tone Selection

## Change ID
`add-text-tone-selection`

## Summary
Add a tone selection feature to the Word document formatting web interface, allowing users to choose from 7 predefined text tones (Rigorous, Cold/Sharp, Humorous, Empathetic, Direct, Inspirational, No preference) that influence AI text processing. The tone selector will be visible in the UI but only active when AI processing is enabled.

## Motivation
Currently, the AI text processing applies a neutral/polite tone to all document processing. Users need the ability to control the writing style to match different contexts:
- **Business documents** may require Rigorous or Cold/Sharp tones
- **Marketing materials** benefit from Humorous or Inspirational tones
- **Customer communications** often need Empathetic tones
- **Internal communications** work well with Direct tone

This feature enhances the tool's versatility without adding significant complexity to the architecture.

## Proposed Solution
1. **Add tone selection UI**: Dropdown/radio buttons in the web interface below the AI checkbox
2. **Extend AITextProcessor**: Add `tone` parameter to `process_text()` method
3. **Dynamic prompt generation**: Adjust AI system prompts based on selected tone
4. **Conditional activation**: Tone selector is disabled when AI checkbox is unchecked
5. **Default behavior**: "No preference" option maintains current neutral tone

## User Impact
- **Positive**: Users can tailor document tone to specific use cases
- **Breaking Changes**: None - "No preference" maintains current behavior
- **Migration**: Not applicable (stateless system)

## Dependencies
- Existing `AITextProcessor` class
- Zhipu AI GLM-4 model (supports custom system prompts)
- Current web interface (`upload_word_ai.html`)

## Alternatives Considered
1. **Configurable tones via admin panel**: Rejected - over-engineering for current needs
2. **User-defined custom tones**: Rejected - adds complexity without clear use cases
3. **Separate tone processor classes**: Rejected - unnecessary code duplication

## Open Questions
None - requirements are clear and implementation is straightforward.

## Success Criteria
- [x] UI displays all 7 tone options (including "No preference")
- [x] Tone selector is disabled when AI processing is off
- [ ] Each tone produces distinctly styled output (requires manual testing)
- [ ] "No preference" maintains current neutral behavior (requires manual testing)
- [x] Error handling gracefully falls back to neutral tone on invalid selection
