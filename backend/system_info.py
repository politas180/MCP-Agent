"""System information gathering for MCP Agent.

This module provides functions to gather essential system information
that will be included in the initial system prompt for the AI.
"""
from __future__ import annotations

import os
import platform
import sys
import socket
import psutil
from typing import Dict, Any

def get_system_info() -> str:
    """Gather essential system information and format it for the system prompt.
    
    Returns:
        A formatted string containing system information.
    """
    # Get basic system information
    system_info = f"""
SYSTEM INFORMATION:
- OS: {platform.system()} {platform.release()} {platform.version()}
- Architecture: {platform.machine()}
- Processor: {platform.processor()}
- Hostname: {socket.gethostname()}
- Username: {os.getlogin() if hasattr(os, 'getlogin') else 'unknown'}
- Python Version: {platform.python_version()}
- Current Directory: {os.getcwd()}
"""
    
    # Get memory information
    memory = psutil.virtual_memory()
    system_info += f"""
MEMORY:
- Total: {format_bytes(memory.total)}
- Available: {format_bytes(memory.available)}
- Used: {format_bytes(memory.used)} ({memory.percent}%)
"""

    # Get disk information
    disk = psutil.disk_usage('/')
    system_info += f"""
DISK:
- Total: {format_bytes(disk.total)}
- Free: {format_bytes(disk.free)}
- Used: {format_bytes(disk.used)} ({disk.percent}%)
"""

    # Get network information
    try:
        # Get primary IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        system_info += f"""
NETWORK:
- IP Address: {ip_address}
"""
    except:
        # If we can't get the IP address, skip this section
        pass

    return system_info

def format_bytes(bytes_value):
    """Format bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"
