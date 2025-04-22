"""Terminal command execution tool implementation."""
from __future__ import annotations

import os
import subprocess
import platform
from typing import Dict, Any

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
            # On Windows, we'll use cmd.exe with /c flag to execute the command
            # This ensures proper command execution in Windows environment
            shell_cmd = f"cmd.exe /c {command}"
        else:
            # On Unix-like systems, we'll use bash
            shell_cmd = command

        # Execute the command
        process = subprocess.Popen(
            shell_cmd,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()  # Explicitly set the current working directory
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
