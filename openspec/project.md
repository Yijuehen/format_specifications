# Project Context

## Purpose
AI-Powered Word Document Formatting Tool - A Django application that provides intelligent document processing capabilities. The application accepts .docx files and applies professional formatting with optional AI enhancement using Zhipu AI's GLM-4 model for text polishing and paragraph structuring, specifically optimized for Chinese language documents.

## Tech Stack
- **Framework**: Django 6.0
- **Language**: Python 3.14
- **Database**: SQLite3 (development)
- **AI Service**: Zhipu AI (智谱AI) GLM-4 model via `zhipuai` SDK 2.1.5
- **Word Processing**:
  - `python-docx` 1.2.0 - Primary Word document manipulation
  - `spire-doc` 13.12.0 - Additional document processing capabilities
- **Key Libraries**:
  - `pillow` 12.1.0 - Image processing
  - `lxml` 6.0.2 - XML processing
  - `requests` 2.32.5 - HTTP requests
  - `python-dotenv` 1.2.1 - Environment variable management

## Project Conventions

### Code Style
- **Function-based views** in Django (not class-based views)
- **Service layer pattern**: Separate business logic from views
  - `AIWordFormatter` - Core document formatting service
  - `AITextProcessor` - AI text processing service
- **Stateless design**: No database persistence for document processing
- **Chinese-first localization**: UI labels, messages, and document content in Chinese
- **Error handling**: Comprehensive exception handling with graceful degradation

### Architecture Patterns
- **MVC Pattern**: Classic Django implementation with models, views, templates
- **Service Layer**: Business logic encapsulated in utility classes under `utils/`
- **Separation of Concerns**:
  - Views handle HTTP request/response
  - Services handle document manipulation
  - AI processing isolated with caching (30-second cache)
  - Image processing with temporary directory management

### Testing Strategy
- **Framework**: Django's built-in TestCase
- **Current Coverage**: Minimal - basic unit tests for `AIWordFormatter.analyze_document()`
- **Test Features**:
  - Temporary document creation for testing
  - Document analysis validation (word count, paragraph count, etc.)
  - Clean-up of temporary test files
- **Guideline**: Expand test coverage for new features, especially AI processing logic

### Git Workflow
- **Branch naming**: `feat(scope)`, `fix(scope)`, `refactor(scope)` prefixes
- **Commit messages**: Conventional commits with Chinese descriptions (e.g., "feat(utils): 增强AI文本处理器")
- **Main branch**: `main` (typically used for PRs)

## Domain Context

### Document Processing Pipeline
1. **Upload**: User uploads .docx file via web interface
2. **Analysis**: Document structure analyzed (paragraphs, images, tables, word count)
3. **Mode Selection**: User chooses AI-enhanced or basic formatting
4. **Processing**:
   - AI mode: Text polishing via Zhipu AI GLM-4, then standard formatting
   - Basic mode: Standard formatting only
5. **Output**: Formatted document available for download

### AI Integration Details
- **Model**: Zhipu AI GLM-4
- **Timeout**: 15 seconds per request
- **Caching**: 30-second cache to avoid redundant API calls
- **Use Cases**: Text polishing, paragraph structuring, content enhancement
- **Error Handling**: Graceful fallback when AI service unavailable

### Document Formatting Rules
- **Fonts**: 黑体 (SimHei) for headings, 宋体 (SimSun) for body text
- **Alignment**: Standardized alignment (typically justified or left-aligned)
- **Spacing**: Consistent line and paragraph spacing
- **Tables**: Standardized table formatting
- **Images**: Resizing and positioning while preserving original locations

## Important Constraints
- **AI API Rate Limits**: Zhipu API may have rate limits - implement caching and respect timeouts
- **File Size**: No explicit limits documented, but consider processing time
- **Chinese Language**: Primary focus on Chinese document formatting
- **Stateless**: No long-term storage of user documents - temporary files only
- **Permissions**: Requires proper directory access for temporary file handling

## External Dependencies

### Zhipu AI API
- **Purpose**: AI text processing and enhancement
- **Authentication**: API key via environment variables (`.env`)
- **Model**: GLM-4
- **Configuration**: Timeout (15s), cache duration (30s)

### Word Processing Libraries
- **python-docx**: Primary .docx manipulation (read, write, format)
- **spire-doc**: Advanced document operations, image handling

## File Structure Reference
```
format_specifications/
├── views.py              # Django view functions (upload, format, download)
├── utils/
│   └── word_formatter.py # AIWordFormatter, AITextProcessor services
├── templates/            # HTML templates
│   └── upload_word_ai.html
├── tests.py              # Django test cases
└── [other Django files]
```
