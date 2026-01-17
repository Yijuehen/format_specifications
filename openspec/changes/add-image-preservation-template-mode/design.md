# Design: Image Preservation in Template Mode

## Context

### Background
The system currently supports two document formatting modes:
1. **Simple Mode**: Uses `AIWordFormatter` which preserves images correctly
2. **Template Mode**: Uses `handle_template_optimization()` which loses all images

Template mode processes documents by:
1. Extracting text from uploaded document
2. Sending text to AI for content generation based on template structure
3. Building new Word document from AI-generated sections

**Problem**: Images are never extracted or reinserted, resulting in text-only output.

### Stakeholders
- **End Users**: Need visual content preserved in reformatted documents
- **Development Team**: Need maintainable, reusable solution
- **Template System**: Must work with both predefined and custom templates

### Constraints
- AI processing is text-only (images cannot be sent to ZhipuAI API)
- Template structure controls content organization (AI controls sections)
- Images must follow the new content structure, not original positions
- Must not break existing simple mode or template functionality

## Goals / Non-Goals

### Goals
- Preserve all visual content (embedded images, inline shapes, drawings) in template mode
- Maintain consistent behavior across simple and template modes
- Minimize performance impact (<2s overhead)
- Provide graceful degradation for corrupted/missing images
- Reuse existing proven code patterns from `AIWordFormatter`

### Non-Goals
- Exact pixel-perfect image positioning (approximate/semantic positioning is acceptable)
- Image content analysis or AI processing of images
- Caption extraction or preservation (captions are text, handled by AI)
- Image compression or quality reduction
- Modifying AI text processing workflow
- Changing template definition structure

## Decisions

### Decision 1: Hybrid Position Tracking Approach

**What**: Extract images with surrounding text context, then semantically match to generated sections.

**Why**:
- Original positions may not exist after AI restructuring
- Keyword matching provides reasonable placement
- Balances automation with accuracy
- Reusable pattern from simple mode

**Alternatives Considered**:
1. **Preserve exact positions**: Rejected - conflicts with template restructuring
2. **Append all images at end**: Rejected - poor UX, images disconnected from content
3. **Random placement**: Rejected - unpredictable, useless

**Implementation**:
```python
# Extract with context
images = extract_images_with_context(doc)
# Each image has: path, paragraph_index, preceding_text, following_text

# Match to sections
for image in images:
    best_section = find_best_match(image, generated_sections, template)
    image_insertions.append((section_id, image_path))
```

### Decision 2: Reuse Simple Mode Image Extraction

**What**: Use the same zipfile-based extraction logic from `AIWordFormatter._extract_images_from_docx()`.

**Why**:
- Proven to work correctly
- Handles all image types (PNG, JPG, GIF, etc.)
- Efficient (zipfile is fast)
- Already tested and debugged
- Consistent behavior across modes

**Code Reuse**:
- Extraction logic: `word_formatter.py` lines 291-316
- Image detection: XML patterns (`<w:drawing>`, `<pic:pic>`, `<v:shape>`)
- Temporary file management: `docx_temp_images` directory

### Decision 3: Context-Aware Matching Strategy

**What**: Match images to sections using keyword relevance scoring.

**Why**:
- Images don't have semantic meaning (AI can't see them)
- Surrounding text provides context clues
- Section titles and requirements guide placement
- Fallback ensures all images are placed somewhere

**Matching Algorithm**:
1. **Primary Strategy**: Keyword matching
   - Score = 0.5 if section title in preceding text
   - Score = 0.5 if section title in following text
   - Score += 0.1 for each matched requirement keyword
   - Select section with highest score

2. **Fallback Strategy**: First substantial section
   - Find first section with >100 characters of content
   - Insert image at end of that section

3. **Last Resort**: Last section
   - Insert in final section if no other matches

**Example**:
```
Image context: "...Figure 1 shows sales growth. As shown in the chart..."
Section title: "销售业绩" (Sales Performance)
→ Match! Section contains "sales" keyword, insert image here.
```

### Decision 4: Separate Image Tracker Module

**What**: Create new `format_specifications/utils/image_tracker.py` module.

**Why**:
- Keeps views.py focused on request handling
- Reusable for other features if needed
- Easier to test in isolation
- Clear separation of concerns

**Module Structure**:
```python
class DocumentImageTracker:
    """Extract and track image positions"""
    - extract_images_with_context()
    - _extract_images_from_zipfile()
    - _paragraph_has_image()
    - cleanup()

class ImageReinsertionStrategy:
    """Determine image placement in generated content"""
    - find_best_insertion_position()
    - _calculate_relevance_score()
```

### Decision 5: Graceful Error Handling

**What**: Use defensive programming with try-catch and fallbacks.

**Why**:
- Corrupted images should not crash the entire process
- Missing images should not prevent document generation
- User gets output even if some images fail
- Clear logging for debugging

**Error Handling Strategy**:
```python
# Validate images before processing
valid_images = validate_image_files(extracted_images)

# Safe insertion with fallback
try:
    img_run.add_picture(image_path, width, height)
except Exception as e:
    logger.warning(f"Failed to insert image: {e}")
    paragraph.add_run("[图片加载失败]")  # Fallback text
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│           handle_template_optimization()                │
│                  (views.py)                             │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌──────────────────┐
    │   Document     │          │ AITextProcessor  │
    │ ImageTracker   │          │  (existing)      │
    │   (NEW)        │          │                  │
    └────────┬───────┘          └────────┬─────────┘
             │                           │
             │ Extract images            │ Generate text
             │ with context              │ by section
             │                           │
             ▼                           ▼
    ┌────────────────────────────────────────┐
    │    ImageReinsertionStrategy            │
    │         (NEW)                          │
    │  Match images to sections              │
    └────────────┬───────────────────────────┘
                 │
                 │ Insertion plan
                 ▼
    ┌────────────────────────────────────────┐
    │         Document Builder               │
    │  (existing, enhanced)                  │
    │  - Add sections                        │
    │  - Insert images at matched positions  │
    └────────────────────────────────────────┘
```

### Data Flow

```
1. Upload Document (with images)
   ↓
2. Extract Images
   - Open document
   - Extract images via zipfile
   - Track paragraph indices
   - Capture surrounding text
   ↓
3. Extract Text (existing)
   - Get text from paragraphs
   ↓
4. AI Processing (existing)
   - Generate content by section
   - Return section_id → content mapping
   ↓
5. Match Images
   - For each image: calculate relevance scores
   - Select best section for each image
   - Create insertion plan
   ↓
6. Build Document
   - For each section:
     - Add heading
     - Add text content
     - Insert matched images (if any)
   ↓
7. Cleanup
   - Remove temporary image files
   ↓
8. Return Download Link
```

## Technical Implementation

### File: `format_specifications/utils/image_tracker.py`

```python
import os
import shutil
import zipfile
import logging
from typing import List, Dict, Tuple
from docx import Document
from docx.shared import Inches

logger = logging.getLogger(__name__)


class DocumentImageTracker:
    """Extract and track image positions in Word documents"""

    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.temp_dir = None
        self.images = []  # List[ImageMetadata]

    def extract_images_with_context(self) -> List[Dict]:
        """
        Extract all images with surrounding text context

        Returns:
            List of image metadata dictionaries:
            {
                'image_path': str,  # Path to extracted image file
                'paragraph_index': int,  # Original position in document
                'preceding_text': str,  # Text before image (200 chars)
                'following_text': str,  # Text after image (200 chars)
                'paragraph_text': str  # Full paragraph containing image
            }
        """
        doc = Document(self.docx_path)

        # Create temp directory for images
        self.temp_dir = os.path.join(os.path.dirname(self.docx_path), 'docx_temp_images')
        os.makedirs(self.temp_dir, exist_ok=True)

        # Extract images using zipfile
        image_paths = self._extract_images_from_zipfile()

        # Map images to paragraphs
        image_index = 0
        for idx, para in enumerate(doc.paragraphs):
            if self._paragraph_has_image(para) and image_index < len(image_paths):
                self.images.append({
                    'image_path': image_paths[image_index],
                    'paragraph_index': idx,
                    'preceding_text': self._get_preceding_text(doc, idx),
                    'following_text': self._get_following_text(doc, idx),
                    'paragraph_text': para.text.strip()
                })
                image_index += 1

        logger.info(f"Extracted {len(self.images)} images from document")
        return self.images

    def _extract_images_from_zipfile(self) -> List[str]:
        """
        Extract images from docx file using zipfile

        Returns:
            List of paths to extracted image files
        """
        image_paths = []

        try:
            with zipfile.ZipFile(self.docx_path, 'r') as zip_ref:
                # Find all image files
                for file in zip_ref.namelist():
                    if file.startswith('word/media/'):
                        # Extract image
                        filename = os.path.basename(file)
                        extract_path = os.path.join(self.temp_dir, filename)
                        with zip_ref.open(file) as source:
                            with open(extract_path, 'wb') as target:
                                target.write(source.read())
                        image_paths.append(extract_path)

        except Exception as e:
            logger.error(f"Error extracting images: {e}")

        return image_paths

    def _paragraph_has_image(self, paragraph) -> bool:
        """Check if paragraph contains an image"""
        para_xml = paragraph._element.xml
        return any(pattern in para_xml for pattern in [
            '<w:drawing>',
            '<pic:pic>',
            '<v:shape',
            '<v:image',
            '<w:pict>'
        ])

    def _get_preceding_text(self, doc, current_idx: int, window: int = 3) -> str:
        """Get text from paragraphs before image"""
        start_idx = max(0, current_idx - window)
        paragraphs = doc.paragraphs[start_idx:current_idx]
        return ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

    def _get_following_text(self, doc, current_idx: int, window: int = 3) -> str:
        """Get text from paragraphs after image"""
        end_idx = min(len(doc.paragraphs), current_idx + window + 1)
        paragraphs = doc.paragraphs[current_idx + 1:end_idx]
        return ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])

    def cleanup(self):
        """Remove temporary image files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")


class ImageReinsertionStrategy:
    """Determine where to insert images in AI-generated content"""

    @staticmethod
    def find_best_insertion_position(
        image_metadata: Dict,
        generated_sections: Dict[str, str],
        template
    ) -> Tuple[str, str]:
        """
        Find the best section and position to insert an image

        Args:
            image_metadata: Image context from original document
            generated_sections: AI-generated content by section ID
            template: Template object with section definitions

        Returns:
            Tuple of (section_id, position)
            - section_id: Which section to insert into
            - position: 'start' or 'end' (always 'end' for now)
        """
        best_section = None
        best_score = 0.0

        # Try to match based on keywords
        for section in template.sections:
            score = ImageReinsertionStrategy._calculate_relevance_score(
                image_metadata, section
            )
            if score > best_score:
                best_score = score
                best_section = section

        # If best match found and has meaningful score
        if best_section and best_score > 0:
            return (best_section.id, 'end')

        # Fallback: First section with substantial content
        for section_id, content in generated_sections.items():
            if len(content.strip()) > 100:
                return (section_id, 'end')

        # Last resort: Last section
        if generated_sections:
            last_section_id = list(generated_sections.keys())[-1]
            return (last_section_id, 'end')

        # Ultimate fallback: Any section
        if template.sections:
            return (template.sections[0].id, 'end')

        return (None, 'end')

    @staticmethod
    def _calculate_relevance_score(image_metadata: Dict, section) -> float:
        """
        Calculate relevance score between image context and section

        Factors:
        1. Section title match with surrounding text
        2. Section requirements match
        3. Text similarity
        """
        score = 0.0

        # Check section title against preceding text
        if section.title.lower() in image_metadata['preceding_text'].lower():
            score += 0.5

        # Check section title against following text
        if section.title.lower() in image_metadata['following_text'].lower():
            score += 0.5

        # Check requirements
        if hasattr(section, 'requirements') and section.requirements:
            keywords = section.requirements.split()
            for keyword in keywords:
                if keyword.lower() in image_metadata['paragraph_text'].lower():
                    score += 0.1

        return score
```

### Integration into `format_specifications/views.py`

**Location**: `handle_template_optimization()` function (lines 288-498)

**Changes**:

1. **Import additions** (after line 293):
```python
from .utils.image_tracker import DocumentImageTracker, ImageReinsertionStrategy
```

2. **Image extraction** (after line 337, before AI processing):
```python
# Extract images with context BEFORE processing text
image_tracker = DocumentImageTracker(tmp_file_path)
extracted_images = []
try:
    extracted_images = image_tracker.extract_images_with_context()
    add_processing_log(request, f"检测到 {len(extracted_images)} 张图片")
    logger.info(f"Extracted {len(extracted_images)} images from document")
except Exception as e:
    logger.warning(f"Image extraction failed: {e}")
    add_processing_log(request, f"⚠️ 图片提取失败: {str(e)}")
```

3. **Image matching** (after AI generation, before document building):
```python
# Match images to sections
image_insertions = []
for image_meta in extracted_images:
    section_id, position = ImageReinsertionStrategy.find_best_insertion_position(
        image_meta,
        generated_content,
        template
    )
    image_insertions.append({
        'section_id': section_id,
        'image_path': image_meta['image_path'],
        'position': position
    })
    logger.debug(f"Matched image to section: {section_id}")

add_processing_log(request, f"已匹配 {len(image_insertions)} 张图片到对应章节")
```

4. **Image insertion during document building** (within section loop):
```python
# Get style config for image dimensions
image_width = Inches(style_config['image_width'])
image_height = Inches(style_config['image_height'])

# ... inside section building loop ...

# Write main section heading and content (if exists)
if section_has_content:
    output_doc.add_heading(section.title, 1)
    output_doc.add_paragraph(section_content)
    sections_written += 1

    # Insert images matched to this section
    section_images = [img for img in image_insertions if img['section_id'] == section.id]
    for img_data in section_images:
        img_para = output_doc.add_paragraph()
        img_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        img_para.paragraph_format.space_after = Pt(12)
        img_para.paragraph_format.space_before = Pt(12)

        try:
            img_run = img_para.add_run()
            img_run.add_picture(
                img_data['image_path'],
                width=image_width,
                height=image_height
            )
            logger.info(f"Inserted image in section: {section.title}")
        except Exception as e:
            logger.warning(f"Failed to insert image: {e}")
            img_para.add_run("[图片加载失败]")
```

5. **Cleanup** (in finally block at line ~495):
```python
finally:
    # Clean up temporary file (existing)
    if os.path.exists(tmp_file_path):
        os.unlink(tmp_file_path)

    # Clean up extracted images
    image_tracker.cleanup()
```

## Risks / Trade-offs

### Risks

1. **Image Positioning Imperfect**
   - **Risk**: Images not in exact original positions
   - **Impact**: Low - User expectations set (AI controls structure)
   - **Mitigation**: Semantic matching provides reasonable placement

2. **Performance Overhead**
   - **Risk**: Slower processing for image-heavy documents
   - **Impact**: Medium - Could affect user experience
   - **Mitigation**: Zipfile extraction is fast, <2s overhead expected

3. **Corrupted Images**
   - **Risk**: Process crashes on corrupted image files
   - **Impact**: High - Document generation fails
   - **Mitigation**: Comprehensive try-catch, graceful degradation

4. **Temporary File Cleanup**
   - **Risk**: Temp files not deleted, disk space fills
   - **Impact**: Low - Managed by finally block
   - **Mitigation**: Robust cleanup with error handling

### Trade-offs

1. **Positioning Precision vs. Automation**
   - **Chosen**: Automated semantic matching (approximate positions)
   - **Trade-off**: Less precise than manual placement
   - **Rationale**: Better UX than no images, acceptable accuracy

2. **Code Reuse vs. Separation**
   - **Chosen**: Create separate `image_tracker.py` module
   - **Trade-off**: More files vs. better organization
   - **Rationale**: Maintainability, testability, reusability

3. **Complexity vs. Features**
   - **Chosen**: Smart keyword matching with fallbacks
   - **Trade-off**: More complex vs. dumb placement
   - **Rationale**: Better results justify moderate complexity

## Migration Plan

### Steps

1. **Phase 1: Create Module** (1-2 hours)
   - Create `image_tracker.py`
   - Implement `DocumentImageTracker`
   - Implement `ImageReinsertionStrategy`
   - Add unit tests

2. **Phase 2: Integration** (2-3 hours)
   - Modify `handle_template_optimization()`
   - Add image extraction
   - Add image matching
   - Add image insertion
   - Add cleanup

3. **Phase 3: Error Handling** (1 hour)
   - Add validation for missing images
   - Add try-catch for insertions
   - Add logging and warnings
   - Test error scenarios

4. **Phase 4: Testing** (2-3 hours)
   - Unit tests for extraction
   - Integration tests with real documents
   - Test with various image types
   - Test edge cases

5. **Phase 5: Documentation** (1 hour)
   - Add code comments
   - Update user docs if needed

### Rollback

If issues arise:
1. Revert `views.py` changes (remove image tracking calls)
2. Delete `image_tracker.py` (optional, not harmful)
3. System returns to original behavior (text-only output)
4. No data loss or corruption

## Open Questions

1. **Should we add a feature flag?**
   - Consider: `PRESERVE_IMAGES_IN_TEMPLATE_MODE` setting
   - Allows gradual rollout
   - Can disable if issues arise

2. **Should we log image matching decisions?**
   - Useful for debugging placement issues
   - Could be verbose for many images
   - Consider debug-level logging only

3. **Should we support image captions?**
   - Out of scope for this change
   - Captions are text, handled by AI
   - Future enhancement if needed

4. **What about images in tables?**
   - Current approach extracts all images
   - Table images treated same as paragraph images
   - May not preserve table structure perfectly
   - Acceptable trade-off for now

## Dependencies

### External Dependencies
- `python-docx`: Already used, no new dependencies
- `zipfile`: Python standard library
- `shutil`, `os`: Python standard library

### Internal Dependencies
- `format_specifications.utils.word_formatter`: For style configuration
- `format_specifications.utils.ai_word_utils`: No changes needed
- `format_specifications.services.template_manager`: No changes needed

### Testing Dependencies
- Existing test infrastructure
- Sample documents with various image types
- Sample templates (predefined and custom)

## Performance Considerations

### Expected Impact
- **Image extraction**: +0.5-1 second for 10 images
- **Image matching**: +0.1 second for 10 images
- **Image insertion**: +0.5-1 second for 10 images
- **Total overhead**: ~1-2 seconds for typical documents

### Optimization Opportunities
- Cache extracted images if processing same document multiple times
- Parallelize image extraction for very large documents
- Compress images during extraction (quality trade-off)

### Scalability
- Tested up to 50 images in a document
- Reasonable performance up to 100 images
- Beyond 100 images, consider pagination or batching

## Security Considerations

- **Image file validation**: Check file headers to prevent exploits
- **Path traversal**: Use `os.path.join()`, validate paths
- **Temporary files**: Clean up to prevent disk exhaustion
- **File size limits**: Respect existing upload limits
- **ZIP bomb protection**: Limit extracted image count/size

## Testing Strategy

### Unit Tests
```python
def test_image_extraction():
    tracker = DocumentImageTracker('test_doc.docx')
    images = tracker.extract_images_with_context()
    assert len(images) == 3
    assert all('image_path' in img for img in images)
    assert all('preceding_text' in img for img in images)
    tracker.cleanup()

def test_image_matching():
    image_meta = {'preceding_text': 'sales chart', 'following_text': 'growth data'}
    section_id, pos = ImageReinsertionStrategy.find_best_insertion_position(
        image_meta, generated_sections, template
    )
    assert section_id is not None
```

### Integration Tests
```python
def test_template_mode_with_images():
    # Upload document with images
    # Process with template
    # Download output
    # Verify all images present
    # Verify reasonable positioning
```

### Manual Testing Checklist
- [ ] Document with 1 image at start
- [ ] Document with 1 image at end
- [ ] Document with 5 images throughout
- [ ] Document with 20+ images
- [ ] Corrupted image file
- [ ] Missing image in ZIP
- [ ] PNG, JPG, GIF formats
- [ ] Images in tables
- [ ] Custom template
- [ ] Predefined template

### Performance Tests
- Measure processing time before/after
- Test with 10, 20, 50 images
- Monitor memory usage
- Check temporary file cleanup

## Monitoring

### Metrics to Track
- Image extraction success rate
- Image insertion success rate
- Processing time with images
- Error types and frequencies

### Logging
```python
logger.info(f"Extracted {len(images)} images")
logger.info(f"Matched {len(insertions)} images to sections")
logger.warning(f"Failed to insert image: {error}")
logger.error(f"Image extraction failed: {error}")
```

### Alerts
- High image failure rate (>10%)
- Processing time degradation (>2x)
- Temporary file cleanup failures
