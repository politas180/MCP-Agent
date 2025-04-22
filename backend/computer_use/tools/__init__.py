"""Computer Use tools package for MCP Agent.

This package contains tools for the Computer Use mode, which allows users to
execute Python code and interact with their computer through a natural language interface.
"""
from __future__ import annotations

from typing import Dict, List, Any

# Import all tools and their schemas
from .python_execution import execute_python
from .terminal_execution import execute_terminal_command
from .schemas import EXECUTE_PYTHON_PARAMS_SCHEMA, EXECUTE_TERMINAL_PARAMS_SCHEMA, COMPUTER_TOOLS
from .formatting import pretty_print_execute_python_results, pretty_print_execute_terminal_results

# Tool implementations registry
COMPUTER_TOOL_IMPLS = {
    "execute_python": execute_python,
    "execute_terminal": execute_terminal_command
}

# Export all the necessary components
__all__ = [
    "COMPUTER_TOOLS",
    "COMPUTER_TOOL_IMPLS",
    "execute_python",
    "execute_terminal_command",
    "pretty_print_execute_python_results",
    "pretty_print_execute_terminal_results",
]
