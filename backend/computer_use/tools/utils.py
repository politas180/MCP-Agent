"""Utility functions for Computer Use tools."""
from __future__ import annotations

import re
import os
from typing import Dict, List, Any

def sanitize_python_code(code: str) -> str:
    """Sanitize Python code by removing markdown formatting.

    This function removes markdown code block formatting (backticks, language identifiers)
    and other common formatting elements that might be included by the LLM.

    Args:
        code: The potentially markdown-formatted Python code

    Returns:
        Clean Python code ready for execution
    """
    # Process the code line by line to handle various formatting issues
    lines = code.split('\n')
    cleaned_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # Skip lines that only contain "python", "Copy", or "Edit"
        if line.strip() in ['python', 'Copy', 'Edit']:
            continue

        # Handle code block start markers like ```python or ```py
        if re.match(r'^```\w*$', line.strip()):
            skip_next = False  # Reset in case there are multiple code blocks
            continue

        # Handle code block end markers
        if line.strip() == '```':
            continue

        # Add the line if it's not skipped
        if not skip_next:
            cleaned_lines.append(line)

    # Join the lines back together
    cleaned_code = '\n'.join(cleaned_lines).strip()

    # Handle the case where the entire code might still be wrapped in backticks
    if cleaned_code.startswith('```') and cleaned_code.endswith('```'):
        cleaned_code = cleaned_code[3:-3].strip()

    return cleaned_code

def safe_path(path: str) -> str:
    """Convert a path string to a safe format for Python execution.

    This function handles Windows path issues with backslashes by using
    raw strings or proper escaping to prevent Unicode escape errors.

    Args:
        path: The path string that might contain backslashes

    Returns:
        A path string that can be safely used in Python code
    """
    # Use os.path.normpath to standardize the path format for the current OS
    normalized_path = os.path.normpath(path)

    # For Windows paths, ensure backslashes are properly escaped
    if os.name == 'nt' and '\\' not in normalized_path and '\\\\' not in normalized_path:
        # Replace single backslashes with double backslashes
        safe_path_str = normalized_path.replace('\\', '\\\\')
        return safe_path_str

    return normalized_path
