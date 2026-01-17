"""
Database models for template management
"""
from django.db import models
from django.contrib.auth.models import User
import json
import logging

logger = logging.getLogger(__name__)


class DocumentTemplate(models.Model):
    """
    Database model for storing document templates
    """
    # Template types
    TEMPLATE_TYPE_CHOICES = [
        ('system', 'System Template'),
        ('user', 'User Template'),
    ]

    # Basic information
    template_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier (e.g., 'annual_work_summary')"
    )
    name = models.CharField(
        max_length=200,
        help_text="Display name"
    )
    description = models.TextField(
        help_text="Template description"
    )
    category = models.CharField(
        max_length=100,
        help_text="Template category (e.g., '工作总结', '项目报告')"
    )

    # Template structure (stored as JSON)
    sections_json = models.JSONField(
        help_text="Template sections structure in JSON format",
        default=dict
    )

    # Metadata
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        default='user',
        help_text="Whether this is a system or user template"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_templates',
        null=True,  # Allow null for system templates
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    version = models.CharField(
        max_length=20,
        default='1.0'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available"
    )

    # Usage statistics
    usage_count = models.IntegerField(
        default=0,
        help_text="Number of times this template has been used"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Document Template"
        verbose_name_plural = "Document Templates"
        unique_together = [['template_id', 'created_by']]  # Each user can have unique template IDs

    def __str__(self):
        return f"{self.name} ({self.template_id})"

    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def to_template_definition(self):
        """
        Convert database model to TemplateDefinition object
        This is used when loading templates from database
        """
        from .utils.template_definitions import DocumentTemplate, TemplateSection, SectionType

        sections_data = self.sections_json.get('sections', [])
        sections = [
            self._dict_to_section(section_dict)
            for section_dict in sections_data
        ]

        return DocumentTemplate(
            id=self.template_id,
            name=self.name,
            description=self.description,
            category=self.category,
            sections=sections,
            created_by=self.created_by.username if self.created_by else 'system',
            version=self.version
        )

    def _dict_to_section(self, section_dict: dict):
        """Convert dictionary to TemplateSection object"""
        from .utils.template_definitions import TemplateSection, SectionType

        subsections = [
            self._dict_to_section(sub)
            for sub in section_dict.get('subsections', [])
        ]

        return TemplateSection(
            id=section_dict['id'],
            title=section_dict['title'],
            section_type=SectionType(section_dict.get('section_type', 'heading')),
            word_count=section_dict.get('word_count'),
            requirements=section_dict.get('requirements'),
            subsections=subsections,
            bullet_points=section_dict.get('bullet_points'),
            is_optional=section_dict.get('is_optional', False),
            placeholder_template=section_dict.get('placeholder_template')
        )

    def save(self, *args, **kwargs):
        # Validate template before saving
        if self.sections_json:
            from .utils.template_validator import TemplateValidator
            is_valid, errors = TemplateValidator.validate_custom_template_json(self.sections_json)
            if not is_valid:
                logger.warning(f"Invalid template structure: {errors}")
                raise ValueError(f"Invalid template structure: {', '.join(errors)}")

        super().save(*args, **kwargs)


class TemplateUsageLog(models.Model):
    """
    Track template usage for analytics and debugging
    """
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        null=True,  # Allow null for deleted templates
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    used_at = models.DateTimeField(
        auto_now_add=True
    )

    # Input parameters
    user_outline = models.TextField(
        help_text="User's outline/key points"
    )
    had_source_document = models.BooleanField(
        default=False,
        help_text="Whether user uploaded a source document"
    )
    template_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Template name used (for reference if template is deleted)"
    )

    # Results
    generation_success = models.BooleanField(
        default=True,
        help_text="Whether the generation was successful"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )
    generation_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Generation duration in seconds"
    )

    class Meta:
        ordering = ['-used_at']
        verbose_name = "Template Usage Log"
        verbose_name_plural = "Template Usage Logs"

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        template_str = self.template_name if self.template else 'Deleted Template'
        return f"{user_str} - {template_str} - {self.used_at.strftime('%Y-%m-%d %H:%M')}"
