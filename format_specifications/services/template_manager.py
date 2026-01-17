"""
Template management service for template CRUD operations
"""
import logging
from typing import List, Tuple, Optional
from django.contrib.auth.models import User
from format_specifications.models import DocumentTemplate, TemplateUsageLog
from format_specifications.utils.predefined_templates import PREDEFINED_TEMPLATES, get_template as get_predefined_template
from format_specifications.utils.template_validator import TemplateValidator

logger = logging.getLogger(__name__)


class TemplateManager:
    """Service for managing document templates"""

    @staticmethod
    def get_template(template_id: str, user: User = None) -> Optional[object]:
        """
        Get a template by ID (checks predefined first, then database)

        Args:
            template_id: Template identifier
            user: Optional user for user-specific templates

        Returns:
            Template object or None
        """
        # First check predefined templates
        if template_id in PREDEFINED_TEMPLATES:
            logger.debug(f"Retrieved predefined template: {template_id}")
            return PREDEFINED_TEMPLATES[template_id]

        # Then check database for user templates
        try:
            if user:
                db_template = DocumentTemplate.objects.get(
                    template_id=template_id,
                    created_by=user,
                    is_active=True
                )
            else:
                # Only get active user templates (no authentication required)
                db_template = DocumentTemplate.objects.get(
                    template_id=template_id,
                    is_active=True
                )

            # Convert database model to template definition
            template = db_template.to_template_definition()
            logger.debug(f"Retrieved database template: {template_id}")
            return template

        except DocumentTemplate.DoesNotExist:
            logger.warning(f"Template not found: {template_id}")
            return None

    @staticmethod
    def list_available_templates(user: User = None) -> List[Tuple[str, str, str, str]]:
        """
        List all available templates (system + user)

        Args:
            user: Optional user to include their custom templates

        Returns:
            List of tuples: (template_id, name, category, template_type)
        """
        templates = []

        # Add predefined templates
        for template_id, template in PREDEFINED_TEMPLATES.items():
            templates.append((
                template_id,
                template.name,
                template.category,
                'system'
            ))

        # Add user templates from database
        if user:
            user_templates = DocumentTemplate.objects.filter(
                created_by=user,
                is_active=True
            )

            for db_template in user_templates:
                templates.append((
                    db_template.template_id,
                    db_template.name,
                    db_template.category,
                    'user'
                ))

        logger.info(f"Listed {len(templates)} templates for user {user}")
        return templates

    @staticmethod
    def create_custom_template(
        user: User,
        template_id: str,
        name: str,
        description: str,
        category: str,
        sections_data: dict,
        version: str = "1.0"
    ) -> DocumentTemplate:
        """
        Create a new custom template

        Args:
            user: User creating the template
            template_id: Unique template identifier
            name: Template display name
            description: Template description
            category: Template category
            sections_data: Template sections structure (dict/JSON)
            version: Template version

        Returns:
            Created DocumentTemplate instance

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Creating custom template: {template_id} for user {user}")

        # Validate template structure
        is_valid, errors = TemplateValidator.validate_custom_template_json(sections_data)

        if not is_valid:
            error_msg = f"Template validation failed: {', '.join(errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Check if template_id already exists for this user
        existing = DocumentTemplate.objects.filter(
            template_id=template_id,
            created_by=user
        ).first()

        if existing:
            raise ValueError(f"Template ID '{template_id}' already exists for this user")

        # Create database record
        db_template = DocumentTemplate.objects.create(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            sections_json=sections_data,
            template_type='user',
            created_by=user,
            version=version
        )

        logger.info(f"Created custom template: {template_id}")
        return db_template

    @staticmethod
    def update_template(
        template_id: str,
        user: User,
        **updates
    ) -> DocumentTemplate:
        """
        Update an existing user template

        Args:
            template_id: Template identifier
            user: User who owns the template
            **updates: Fields to update (name, description, category, sections_json, etc.)

        Returns:
            Updated DocumentTemplate instance

        Raises:
            ValueError: If template not found or validation fails
        """
        logger.info(f"Updating template: {template_id} for user {user}")

        try:
            db_template = DocumentTemplate.objects.get(
                template_id=template_id,
                created_by=user,
                is_active=True
            )

        except DocumentTemplate.DoesNotExist:
            raise ValueError(f"Template '{template_id}' not found or doesn't belong to user")

        # Validate sections_json if provided
        if 'sections_json' in updates:
            is_valid, errors = TemplateValidator.validate_custom_template_json(updates['sections_json'])
            if not is_valid:
                error_msg = f"Template validation failed: {', '.join(errors)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # Update fields
        for field, value in updates.items():
            if hasattr(db_template, field):
                setattr(db_template, field, value)

        db_template.save()

        logger.info(f"Updated template: {template_id}")
        return db_template

    @staticmethod
    def delete_template(template_id: str, user: User) -> bool:
        """
        Soft delete a user template (set is_active=False)

        Args:
            template_id: Template identifier
            user: User who owns the template

        Returns:
            True if deleted, False otherwise

        Raises:
            ValueError: If template not found
        """
        logger.info(f"Deleting template: {template_id} for user {user}")

        try:
            db_template = DocumentTemplate.objects.get(
                template_id=template_id,
                created_by=user,
                is_active=True
            )

            # Soft delete
            db_template.is_active = False
            db_template.save()

            logger.info(f"Deleted template: {template_id}")
            return True

        except DocumentTemplate.DoesNotExist:
            raise ValueError(f"Template '{template_id}' not found or doesn't belong to user")

    @staticmethod
    def log_template_usage(
        template: object,
        user: User = None,
        user_outline: str = "",
        had_source_document: bool = False,
        generation_success: bool = True,
        error_message: str = "",
        generation_duration: int = None
    ) -> TemplateUsageLog:
        """
        Log template usage for analytics

        Args:
            template: Template object (predefined or database)
            user: Optional user who used the template
            user_outline: User's outline/key points
            had_source_document: Whether user uploaded a source document
            generation_success: Whether generation was successful
            error_message: Error message if generation failed
            generation_duration: Generation duration in seconds

        Returns:
            TemplateUsageLog instance
        """
        # Get database template if available
        db_template = None
        if hasattr(template, 'id'):
            # This is a database model
            db_template = template
            template_name = template.name
            template_id = template.template_id
        else:
            # This is a predefined template
            template_name = template.name
            template_id = template.id

        # Create usage log
        usage_log = TemplateUsageLog.objects.create(
            template=db_template,
            user=user,
            user_outline=user_outline,
            had_source_document=had_source_document,
            template_name=template_name,
            generation_success=generation_success,
            error_message=error_message,
            generation_duration=generation_duration
        )

        logger.info(f"Logged template usage: {template_id} - Success: {generation_success}")

        # Increment usage counter if database template
        if db_template:
            db_template.increment_usage()

        return usage_log

    @staticmethod
    def get_template_details_dict(template_id: str, user: User = None) -> Optional[dict]:
        """
        Get template details as dictionary for API responses

        Args:
            template_id: Template identifier
            user: Optional user

        Returns:
            Dictionary with template details or None
        """
        template = TemplateManager.get_template(template_id, user)

        if not template:
            return None

        # Convert to dictionary
        template_dict = template.to_dict() if hasattr(template, 'to_dict') else {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'sections': [s.__dict__ for s in template.sections] if hasattr(template.sections[0], '__dict__') else []
        }

        # Add template type
        if template_id in PREDEFINED_TEMPLATES:
            template_dict['type'] = 'system'
        else:
            template_dict['type'] = 'user'

        return template_dict
