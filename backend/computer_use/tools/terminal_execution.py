"""Terminal command execution tool implementation."""
from __future__ import annotations

import os
import subprocess
import sys
import platform
from typing import Dict, List, Any

def execute_terminal_command(command: str) -> Dict[str, Any]:
    """Execute a terminal command without restrictions.

    This tool allows executing any command in the system's command prompt or terminal.
    It provides full access to the system through command line operations.

    Args:
        command: The terminal command to execute

    Returns:
        A dictionary with the execution result or error message
    """
    try:
        # Determine the shell to use based on the platform
        use_shell = True
        if platform.system() == "Windows":
            # On Windows, we'll use cmd.exe
            shell_cmd = command
        else:
            # On Unix-like systems, we'll use bash
            shell_cmd = command

        # Execute the command
        process = subprocess.Popen(
            shell_cmd,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Get the output
        stdout, stderr = process.communicate()
        return_code = process.returncode

        # Prepare the result
        result = {
            "status": "success" if return_code == 0 else "error",
            "output": stdout,
            "error_output": stderr,
            "return_code": return_code
        }

        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing command: {str(e)}",
            "output": "",
            "error_output": str(e),
            "return_code": -1
        }
