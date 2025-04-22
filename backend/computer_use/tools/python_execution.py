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

from .utils import sanitize_python_code

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
    
    # Sanitize the code to remove markdown formatting
    code = sanitize_python_code(code)

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
