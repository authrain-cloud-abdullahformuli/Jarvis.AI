"""Base skill interface for Mark-X Enhanced."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class SkillCategory(Enum):
    """Skill categories."""
    SYSTEM = "system"
    COMMUNICATION = "communication"
    INFORMATION = "information"
    AUTOMATION = "automation"
    ENTERTAINMENT = "entertainment"
    PRODUCTIVITY = "productivity"


@dataclass
class SkillParameter:
    """Skill parameter definition."""
    name: str
    description: str
    required: bool = True
    param_type: type = str
    default: Any = None


@dataclass
class SkillResult:
    """Result of skill execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    needs_user_input: bool = False
    prompt_for: Optional[str] = None


class BaseSkill(ABC):
    """Base class for all skills."""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.category = self.get_category()
        self.parameters = self.get_parameters()
        self.examples = self.get_examples()
    
    @abstractmethod
    def get_name(self) -> str:
        """Return skill name."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return skill description."""
        pass
    
    @abstractmethod
    def get_category(self) -> SkillCategory:
        """Return skill category."""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[SkillParameter]:
        """Return list of parameters this skill requires."""
        pass
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
        """Execute the skill with given parameters.
        
        Args:
            parameters: Skill parameters extracted from user input
            context: Additional context (memory, user info, etc.)
            
        Returns:
            SkillResult with execution status and data
        """
        pass
    
    def get_examples(self) -> List[str]:
        """Return example user inputs for this skill."""
        return []
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that all required parameters are present.
        
        Returns:
            Tuple of (is_valid, missing_parameter_name)
        """
        for param in self.parameters:
            if param.required and param.name not in parameters:
                return False, param.name
        return True, None
    
    def get_parameter_description(self, param_name: str) -> Optional[str]:
        """Get description of a specific parameter."""
        for param in self.parameters:
            if param.name == param_name:
                return param.description
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary for LLM context."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "required": p.required,
                    "type": p.param_type.__name__
                }
                for p in self.parameters
            ],
            "examples": self.examples
        }
