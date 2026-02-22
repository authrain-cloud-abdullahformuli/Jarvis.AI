"""Open application skill."""

import subprocess
import platform
from typing import Dict, Any, List
from skills.base_skill import BaseSkill, SkillCategory, SkillParameter, SkillResult


class OpenAppSkill(BaseSkill):
    """Skill to open applications on the system."""
    
    def get_name(self) -> str:
        return "open_app"
    
    def get_description(self) -> str:
        return "Opens applications on your computer"
    
    def get_category(self) -> SkillCategory:
        return SkillCategory.SYSTEM
    
    def get_parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="app_name",
                description="Name of the application to open (e.g., 'chrome', 'spotify', 'vscode')",
                required=True,
                param_type=str
            )
        ]
    
    def get_examples(self) -> List[str]:
        return [
            "open chrome",
            "launch spotify",
            "start visual studio code",
            "open calculator"
        ]
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
        """Execute the skill to open an application."""
        app_name = parameters.get("app_name", "").lower()
        
        if not app_name:
            return SkillResult(
                success=False,
                message="Please specify which application you want me to open.",
                needs_user_input=True,
                prompt_for="app_name"
            )
        
        # App name mappings for different platforms
        app_mappings = {
            "chrome": {"windows": "chrome.exe", "darwin": "Google Chrome", "linux": "google-chrome"},
            "firefox": {"windows": "firefox.exe", "darwin": "Firefox", "linux": "firefox"},
            "spotify": {"windows": "spotify.exe", "darwin": "Spotify", "linux": "spotify"},
            "vscode": {"windows": "code.exe", "darwin": "Visual Studio Code", "linux": "code"},
            "code": {"windows": "code.exe", "darwin": "Visual Studio Code", "linux": "code"},
            "calculator": {"windows": "calc.exe", "darwin": "Calculator", "linux": "gnome-calculator"},
            "notepad": {"windows": "notepad.exe", "darwin": "TextEdit", "linux": "gedit"},
            "terminal": {"windows": "cmd.exe", "darwin": "Terminal", "linux": "gnome-terminal"},
            "safari": {"windows": None, "darwin": "Safari", "linux": None},
            "excel": {"windows": "excel.exe", "darwin": "Microsoft Excel", "linux": None},
            "word": {"windows": "winword.exe", "darwin": "Microsoft Word", "linux": None},
            "powerpoint": {"windows": "powerpnt.exe", "darwin": "Microsoft PowerPoint", "linux": None},
        }
        
        system = platform.system().lower()
        if system == "darwin":
            platform_key = "darwin"
        elif system == "windows":
            platform_key = "windows"
        else:
            platform_key = "linux"
        
        # Get the actual app name for this platform
        actual_app_name = app_mappings.get(app_name, {}).get(platform_key, app_name)
        
        if actual_app_name is None:
            return SkillResult(
                success=False,
                message=f"Sorry sir, {app_name} is not available on {system}."
            )
        
        try:
            if platform_key == "darwin":
                # macOS
                subprocess.Popen(["open", "-a", actual_app_name])
            elif platform_key == "windows":
                # Windows
                subprocess.Popen(["start", actual_app_name], shell=True)
            else:
                # Linux
                subprocess.Popen([actual_app_name])
            
            return SkillResult(
                success=True,
                message=f"Opening {app_name} for you, sir.",
                data={"app_name": app_name, "system": system}
            )
        
        except FileNotFoundError:
            return SkillResult(
                success=False,
                message=f"Sorry sir, I couldn't find {app_name} on your system."
            )
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"Sorry sir, I encountered an error while opening {app_name}: {str(e)}"
            )
