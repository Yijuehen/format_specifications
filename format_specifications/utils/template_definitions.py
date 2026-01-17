"""
Template data structures for document generation
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Union


class SectionType(Enum):
    """Section types for different content structures"""
    HEADING = "heading"           # Simple heading with content
    LIST = "list"                 # Bullet points with sub-items
    NESTED = "nested"             # Nested sections (subheadings)
    TABLE = "table"               # Table structure
    OPTIONAL = "optional"         # Optional content


@dataclass
class TemplateSection:
    """Represents a single section in a template"""
    id: str                              # Unique identifier (e.g., "overview")
    title: str                           # Display title (e.g., "一、开篇概览")
    section_type: SectionType            # Type of section
    word_count: Optional[int] = None     # Target word count (e.g., 100)
    requirements: Optional[str] = None   # Content requirements/guidance
    subsections: List['TemplateSection'] = field(default_factory=list)  # Nested sections
    bullet_points: Optional[List[str]] = None  # For list sections
    is_optional: bool = False            # Whether section is optional
    placeholder_template: Optional[str] = None  # Template for generating skeleton content


@dataclass
class DocumentTemplate:
    """Complete document template definition"""
    id: str                              # Template ID (e.g., "annual_work_summary")
    name: str                            # Display name
    description: str                     # Template description
    category: str                        # Category (e.g., "工作总结", "项目报告")
    sections: List[TemplateSection]      # Top-level sections
    total_word_count: Optional[int] = None  # Optional target total
    created_by: str = "system"           # Creator (system/user)
    version: str = "1.0"                 # Template version

    def to_dict(self) -> Dict:
        """Convert template to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'version': self.version,
            'sections': [self._section_to_dict(s) for s in self.sections]
        }

    def _section_to_dict(self, section: TemplateSection) -> Dict:
        """Convert section to dictionary"""
        return {
            'id': section.id,
            'title': section.title,
            'section_type': section.section_type.value,
            'word_count': section.word_count,
            'requirements': section.requirements,
            'subsections': [self._section_to_dict(s) for s in section.subsections],
            'bullet_points': section.bullet_points,
            'is_optional': section.is_optional,
            'placeholder_template': section.placeholder_template
        }
