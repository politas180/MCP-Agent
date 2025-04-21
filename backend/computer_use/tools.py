"""Python code execution tool implementation."""
from __future__ import annotations

import os
import platform
import subprocess
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Any

# ────────────────────────────────────────────────────────────────────────────────
# Tool implementations
# ────────────────────────────────────────────────────────────────────────────────

def execute_python(code: str) -> Dict[str, Any]:
    """Execute Python code in a controlled environment.

    This tool allows executing Python code with access to common libraries for
    data analysis, visualization, and system automation. It provides a sandbox
    for running Python code through a natural language interface.

    Args:
        code: The Python code to execute

    Returns:
        A dictionary with the execution result or error message
    """
    # No restrictions on code execution

    # Capture stdout to include print statements in the output
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    # Capture matplotlib figures if generated
    figure_data = None

    try:
        # Use globals() to allow access to all modules
        safe_globals = globals()

        # Create a local namespace for execution
        local_namespace = {}

        # Redirect stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            # Execute the code
            exec(code, safe_globals, local_namespace)

            # Check if there are any matplotlib figures to capture
            if plt.get_fignums():
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                figure_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close('all')
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        # Get stdout and stderr content
        stdout_content = stdout_capture.getvalue()
        stderr_content = stderr_capture.getvalue()

        # Prepare the result
        result = {
            "status": "success",
            "output": stdout_content if stdout_content else str(local_namespace.get("result", "Code executed successfully")),
            "variables": {k: str(v) for k, v in local_namespace.items() if not k.startswith("_")},
            "error_output": stderr_content if stderr_content else None
        }

        # Add figure data if available
        if figure_data:
            result["figure"] = figure_data

        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing code: {str(e)}"
        }



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

COMPUTER_TOOL_IMPLS = {
    "execute_python": execute_python
}

# ────────────────────────────────────────────────────────────────────────────────
# Helper functions for pretty printing
# ────────────────────────────────────────────────────────────────────────────────

def pretty_print_execute_python_results(result: Dict[str, Any]) -> str:
    """Format execute_python results for display."""
    if result.get("status") == "error":
        return f"Error: {result.get('message', 'Unknown error')}"

    output = result.get("output", "")
    variables = result.get("variables", {})
    error_output = result.get("error_output")
    figure = result.get("figure")

    formatted = ""

    # Add output
    if output and output != "Code executed successfully":
        formatted += f"{output}\n\n"

    # Add error output if any
    if error_output:
        formatted += f"Errors/Warnings:\n{error_output}\n\n"

    # Add figure if available
    if figure:
        formatted += f"<img src=\"data:image/png;base64,{figure}\" />\n\n"

    # Add variables if any
    if variables:
        formatted += "Variables:\n"
        for name, value in variables.items():
            if name != "result":
                formatted += f"- {name}: {value}\n"

    return formatted
