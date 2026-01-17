"""
Template validation utilities
"""
import re
import json
import logging
from typing import List, Dict, Tuple
from .template_definitions import TemplateSection, DocumentTemplate, SectionType

logger = logging.getLogger(__name__)


class TemplateValidationError(Exception):
    """Raised when template validation fails"""
    pass


class TemplateValidator:
    """Validates template definitions for correctness and completeness"""

    # Valid template ID pattern (alphanumeric, underscores, hyphens)
    TEMPLATE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    @staticmethod
    def validate_template_id(template_id: str) -> bool:
        """
        Validate template ID format
        Args:
            template_id: Template identifier to validate
        Returns:
            True if valid, False otherwise
        """
        return bool(TemplateValidator.TEMPLATE_ID_PATTERN.match(template_id))

    @staticmethod
    def validate_section(section: TemplateSection) -> List[str]:
        """
        Validate a single section
        Args:
            section: TemplateSection to validate
        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check required fields
        if not section.id or not isinstance(section.id, str):
            errors.append("Section must have a valid 'id' string")
        if not section.title or not isinstance(section.title, str):
            errors.append("Section must have a valid 'title' string")
        if not isinstance(section.section_type, SectionType):
            errors.append(f"Section must have a valid 'section_type' (SectionType enum)")

        # Validate word count
        if section.word_count is not None:
            if not isinstance(section.word_count, int) or section.word_count < 0:
                errors.append(f"Section '{section.id}': word_count must be a positive integer")
            if section.word_count > 10000:
                errors.append(f"Section '{section.id}': word_count too large (max 10000)")

        # Validate list sections
        if section.section_type == SectionType.LIST and not section.bullet_points:
            errors.append(f"Section '{section.id}': list type sections must have bullet_points")

        # Validate nested sections recursively
        for i, subsection in enumerate(section.subsections):
            subsection_errors = TemplateValidator.validate_section(subsection)
            for error in subsection_errors:
                errors.append(f"Section '{section.id}' subsection {i+1}: {error}")

        return errors

    @staticmethod
    def validate_template(template: DocumentTemplate) -> List[str]:
        """
        Validate complete template
        Args:
            template: DocumentTemplate to validate
        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate template ID
        if not TemplateValidator.validate_template_id(template.id):
            errors.append(f"Invalid template ID: '{template.id}'. Only alphanumeric, underscores, and hyphens allowed")

        # Validate required fields
        if not template.name or not isinstance(template.name, str):
            errors.append("Template must have a valid 'name' string")
        if not template.description or not isinstance(template.description, str):
            errors.append("Template must have a valid 'description' string")
        if not template.category or not isinstance(template.category, str):
            errors.append("Template must have a valid 'category' string")

        # Validate sections
        if not template.sections or not isinstance(template.sections, list):
            errors.append("Template must have at least one section")
        else:
            if len(template.sections) == 0:
                errors.append("Template sections list cannot be empty")
            if len(template.sections) > 50:
                errors.append(f"Template has too many sections ({len(template.sections)}), max 50")

            # Validate each section
            for i, section in enumerate(template.sections):
                section_errors = TemplateValidator.validate_section(section)
                for error in section_errors:
                    errors.append(f"Section {i+1} ('{section.id}'): {error}")

        # Validate total word count
        if template.total_word_count is not None:
            if not isinstance(template.total_word_count, int) or template.total_word_count < 0:
                errors.append("total_word_count must be a positive integer")
            if template.total_word_count > 100000:
                errors.append("total_word_count too large (max 100000)")

        return errors

    @staticmethod
    def validate_custom_template_json(template_json: Dict) -> Tuple[bool, List[str]]:
        """
        Validate user-submitted custom template JSON
        Args:
            template_json: Dictionary containing template data
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        try:
            # Check required fields
            required_fields = ['id', 'name', 'description', 'category', 'sections']
            for field in required_fields:
                if field not in template_json:
                    errors.append(f"Missing required field: '{field}'")

            # Validate sections structure
            if 'sections' in template_json:
                if not isinstance(template_json['sections'], list):
                    errors.append("'sections' must be a list")
                elif len(template_json['sections']) == 0:
                    errors.append("Template must have at least one section")
                else:
                    # Validate each section
                    for i, section_dict in enumerate(template_json['sections']):
                        section_errors = TemplateValidator._validate_section_dict(section_dict)
                        for error in section_errors:
                            errors.append(f"Section {i+1}: {error}")

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return (len(errors) == 0, errors)

    @staticmethod
    def _validate_section_dict(section_dict: Dict) -> List[str]:
        """
        Validate a section dictionary (from JSON)
        Args:
            section_dict: Dictionary containing section data
        Returns:
            List of error messages
        """
        errors = []

        # Required fields
        required_fields = ['id', 'title', 'section_type']
        for field in required_fields:
            if field not in section_dict:
                errors.append(f"Missing required field: '{field}'")

        # Validate section_type
        if 'section_type' in section_dict:
            valid_types = ['heading', 'list', 'nested', 'table', 'optional']
            if section_dict['section_type'] not in valid_types:
                errors.append(f"Invalid section_type: '{section_dict['section_type']}'")

        # Validate word_count
        if 'word_count' in section_dict:
            if not isinstance(section_dict['word_count'], int):
                errors.append("word_count must be an integer")
            elif section_dict['word_count'] < 0:
                errors.append("word_count must be positive")

        # Validate subsections if present
        if 'subsections' in section_dict:
            if not isinstance(section_dict['subsections'], list):
                errors.append("subsections must be a list")
            else:
                for i, subsection_dict in enumerate(section_dict['subsections']):
                    subsection_errors = TemplateValidator._validate_section_dict(subsection_dict)
                    for error in subsection_errors:
                        errors.append(f"Subsection {i+1}: {error}")

        return errors

    @staticmethod
    def validate_template_consistency(template: DocumentTemplate) -> List[str]:
        """
        Validate logical consistency of template
        Args:
            template: DocumentTemplate to validate
        Returns:
            List of warning messages (not errors, just warnings)
        """
        warnings = []

        # Check for duplicate section IDs
        section_ids = []
        def collect_section_ids(section: TemplateSection):
            section_ids.append(section.id)
            for subsection in section.subsections:
                collect_section_ids(subsection)

        for section in template.sections:
            collect_section_ids(section)

        duplicates = [sid for sid in set(section_ids) if section_ids.count(sid) > 1]
        if duplicates:
            warnings.append(f"Duplicate section IDs found: {', '.join(duplicates)}")

        # Check word count total vs sections
        if template.total_word_count and template.sections:
            section_word_counts = []
            def collect_word_counts(section: TemplateSection):
                if section.word_count:
                    section_word_counts.append(section.word_count)
                for subsection in section.subsections:
                    collect_word_counts(subsection)

            for section in template.sections:
                collect_word_counts(section)

            total_estimated = sum(section_word_counts)
            if total_estimated > template.total_word_count * 1.5:
                warnings.append(f"Total section word counts ({total_estimated}) significantly exceed template total ({template.total_word_count})")
            elif total_estimated < template.total_word_count * 0.5:
                warnings.append(f"Total section word counts ({total_estimated}) significantly less than template total ({template.total_word_count})")

        return warnings
