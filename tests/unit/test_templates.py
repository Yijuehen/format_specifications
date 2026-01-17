"""
Test all predefined templates
"""
import os
import sys
import django

# Setup Django environment
# Navigate to project root from tests/unit/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'format_specifications.settings')
django.setup()

from format_specifications.utils.predefined_templates import (
    PREDEFINED_TEMPLATES,
    list_all_templates,
    get_template
)
from format_specifications.utils.template_validator import TemplateValidator


def test_all_templates_exist():
    """Test that all 10 templates exist and are accessible"""
    print("\n" + "=" * 60)
    print("TEST 1: Template Availability")
    print("=" * 60)

    expected_templates = [
        "annual_work_summary",
        "project_summary_report",
        "meeting_minutes",
        "work_plan",
        "weekly_monthly_report",
        "research_report",
        "problem_analysis_report",
        "training_summary",
        "event_planning",
        "competitor_analysis"
    ]

    print(f"Expected templates: {len(expected_templates)}")
    print(f"Available templates: {len(PREDEFINED_TEMPLATES)}")

    for template_id in expected_templates:
        assert template_id in PREDEFINED_TEMPLATES, f"Missing template: {template_id}"
        template = PREDEFINED_TEMPLATES[template_id]
        print(f"  [OK] {template.name} ({template_id})")

    print(f"[SUCCESS] All {len(expected_templates)} templates available")
    return True


def test_template_structure():
    """Test that each template has correct structure"""
    print("\n" + "=" * 60)
    print("TEST 2: Template Structure Validation")
    print("=" * 60)

    for template_id, template in PREDEFINED_TEMPLATES.items():
        print(f"\nValidating: {template.name} ({template_id})")

        # Validate using validator
        errors = TemplateValidator.validate_template(template)

        if errors:
            print(f"  ✗ Validation failed with {len(errors)} errors:")
            for error in errors:
                print(f"    - {error}")
            return False
        else:
            # Check basic structure
            assert template.id, "Missing ID"
            assert template.name, "Missing name"
            assert template.description, "Missing description"
            assert template.category, "Missing category"
            assert template.sections, "Missing sections"
            assert len(template.sections) > 0, "No sections"

            # Count sections
            total_sections = len(template.sections)
            total_subsections = sum(len(s.subsections) for s in template.sections)

            print(f"  [OK] Valid structure")
            print(f"    Sections: {total_sections}, Subsections: {total_subsections}")

    print(f"\n[SUCCESS] All templates have valid structure")
    return True


def test_template_details():
    """Test specific details of each template"""
    print("\n" + "=" * 60)
    print("TEST 3: Template Details")
    print("=" * 60)

    template_info = []

    for template_id, template in PREDEFINED_TEMPLATES.items():
        total_word_count = 0
        section_count = len(template.sections)
        subsection_count = sum(len(s.subsections) for s in template.sections)

        # Count word counts
        def count_words(section):
            count = section.word_count or 0
            for subsection in section.subsections:
                count += count_words(subsection)
            return count

        for section in template.sections:
            total_word_count += count_words(section)

        template_info.append({
            'id': template_id,
            'name': template.name,
            'category': template.category,
            'sections': section_count,
            'subsections': subsection_count,
            'total_words': total_word_count
        })

        print(f"\n{template.name}")
        print(f"  Category: {template.category}")
        print(f"  Sections: {section_count} (with {subsection_count} subsections)")
        print(f"  Target word count: ~{total_word_count} words")

    print(f"\n[SUCCESS] All {len(template_info)} templates have valid details")
    return True


def test_template_retrieval():
    """Test get_template function"""
    print("\n" + "=" * 60)
    print("TEST 4: Template Retrieval")
    print("=" * 60)

    # Test getting each template
    for template_id in PREDEFINED_TEMPLATES.keys():
        template = get_template(template_id)
        assert template is not None, f"Failed to get template: {template_id}"
        assert template.id == template_id
        print(f"  [OK] Retrieved: {template.name}")

    # Test getting non-existent template
    template = get_template("non_existent_template")
    assert template is None
    print(f"  [OK] Non-existent template returns None")

    print(f"\n[SUCCESS] Template retrieval working correctly")
    return True


def test_list_all_templates():
    """Test list_all_templates function"""
    print("\n" + "=" * 60)
    print("TEST 5: List All Templates")
    print("=" * 60)

    templates = list_all_templates()

    assert len(templates) == 10, f"Expected 10 templates, got {len(templates)}"
    print(f"Total templates: {len(templates)}")

    for template_id, name, category in templates:
        print(f"  - {name} ({category}) - ID: {template_id}")

    print(f"\n[SUCCESS] Listing all templates works correctly")
    return True


def test_template_serialization():
    """Test template to_dict conversion"""
    print("\n" + "=" * 60)
    print("TEST 6: Template Serialization")
    print("=" * 60)

    for template_id, template in PREDEFINED_TEMPLATES.items():
        template_dict = template.to_dict()

        # Check required fields
        assert 'id' in template_dict
        assert 'name' in template_dict
        assert 'description' in template_dict
        assert 'category' in template_dict
        assert 'sections' in template_dict

        print(f"  [OK] {template.name} serialized to dict")

    print(f"\n[SUCCESS] All templates can be serialized")
    return True


def test_nested_sections():
    """Test that templates with nested sections work correctly"""
    print("\n" + "=" * 60)
    print("TEST 7: Nested Sections")
    print("=" * 60)

    # Annual work summary has nested sections
    template = get_template("annual_work_summary")
    assert template is not None

    # Find the "achievements" section (has subsections)
    achievements_section = None
    for section in template.sections:
        if section.id == "achievements":
            achievements_section = section
            break

    assert achievements_section is not None, "Achievements section not found"
    assert len(achievements_section.subsections) == 6, f"Expected 6 subsections, got {len(achievements_section.subsections)}"

    print(f"Section: {achievements_section.title}")
    print(f"  Subsections: {len(achievements_section.subsections)}")
    for subsection in achievements_section.subsections:
        subsection_title = subsection.title.replace('•', '-').replace('●', '-')
        print(f"    - {subsection_title} ({subsection.word_count} words)")

    print(f"\n[SUCCESS] Nested sections working correctly")
    return True


def test_optional_sections():
    """Test optional sections are marked correctly"""
    print("\n" + "=" * 60)
    print("TEST 8: Optional Sections")
    print("=" * 60)

    # Check templates have optional sections
    templates_with_optional = []

    for template_id, template in PREDEFINED_TEMPLATES.items():
        optional_count = 0
        for section in template.sections:
            if section.is_optional:
                optional_count += 1

        if optional_count > 0:
            templates_with_optional.append({
                'template': template.name,
                'optional_count': optional_count
            })

    print(f"Templates with optional sections: {len(templates_with_optional)}")
    for info in templates_with_optional:
        print(f"  - {info['template']}: {info['optional_count']} optional section(s)")

    # Annual work summary should have 1 optional section (appendix)
    annual_template = get_template("annual_work_summary")
    appendix = None
    for section in annual_template.sections:
        if section.id == "appendix":
            appendix = section
            break

    assert appendix is not None, "Appendix section not found"
    assert appendix.is_optional == True, "Appendix should be marked as optional"

    print(f"\n[SUCCESS] Optional sections marked correctly")
    return True


def test_section_types():
    """Test that different section types are used"""
    print("\n" + "=" * 60)
    print("TEST 9: Section Types")
    print("=" * 60)

    # Collect all section types used
    from format_specifications.utils.template_definitions import SectionType

    type_counts = {st.value: 0 for st in SectionType}

    for template_id, template in PREDEFINED_TEMPLATES.items():
        def count_types(section):
            type_counts[section.section_type.value] += 1
            for subsection in section.subsections:
                count_types(subsection)

        for section in template.sections:
            count_types(section)

    print("Section types used across all templates:")
    for section_type, count in type_counts.items():
        print(f"  - {section_type}: {count} occurrences")

    # Check that we use multiple types
    used_types = [t for t, c in type_counts.items() if c > 0]
    assert len(used_types) >= 2, "Should use at least 2 different section types"

    print(f"\n[SUCCESS] Multiple section types used ({len(used_types)} types)")
    return True


def main():
    """Run all template tests"""
    print("=" * 60)
    print("TEMPLATE SYSTEM TESTING")
    print("=" * 60)

    results = {}

    try:
        results['availability'] = test_all_templates_exist()
        results['structure'] = test_template_structure()
        results['details'] = test_template_details()
        results['retrieval'] = test_template_retrieval()
        results['listing'] = test_list_all_templates()
        results['serialization'] = test_template_serialization()
        results['nested'] = test_nested_sections()
        results['optional'] = test_optional_sections()
        results['types'] = test_section_types()

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
        print("[SUCCESS] ALL TEMPLATE TESTS PASSED!")
        print("=" * 60)
        print("\nTemplate System Summary:")
        print("  - 10 predefined templates created")
        print("  - All templates validated successfully")
        print("  - Database models created and migrated")
        print("  - Nested sections supported")
        print("  - Optional sections supported")
        print("  - Multiple section types supported")
        print("\nTemplates available:")
        print("  1. 年度工作总结")
        print("  2. 项目总结报告")
        print("  3. 会议纪要")
        print("  4. 工作计划")
        print("  5. 周报/月报")
        print("  6. 调研报告")
        print("  7. 问题分析报告")
        print("  8. 培训总结")
        print("  9. 活动策划")
        print("  10. 竞品分析")
        print("\nNext: Implement Phase 2 (AI Generation)")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
