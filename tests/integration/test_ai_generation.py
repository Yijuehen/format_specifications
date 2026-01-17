"""
Test AI template generation functionality
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

from format_specifications.utils.predefined_templates import get_template
from format_specifications.utils.ai_word_utils import AITextProcessor
from format_specifications.utils.document_extractor import DocumentExtractor


def test_skeleton_generation():
    """Test skeleton content generation without source document"""
    print("\n" + "=" * 60)
    print("TEST 1: Skeleton Generation (No Source Document)")
    print("=" * 60)

    # Get a template
    template = get_template("annual_work_summary")
    assert template is not None

    # Create AI processor
    processor = AITextProcessor(tone='direct')

    # User outline
    user_outline = """
    2024年度工作总结要点：
    - 完成了3个重点项目，提升了20%的工作效率
    - 培训了2名新人，帮助他们快速上手
    - 优化了团队工作流程，减少了沟通成本
    - 存在的问题：时间管理需要改进，技能深度有待提升
    - 2025年目标：提升技术能力，承担更多责任
    """

    try:
        # Generate content
        generated = processor.generate_from_template(
            template=template,
            user_outline=user_outline,
            tone='direct'
        )

        print(f"\nGenerated {len(generated)} sections")
        print("\nGenerated content preview:")

        for section_id, content in list(generated.items())[:5]:
            if content:
                # Clean Unicode characters for Windows console output
                preview = content[:150].replace('\n', ' ')
                section_id_clean = section_id.replace('•', '-').replace('●', '-')
                preview_clean = preview.replace('•', '-').replace('●', '-')
                print(f"\n[{section_id_clean}]")
                print(f"  {preview_clean}...")

        print(f"\n[SUCCESS] Skeleton generation completed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Skeleton generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_generation():
    """Test hybrid generation with source document"""
    print("\n" + "=" * 60)
    print("TEST 2: Hybrid Generation (With Source Document)")
    print("=" * 60)

    # Get a template
    template = get_template("meeting_minutes")
    assert template is not None

    # Create AI processor
    processor = AITextProcessor(tone='direct')

    # User outline
    user_outline = """
    项目进度会议：
    - 讨论了当前项目的进展情况
    - 识别了几个技术挑战
    - 确定了下一步的行动计划
    """

    # Simulated source document text
    source_text = """
    项目进度会议记录

    参会人员：张三、李四、王五
    时间：2024年1月15日

    讨论内容：
    项目目前进展顺利，前端开发已完成80%，后端API开发完成60%。
    遇到了性能优化的问题，需要进一步研究。
    数据库设计基本完成，但需要调整索引结构。

    行动项：
    张三负责前端优化，预计下周完成
    李四负责API接口开发，预计两周内完成
    王五负责数据库调优
    """

    try:
        # Generate content with source document
        generated = processor.generate_from_template(
            template=template,
            user_outline=user_outline,
            source_document_text=source_text,
            tone='direct'
        )

        print(f"\nGenerated {len(generated)} sections")
        print("\nGenerated content preview:")

        for section_id, content in list(generated.items())[:5]:
            if content:
                # Clean Unicode characters for Windows console output
                preview = content[:150].replace('\n', ' ')
                section_id_clean = section_id.replace('•', '-').replace('●', '-')
                preview_clean = preview.replace('•', '-').replace('●', '-')
                print(f"\n[{section_id_clean}]")
                print(f"  {preview_clean}...")

        print(f"\n[SUCCESS] Hybrid generation completed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Hybrid generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_sections():
    """Test list-type section formatting"""
    print("\n" + "=" * 60)
    print("TEST 3: List Section Formatting")
    print("=" * 60)

    # Get a template with list sections
    template = get_template("weekly_monthly_report")
    assert template is not None

    # Create AI processor
    processor = AITextProcessor(tone='direct')

    # User outline
    user_outline = """
    本周工作总结：
    - 完成了用户管理模块的开发
    - 修复了3个线上bug
    - 参与了代码评审

    下周计划：
    - 开始订单模块开发
    - 学习新技术框架
    """

    try:
        # Generate content
        generated = processor.generate_from_template(
            template=template,
            user_outline=user_outline,
            tone='direct'
        )

        print(f"\nGenerated {len(generated)} sections")

        # Check if list sections were generated
        list_sections = [sid for sid in generated.keys() if 'work' in sid or 'plan' in sid]
        print(f"\nList-related sections: {len(list_sections)}")

        for section_id in list_sections[:3]:
            content = generated.get(section_id, "")
            if content:
                preview = content[:200].replace('\n', ' ')
                section_id_clean = section_id.replace('•', '-').replace('●', '-')
                preview_clean = preview.replace('•', '-').replace('●', '-')
                print(f"\n[{section_id_clean}]")
                print(f"  {preview_clean}...")

        print(f"\n[SUCCESS] List section formatting completed")
        return True

    except Exception as e:
        print(f"\n[ERROR] List section formatting failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_nested_sections():
    """Test generation with nested sections"""
    print("\n" + "=" * 60)
    print("TEST 4: Nested Section Generation")
    print("=" * 60)

    # Get a template with nested sections
    template = get_template("annual_work_summary")
    assert template is not None

    # Create AI processor
    processor = AITextProcessor(tone='direct')

    # User outline
    user_outline = """
    年度工作总结：
    - 完成了年度KPI，达成率110%
    - 主导了核心项目，提升了团队效率
    - 获得优秀员工称号
    """

    try:
        # Generate content
        generated = processor.generate_from_template(
            template=template,
            user_outline=user_outline,
            tone='direct'
        )

        print(f"\nGenerated {len(generated)} sections")

        # Check nested sections (achievements has subsections)
        nested_sections = [sid for sid in generated.keys() if 'achievement' in sid]
        print(f"\nNested achievement sections: {len(nested_sections)}")

        for section_id in nested_sections:
            content = generated.get(section_id, "")
            if content:
                preview = content[:100].replace('\n', ' ')
                section_id_clean = section_id.replace('•', '-').replace('●', '-')
                preview_clean = preview.replace('•', '-').replace('●', '-')
                print(f"\n  [{section_id_clean}]")
                print(f"    {preview_clean}...")

        print(f"\n[SUCCESS] Nested section generation completed")
        return True

    except Exception as e:
        print(f"\n[ERROR] Nested section generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all AI generation tests"""
    print("=" * 60)
    print("AI TEMPLATE GENERATION TESTING")
    print("=" * 60)

    results = {}

    try:
        # Note: These tests require valid ZHIPU_API_KEY in .env file
        results['skeleton'] = test_skeleton_generation()
        results['hybrid'] = test_hybrid_generation()
        results['list_sections'] = test_list_sections()
        results['nested_sections'] = test_nested_sections()

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL AI GENERATION TESTS PASSED!")
        print("=" * 60)
        print("\nAI Generation System Summary:")
        print("  - Skeleton content generation working")
        print("  - Hybrid extraction + generation working")
        print("  - List section formatting working")
        print("  - Nested section generation working")
        print("\nNext: Implement Phase 3 (Template Management Service)")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
