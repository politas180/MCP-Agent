"""Formatting functions for Computer Use tools."""
from __future__ import annotations

from typing import Dict, Any

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


