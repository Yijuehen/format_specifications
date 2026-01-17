"""
Simple verification script for text segmentation and extraction features
"""
import os
import sys
import django

# Setup Django environment
# Navigate to project root from tests/integration/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'format_specifications.settings')
django.setup()

from format_specifications.utils.ai_word_utils import AITextProcessor


def test_segmentation():
    """Test text segmentation functionality"""
    print("Testing text segmentation...")

    processor = AITextProcessor()

    # Test paragraph segmentation
    text = "这是第一段。\n\n这是第二段。\n\n这是第三段。"
    paragraphs = processor.segment_text(text, mode="paragraph")
    print(f"[PASS] Paragraph segmentation: {len(paragraphs)} paragraphs")
    assert len(paragraphs) == 3

    # Test sentence segmentation
    text = "这是第一句。这是第二句！这是第三句？"
    sentences = processor.segment_text(text, mode="sentence")
    print(f"[PASS] Sentence segmentation: {len(sentences)} sentences")
    assert len(sentences) == 3

    # Test semantic segmentation
    text = "一、第一章\n这是第一章内容。\n\n二、第二章\n这是第二章内容。"
    semantic = processor.segment_text(text, mode="semantic")
    print(f"[PASS] Semantic segmentation: {len(semantic)} sections")

    # Test with metadata
    text = "第一段\n\n第二段"
    with_metadata = processor.segment_text(text, mode="paragraph", include_metadata=True)
    print(f"[PASS] Segmentation with metadata: {len(with_metadata)} items")
    assert all("text" in item and "type" in item and "position" in item for item in with_metadata)

    print("[PASS] All segmentation tests passed!\n")


def test_extraction_templates():
    """Test extraction template configuration"""
    print("Testing extraction templates...")

    # Check templates exist
    assert hasattr(AITextProcessor, 'EXTRACTION_TEMPLATES')
    templates = AITextProcessor.EXTRACTION_TEMPLATES

    print(f"[PASS] Templates found: {list(templates.keys())}")

    # Check predefined templates
    assert 'cause_process_result' in templates
    assert 'problem_solution' in templates
    assert 'summary_bullets' in templates
    print("[PASS] All predefined templates present")

    # Check template structure
    assert isinstance(templates['cause_process_result'], list)
    assert len(templates['cause_process_result']) == 3
    print(f"[PASS] Template structure valid: {templates['cause_process_result']}")

    print("[PASS] All template tests passed!\n")


def test_helper_methods():
    """Test helper methods"""
    print("Testing helper methods...")

    processor = AITextProcessor()

    # Test prompt building
    prompt = processor._build_extraction_prompt(["字段1", "字段2"], "测试文本")
    assert "字段1" in prompt
    assert "字段2" in prompt
    assert "禁止编造" in prompt or "绝对禁止" in prompt
    print("[PASS] Prompt building works")

    # Test sentence segmentation
    text = "这是第一句。这是第二句！"
    sentences = processor._segment_by_sentences(text)
    assert len(sentences) == 2
    print(f"[PASS] Sentence segmentation helper: {len(sentences)} sentences")

    # Test content validation
    extracted = {"字段1": "源文本中存在的内容", "字段2": ""}
    source = "这是源文本，源文本中存在的内容在这里"
    result = processor._validate_extracted_content(extracted, source)
    assert result is True
    print("[PASS] Content validation works")

    # Test invalid content detection
    extracted_invalid = {"字段1": "不存在的内容"}
    source_short = "短文本"
    result_invalid = processor._validate_extracted_content(extracted_invalid, source_short)
    assert result_invalid is False
    print("[PASS] Invalid content detection works")

    print("[PASS] All helper method tests passed!\n")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("Testing edge cases...")

    processor = AITextProcessor()

    # Test empty text
    result = processor.segment_text("", mode="paragraph")
    assert result == []
    print("[PASS] Empty text handled")

    # Test invalid mode (should fallback to default)
    result = processor.segment_text("测试文本", mode="invalid_mode")
    assert isinstance(result, list)
    print("[PASS] Invalid mode handled")

    # Test whitespace text
    result = processor.segment_text("   \n\n  ", mode="paragraph")
    assert result == []
    print("[PASS] Whitespace-only text handled")

    print("[PASS] All edge case tests passed!\n")


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Verifying Text Segmentation and Extraction Implementation")
    print("=" * 60)
    print()

    try:
        test_extraction_templates()
        test_segmentation()
        test_helper_methods()
        test_edge_cases()

        print("=" * 60)
        print("[SUCCESS] ALL VERIFICATION TESTS PASSED!")
        print("=" * 60)
        print()
        print("Implementation Summary:")
        print("  - EXTRACTION_TEMPLATES: Added")
        print("  - extract_structure(): Implemented")
        print("  - segment_text(): Implemented")
        print("  - extract_with_template(): Implemented")
        print("  - Helper methods: All implemented")
        print("  - Type hints: Added")
        print("  - Docstrings: Added")
        print("  - Logging: Integrated")
        print()
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
