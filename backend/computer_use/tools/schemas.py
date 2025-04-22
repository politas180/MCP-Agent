"""Schema definitions for Computer Use tools."""
from __future__ import annotations

from typing import Dict, List, Any

# ────────────────────────────────────────────────────────────────────────────────
# Tool schemas
# ────────────────────────────────────────────────────────────────────────────────

EXECUTE_PYTHON_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "The Python code to execute. You can use any Python libraries and perform any operations including file system operations.",
        },
    },
    "required": ["code"],
}

EXECUTE_TERMINAL_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The terminal command to execute. This can be any command that would normally be run in the command prompt or terminal.",
        },
    },
    "required": ["command"],
}

# ────────────────────────────────────────────────────────────────────────────────
# Tool definitions
# ────────────────────────────────────────────────────────────────────────────────

COMPUTER_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute any Python code without restrictions. You can perform file operations, system calls, and use any available Python libraries.",
            "parameters": EXECUTE_PYTHON_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_terminal",
            "description": "Execute any terminal command without restrictions. This allows running commands in the system's command prompt or terminal.",
            "parameters": EXECUTE_TERMINAL_PARAMS_SCHEMA,
        },
    }
]
