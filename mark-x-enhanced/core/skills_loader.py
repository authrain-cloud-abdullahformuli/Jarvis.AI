"""Dynamic skill loader for Mark-X Enhanced."""

import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional
import logging

from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class SkillsLoader:
    """Dynamically loads and manages skills."""
    
    def __init__(self, skills_directory: str = "skills"):
        self.skills_directory = Path(skills_directory)
        self.skills: Dict[str, BaseSkill] = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skills from the skills directory."""
        if not self.skills_directory.exists():
            logger.warning(f"Skills directory {self.skills_directory} does not exist")
            return
        
        # Get all Python files in the skills directory
        skill_files = list(self.skills_directory.glob("*.py"))
        
        for skill_file in skill_files:
            # Skip __init__.py and base_skill.py
            if skill_file.name in ["__init__.py", "base_skill.py"]:
                continue
            
            try:
                self._load_skill_from_file(skill_file)
            except Exception as e:
                logger.error(f"Failed to load skill from {skill_file}: {e}")
    
    def _load_skill_from_file(self, file_path: Path):
        """Load a skill from a Python file."""
        # Convert file path to module name
        module_name = f"skills.{file_path.stem}"
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find all classes that inherit from BaseSkill
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseSkill) and obj is not BaseSkill:
                    # Instantiate the skill
                    skill_instance = obj()
                    self.skills[skill_instance.name] = skill_instance
                    logger.info(f"Loaded skill: {skill_instance.name}")
        
        except Exception as e:
            logger.error(f"Error loading skill from {file_path}: {e}")
            raise
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a skill by name."""
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> List[BaseSkill]:
        """Get all loaded skills."""
        return list(self.skills.values())
    
    def get_skills_by_category(self, category: str) -> List[BaseSkill]:
        """Get all skills in a specific category."""
        return [
            skill for skill in self.skills.values()
            if skill.category.value == category
        ]
    
    def get_skill_names(self) -> List[str]:
        """Get all skill names."""
        return list(self.skills.keys())
    
    def get_skills_for_llm(self) -> List[Dict]:
        """Get skill information formatted for LLM context."""
        return [skill.to_dict() for skill in self.skills.values()]
    
    def reload_skills(self):
        """Reload all skills (useful for development)."""
        self.skills.clear()
        self._load_all_skills()
    
    def register_skill(self, skill_instance: BaseSkill):
        """Manually register a skill instance."""
        self.skills[skill_instance.name] = skill_instance
        logger.info(f"Manually registered skill: {skill_instance.name}")


# Global skills loader instance
skills_loader = SkillsLoader()
