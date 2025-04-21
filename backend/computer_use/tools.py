"""Computer Use tools implementation."""
from __future__ import annotations

import os
import platform
import subprocess
import sys
from typing import Dict, List, Any

# ────────────────────────────────────────────────────────────────────────────────
# Tool implementations
# ────────────────────────────────────────────────────────────────────────────────

def execute_python(code: str) -> Dict[str, Any]:
    """Execute Python code in a controlled environment.
    
    This tool allows executing Python code with access to common libraries for
    computer control like os, subprocess, platform, etc. It provides a sandbox
    for computer automation tasks.
    
    Args:
        code: The Python code to execute
        
    Returns:
        A dictionary with the execution result or error message
    """
    # Check for potentially dangerous operations
    dangerous_patterns = [
        "import shutil",
        "shutil.rmtree",
        "os.remove",
        "os.unlink",
        "os.rmdir",
        "__import__('shutil')",
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                "status": "error",
                "message": f"Code contains potentially dangerous operation: {pattern}"
            }
    
    try:
        # Create a dictionary of allowed modules
        safe_globals = {
            "os": os,
            "platform": platform,
            "subprocess": subprocess,
            "sys": sys,
        }
        
        # Create a local namespace for execution
        local_namespace = {}
        
        # Execute the code
        exec(code, safe_globals, local_namespace)
        
        # Prepare the result
        result = {
            "status": "success",
            "output": str(local_namespace.get("result", "Code executed successfully")),
            "variables": {k: str(v) for k, v in local_namespace.items() if not k.startswith("_")}
        }
        
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing code: {str(e)}"
        }

def get_system_info() -> Dict[str, Any]:
    """Get information about the system.
    
    Returns:
        A dictionary with system information
    """
    try:
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "username": os.getlogin(),
            "home_directory": os.path.expanduser("~"),
            "current_directory": os.getcwd(),
        }
        
        return {
            "status": "success",
            "info": info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting system info: {str(e)}"
        }

def list_files(path: str = ".") -> Dict[str, Any]:
    """List files and directories in the specified path.
    
    Args:
        path: The path to list files from (default: current directory)
        
    Returns:
        A dictionary with the list of files and directories
    """
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
            
        # Get absolute path
        abs_path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(abs_path):
            return {
                "status": "error",
                "message": f"Path does not exist: {abs_path}"
            }
            
        # List files and directories
        items = os.listdir(abs_path)
        
        # Separate files and directories
        files = []
        directories = []
        
        for item in items:
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)
                
        return {
            "status": "success",
            "path": abs_path,
            "files": files,
            "directories": directories
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing files: {str(e)}"
        }

def read_file(path: str) -> Dict[str, Any]:
    """Read the contents of a file.
    
    Args:
        path: The path to the file to read
        
    Returns:
        A dictionary with the file contents
    """
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
            
        # Get absolute path
        abs_path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(abs_path):
            return {
                "status": "error",
                "message": f"File does not exist: {abs_path}"
            }
            
        # Check if it's a file
        if not os.path.isfile(abs_path):
            return {
                "status": "error",
                "message": f"Path is not a file: {abs_path}"
            }
            
        # Read file contents
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {
            "status": "success",
            "path": abs_path,
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading file: {str(e)}"
        }

# ────────────────────────────────────────────────────────────────────────────────
# Tool schemas
# ────────────────────────────────────────────────────────────────────────────────

EXECUTE_PYTHON_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "The Python code to execute.",
        },
    },
    "required": ["code"],
}

GET_SYSTEM_INFO_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {},
    "required": [],
}

LIST_FILES_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The path to list files from (default: current directory).",
            "default": ".",
        },
    },
    "required": [],
}

READ_FILE_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The path to the file to read.",
        },
    },
    "required": ["path"],
}

# ────────────────────────────────────────────────────────────────────────────────
# Tool definitions
# ────────────────────────────────────────────────────────────────────────────────

COMPUTER_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute Python code for computer control tasks.",
            "parameters": EXECUTE_PYTHON_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get information about the system.",
            "parameters": GET_SYSTEM_INFO_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in the specified path.",
            "parameters": LIST_FILES_PARAMS_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": READ_FILE_PARAMS_SCHEMA,
        },
    },
]

COMPUTER_TOOL_IMPLS = {
    "execute_python": execute_python,
    "get_system_info": get_system_info,
    "list_files": list_files,
    "read_file": read_file,
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
    
    formatted = f"Output: {output}\n\n"
    
    if variables:
        formatted += "Variables:\n"
        for name, value in variables.items():
            formatted += f"- {name}: {value}\n"
    
    return formatted

def pretty_print_system_info(result: Dict[str, Any]) -> str:
    """Format system_info results for display."""
    if result.get("status") == "error":
        return f"Error: {result.get('message', 'Unknown error')}"
    
    info = result.get("info", {})
    
    formatted = "System Information:\n"
    for key, value in info.items():
        formatted += f"- {key}: {value}\n"
    
    return formatted

def pretty_print_list_files(result: Dict[str, Any]) -> str:
    """Format list_files results for display."""
    if result.get("status") == "error":
        return f"Error: {result.get('message', 'Unknown error')}"
    
    path = result.get("path", "")
    directories = result.get("directories", [])
    files = result.get("files", [])
    
    formatted = f"Contents of {path}:\n\n"
    
    if directories:
        formatted += "Directories:\n"
        for directory in sorted(directories):
            formatted += f"- 📁 {directory}\n"
        formatted += "\n"
    
    if files:
        formatted += "Files:\n"
        for file in sorted(files):
            formatted += f"- 📄 {file}\n"
    
    if not directories and not files:
        formatted += "Directory is empty."
    
    return formatted

def pretty_print_read_file(result: Dict[str, Any]) -> str:
    """Format read_file results for display."""
    if result.get("status") == "error":
        return f"Error: {result.get('message', 'Unknown error')}"
    
    path = result.get("path", "")
    content = result.get("content", "")
    
    formatted = f"Contents of file {path}:\n\n```\n{content}\n```"
    
    return formatted
