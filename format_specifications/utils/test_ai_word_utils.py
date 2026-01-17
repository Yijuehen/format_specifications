"""
Unit tests for AITextProcessor text segmentation and structured extraction features
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from format_specifications.utils.ai_word_utils import AITextProcessor


@pytest.fixture
def processor():
    """Create an AITextProcessor instance for testing"""
    return AITextProcessor(tone='no_preference')


class TestExtractionTemplates:
    """Test EXTRACTION_TEMPLATES configuration"""

    def test_templates_exist(self):
        """Test that EXTRACTION_TEMPLATES is defined"""
        assert hasattr(AITextProcessor, 'EXTRACTION_TEMPLATES')
        templates = AITextProcessor.EXTRACTION_TEMPLATES
        assert isinstance(templates, dict)

    def test_predefined_templates(self):
        """Test that all predefined templates exist"""
        templates = AITextProcessor.EXTRACTION_TEMPLATES
        assert 'cause_process_result' in templates
        assert 'problem_solution' in templates
        assert 'summary_bullets' in templates

    def test_template_structure(self):
        """Test that templates have correct structure"""
        templates = AITextProcessor.EXTRACTION_TEMPLATES
        assert isinstance(templates['cause_process_result'], list)
        assert len(templates['cause_process_result']) == 3
        assert '原因' in templates['cause_process_result']
        assert '过程' in templates['cause_process_result']
        assert '结果' in templates['cause_process_result']


class TestSegmentationPatterns:
    """Test segmentation patterns and regex"""

    def test_sentence_pattern_exists(self):
        """Test that SENTENCE_PATTERN is defined"""
        assert hasattr(AITextProcessor, 'SENTENCE_PATTERN')
        import re
        assert isinstance(AITextProcessor.SENTENCE_PATTERN, re.Pattern)

    def test_heading_patterns_exist(self):
        """Test that HEADING_PATTERNS is defined"""
        assert hasattr(AITextProcessor, 'HEADING_PATTERNS')
        assert isinstance(AITextProcessor.HEADING_PATTERNS, list)

    def test_compiled_heading_patterns_exist(self):
        """Test that COMPILED_HEADING_PATTERNS is defined"""
        assert hasattr(AITextProcessor, 'COMPILED_HEADING_PATTERNS')
        import re
        assert all(isinstance(p, re.Pattern) for p in AITextProcessor.COMPILED_HEADING_PATTERNS)


class TestExtractStructure:
    """Test extract_structure method"""

    def test_empty_text(self, processor):
        """Test extraction with empty text"""
        result = processor.extract_structure("", "cause_process_result")
        assert result == {}

    def test_whitespace_only_text(self, processor):
        """Test extraction with whitespace-only text"""
        result = processor.extract_structure("   \n\t  ", "cause_process_result")
        assert result == {}

    def test_invalid_template_name(self, processor):
        """Test extraction with invalid template name"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            mock_ai.return_value = '{"原因": "测试原因", "过程": "测试过程", "结果": "测试结果"}'

            result = processor.extract_structure("测试文本", "invalid_template")
            assert result == {}
            # Should use default template
            mock_ai.assert_not_called()  # Returns {} before AI call due to validation

    def test_custom_template_list(self, processor):
        """Test extraction with custom field list"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            mock_ai.return_value = '{"字段1": "内容1", "字段2": "内容2"}'

            result = processor.extract_structure("测试文本", ["字段1", "字段2"])
            assert result == {"字段1": "内容1", "字段2": "内容2"}
            mock_ai.assert_called_once()

    def test_text_too_long(self, processor):
        """Test extraction with text exceeding max length"""
        long_text = "a" * 1001  # max_text_length is 1000
        result = processor.extract_structure(long_text, "cause_process_result")
        assert result == {"原因": "", "过程": "", "结果": ""}

    @patch('format_specifications.utils.ai_word_utils.ZhipuAI')
    def test_successful_extraction(self, mock_zhipu, processor):
        """Test successful extraction with mocked AI"""
        # Mock the AI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"原因": "系统故障", "过程": "修复代码", "结果": "系统恢复"}'

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_zhipu.return_value = mock_client

        # Re-create processor to use mocked client
        processor = AITextProcessor()

        result = processor.extract_structure("系统出现故障，工程师修复了代码，系统恢复正常", "cause_process_result")
        assert result["原因"] == "系统故障"
        assert result["过程"] == "修复代码"
        assert result["结果"] == "系统恢复"

    def test_json_parsing_fallback(self, processor):
        """Test JSON parsing with extra text around JSON"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            # AI returns text with markdown code block
            mock_ai.return_value = '''
这是提取的结果：

```json
{"原因": "测试原因", "过程": "测试过程", "结果": "测试结果"}
```
            '''

            result = processor.extract_structure("测试文本", "cause_process_result")
            assert result["原因"] == "测试原因"
            assert result["过程"] == "测试过程"
            assert result["结果"] == "测试结果"

    def test_ai_api_failure(self, processor):
        """Test extraction when AI API fails"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            mock_ai.side_effect = Exception("API Error")

            result = processor.extract_structure("测试文本", "cause_process_result")
            assert result == {"原因": "", "过程": "", "结果": ""}

    def test_validation_detects_fabricated_content(self, processor, caplog):
        """Test that validation detects AI-fabricated content"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            # AI returns content that doesn't exist in source
            mock_ai.return_value = '{"原因": "源文本中没有的原因", "过程": "测试过程", "结果": "测试结果"}'

            result = processor.extract_structure("源文本内容", "cause_process_result")

            # Should still return result but log warning
            assert "原因" in result
            # Check that warning was logged
            assert any("提取验证失败" in record.message for record in caplog.records)

    def test_empty_fields_valid(self, processor):
        """Test that empty fields are valid (content doesn't exist in source)"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            # AI returns empty fields
            mock_ai.return_value = '{"原因": "", "过程": "", "结果": ""}'

            result = processor.extract_structure("测试文本", "cause_process_result")
            assert result == {"原因": "", "过程": "", "结果": ""}


class TestExtractWithTemplate:
    """Test extract_with_template convenience method"""

    def test_is_alias(self, processor):
        """Test that extract_with_template is an alias for extract_structure"""
        with patch.object(processor, 'extract_structure') as mock_extract:
            mock_extract.return_value = {"field1": "value1"}

            result = processor.extract_with_template("测试文本", ["field1", "field2"])
            mock_extract.assert_called_once_with("测试文本", ["field1", "field2"])


class TestSegmentText:
    """Test segment_text method"""

    def test_empty_text(self, processor):
        """Test segmentation with empty text"""
        result = processor.segment_text("", "paragraph")
        assert result == []

    def test_whitespace_only_text(self, processor):
        """Test segmentation with whitespace-only text"""
        result = processor.segment_text("   \n\n  ", "paragraph")
        assert result == []

    def test_invalid_mode(self, processor):
        """Test segmentation with invalid mode"""
        result = processor.segment_text("测试文本", "invalid_mode")
        # Should use default mode 'paragraph'
        assert isinstance(result, list)

    def test_paragraph_mode(self, processor):
        """Test paragraph segmentation mode"""
        text = "第一段内容\n\n第二段内容\n\n\n第三段内容"
        result = processor.segment_text(text, "paragraph")
        assert len(result) == 3
        assert result[0] == "第一段内容"
        assert result[1] == "第二段内容"
        assert result[2] == "第三段内容"

    def test_sentence_mode_chinese(self, processor):
        """Test sentence segmentation with Chinese punctuation"""
        text = "这是第一句。这是第二句！这是第三句？还有最后一句。"
        result = processor.segment_text(text, "sentence")
        assert len(result) == 4
        assert "这是第一句" in result[0]
        assert "这是第二句" in result[1]
        assert "这是第三句" in result[2]
        assert "还有最后一句" in result[3]

    def test_sentence_mode_english(self, processor):
        """Test sentence segmentation with English punctuation"""
        text = "First sentence. Second sentence! Third sentence? Final sentence."
        result = processor.segment_text(text, "sentence")
        assert len(result) == 4
        assert "First sentence" in result[0]
        assert "Second sentence" in result[1]
        assert "Third sentence" in result[2]
        assert "Final sentence" in result[3]

    def test_semantic_mode_with_headings(self, processor):
        """Test semantic segmentation with headings"""
        text = """一、第一章内容
这是第一章的详细内容。

二、第二章内容
这是第二章的详细内容。"""

        result = processor.segment_text(text, "semantic")
        assert len(result) >= 1
        # Should detect the Chinese numeral headings

    def test_semantic_mode_with_numbered_headings(self, processor):
        """Test semantic segmentation with numbered headings"""
        text = """1. 第一部分
内容在这里

2. 第二部分
更多内容"""

        result = processor.segment_text(text, "semantic")
        assert len(result) >= 1
        # Should detect the numbered headings

    def test_metadata_included(self, processor):
        """Test segmentation with metadata"""
        text = "第一段\n\n第二段\n\n第三段"
        result = processor.segment_text(text, "paragraph", include_metadata=True)

        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
        assert all("text" in item and "type" in item and "position" in item for item in result)
        assert result[0]["type"] == "paragraph"
        assert result[0]["position"] == 0

    def test_metadata_not_included(self, processor):
        """Test segmentation without metadata"""
        text = "第一段\n\n第二段"
        result = processor.segment_text(text, "paragraph", include_metadata=False)

        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)


class TestHelperMethods:
    """Test helper methods"""

    def test_build_extraction_prompt(self, processor):
        """Test prompt building"""
        prompt = processor._build_extraction_prompt(["字段1", "字段2"], "测试文本")
        assert "字段1" in prompt
        assert "字段2" in prompt
        assert "测试文本" in prompt
        assert "禁止编造" in prompt or "绝对禁止" in prompt

    def test_parse_extraction_response_valid_json(self, processor):
        """Test parsing valid JSON response"""
        response = '{"字段1": "内容1", "字段2": "内容2"}'
        result = processor._parse_extraction_response(response, ["字段1", "字段2"])
        assert result == {"字段1": "内容1", "字段2": "内容2"}

    def test_parse_extraction_response_invalid_json(self, processor):
        """Test parsing invalid JSON response"""
        response = "这不是JSON格式"
        result = processor._parse_extraction_response(response, ["字段1", "字段2"])
        # Should return empty dict for all fields
        assert result == {"字段1": "", "字段2": ""}

    def test_parse_extraction_response_json_in_text(self, processor):
        """Test parsing JSON embedded in text"""
        response = "这是结果：\n{'字段1': '内容1', '字段2': '内容2'}\n完成"
        result = processor._parse_extraction_response(response, ["字段1", "字段2"])
        # Should extract JSON from text
        assert "字段1" in result
        assert "字段2" in result

    def test_validate_extracted_content_all_valid(self, processor):
        """Test validation with all valid content"""
        extracted = {"字段1": "源文本中存在的内容", "字段2": ""}
        source = "这是源文本，源文本中存在的内容在这里"
        result = processor._validate_extracted_content(extracted, source)
        assert result is True

    def test_validate_extracted_content_invalid_content(self, processor, caplog):
        """Test validation detects invalid content"""
        extracted = {"字段1": "源文本中不存在的内容"}
        source = "这是源文本"
        result = processor._validate_extracted_content(extracted, source)
        assert result is False

    def test_segment_by_sentences_chinese(self, processor):
        """Test sentence segmentation helper"""
        text = "这是第一句。这是第二句！这是第三句？"
        result = processor._segment_by_sentences(text)
        assert len(result) == 3

    def test_segment_by_semantic_headings(self, processor):
        """Test semantic segmentation helper"""
        text = "一、第一部分\n内容1\n\n二、第二部分\n内容2"
        result = processor._segment_by_semantic(text)
        assert len(result) >= 1


class TestIntegration:
    """Integration tests"""

    def test_extract_and_segment_workflow(self, processor):
        """Test combining extraction and segmentation"""
        text = "这是第一段。\n\n这是第二段，包含重要信息。"

        # First segment
        segments = processor.segment_text(text, "paragraph")
        assert len(segments) == 2

        # Then extract from segments
        with patch.object(processor, '_call_ai_once') as mock_ai:
            mock_ai.return_value = '{"字段1": "提取的内容"}'
            result = processor.extract_structure(segments[0], ["字段1"])
            assert result["字段1"] == "提取的内容"

    def test_concurrent_requests(self, processor):
        """Test handling multiple requests (simplified)"""
        with patch.object(processor, '_call_ai_once') as mock_ai:
            mock_ai.return_value = '{"结果": "成功"}'

            # Make multiple calls
            result1 = processor.extract_structure("文本1", "summary_bullets")
            result2 = processor.extract_structure("文本2", "summary_bullets")

            assert result1["要点"] == "成功"
            assert result2["要点"] == "成功"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
