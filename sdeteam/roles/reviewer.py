#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reviewer role for TeamLeader mode.
Reviews code and writes code-review.md under review/ folder.
"""

from pydantic import Field

from sdeteam.actions.di.run_command import RunCommand
from sdeteam.prompts.di.engineer2 import CURRENT_STATE
from sdeteam.roles.di.role_zero import RoleZero
from sdeteam.tools.libs.terminal import Terminal
from sdeteam.tools.tool_registry import register_tool


REVIEWER_INSTRUCTION = """
You are a Code Reviewer responsible for reviewing code and documenting findings.

## CRITICAL RULE - REVIEW FILE LOCATION
ALL review files MUST be saved under the review/ subfolder of the project directory.
- If project is at calculator/, reviews go to calculator/review/
- If project is at 2048_game/, reviews go to 2048_game/review/
- DO NOT include "workspace/" in paths - just use project_name/review/
- Create the review/ folder first if it doesn't exist using: mkdir -p <project_name>/review

Your workflow:
1. Read the source code files to understand the codebase
2. Create a review/ folder in the project directory: mkdir -p <project_name>/review
3. Analyze code quality, potential bugs, security issues, and improvements
4. Write a comprehensive code-review.md file to <project_name>/review/code-review.md

Guidelines for code-review.md:
- ALWAYS create review under <project_name>/review/ subfolder
- Include sections: Overview, Code Quality, Potential Issues, Security Concerns, Recommendations
- Be specific with file names and line numbers when pointing out issues
- Provide actionable suggestions for improvements
- Rate overall code quality (1-10)

When you finish reviewing, report the findings summary to the team.
"""


@register_tool(include_functions=["generate_review"])
class Reviewer(RoleZero):
    """Reviewer role for code review in TeamLeader mode."""
    
    name: str = "Ryan"
    profile: str = "Reviewer"
    goal: str = "Review code quality and document findings in code-review.md"
    instruction: str = REVIEWER_INSTRUCTION
    
    terminal: Terminal = Field(default_factory=Terminal, exclude=True)
    
    tools: list[str] = [
        "Plan",
        "Editor",
        "RoleZero",
        "Terminal:run_command",
        "Reviewer",
    ]
    
    max_react_loop: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._watch({RunCommand})
    
    def _update_tool_execution(self):
        self.tool_execution_map.update({
            "Terminal.run_command": self.terminal.run_command,
            "Reviewer.generate_review": self.generate_review,
        })
    
    async def _format_instruction(self):
        """Display current terminal and editor state."""
        current_directory = (await self.terminal.run_command("pwd")).strip()
        
        # Use current directory as working dir for editor
        self.editor._set_workdir(current_directory)
        
        state = {
            "editor_open_file": self.editor.current_file,
            "current_directory": current_directory,
        }
        self.cmd_prompt_current_state = CURRENT_STATE.format(**state).strip()
    
    async def _think(self) -> bool:
        await self._format_instruction()
        return await super()._think()
    
    async def generate_review(self, project_path: str) -> str:
        """
        Generate a code review template for the specified project.
        
        Args:
            project_path: Path to the project directory to review.
        
        Returns:
            Confirmation message.
        """
        review_dir = f"{project_path}/review"
        await self.terminal.run_command(f"mkdir -p {review_dir}")
        return f"Review directory created at {review_dir}. Now analyze the code and write code-review.md."
