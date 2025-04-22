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
    }
]
