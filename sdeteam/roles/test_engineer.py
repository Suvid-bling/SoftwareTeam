#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TestEngineer role for TeamLeader mode.
Writes and executes tests under tests/ folder for any project.
"""

from pydantic import Field

from sdeteam.actions.di.run_command import RunCommand
from sdeteam.prompts.di.engineer2 import CURRENT_STATE
from sdeteam.roles.di.role_zero import RoleZero
from sdeteam.tools.libs.terminal import Terminal
from sdeteam.tools.tool_registry import register_tool


TEST_ENGINEER_INSTRUCTION = """
You are a Test Engineer responsible for writing and running tests.

## CRITICAL RULE - TEST FILE LOCATION
ALL test files MUST be saved under the tests/ subfolder of the project directory.
- If project is at calculator/, tests go to calculator/tests/
- If project is at 2048_game/, tests go to 2048_game/tests/
- DO NOT include "workspace/" in paths - just use project_name/tests/
- Create the tests/ folder first if it doesn't exist using: mkdir -p <project_name>/tests

Your workflow:
1. Read the source code files to understand what needs to be tested
2. Create a tests/ folder in the project directory: mkdir -p <project_name>/tests
3. Write comprehensive test files (test_*.py) using pytest, saving them to <project_name>/tests/
4. Run the tests using pytest and report results

Guidelines:
- ALWAYS create tests under <project_name>/tests/ subfolder
- Use pytest framework
- Test both happy paths and edge cases
- Include setup/teardown fixtures when needed
- Name test files as test_<module>.py
- After writing tests, run them with: pytest <project_name>/tests/ -v
- Add __init__.py to tests/ folder for proper imports

When you finish testing, report the test results to the team.
"""


@register_tool(include_functions=["run_tests"])
class TestEngineer(RoleZero):
    """Test Engineer role for writing and executing tests in TeamLeader mode."""
    
    name: str = "Tom"
    profile: str = "TestEngineer"
    goal: str = "Write comprehensive tests and ensure code quality through testing"
    instruction: str = TEST_ENGINEER_INSTRUCTION
    
    terminal: Terminal = Field(default_factory=Terminal, exclude=True)
    
    tools: list[str] = [
        "Plan",
        "Editor",
        "RoleZero",
        "Terminal:run_command",
        "TestEngineer",
    ]
    
    max_react_loop: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Watch for RunCommand messages from TeamLeader
        self._watch({RunCommand})
    
    def _update_tool_execution(self):
        self.tool_execution_map.update({
            "Terminal.run_command": self.terminal.run_command,
            "TestEngineer.run_tests": self.run_tests,
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
    
    async def run_tests(self, test_path: str = "tests/") -> str:
        """
        Run pytest on the specified test path.
        
        Args:
            test_path: Path to tests directory or specific test file. Defaults to "tests/".
        
        Returns:
            Test execution output.
        """
        cmd = f"pytest {test_path} -v --tb=short"
        output = await self.terminal.run_command(cmd)
        return f"Test Results:\n{output}"
