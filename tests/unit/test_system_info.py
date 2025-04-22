"""Unit tests for the system_info module."""
import unittest
import os
import platform
import socket
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.system_info import get_system_info, format_bytes

class TestSystemInfo(unittest.TestCase):
    """Test cases for the system_info module."""

    def test_get_system_info(self):
        """Test that get_system_info returns a properly formatted string with system information."""
        system_info = get_system_info()
        
        # Check that the system info is a non-empty string
        self.assertIsInstance(system_info, str)
        self.assertTrue(len(system_info) > 0)
        
        # Check that it contains the expected sections
        self.assertIn("SYSTEM INFORMATION:", system_info)
        self.assertIn("MEMORY:", system_info)
        self.assertIn("DISK:", system_info)
        
        # Check that it contains the correct OS information
        self.assertIn(f"OS: {platform.system()}", system_info)
        self.assertIn(f"Architecture: {platform.machine()}", system_info)
        self.assertIn(f"Hostname: {socket.gethostname()}", system_info)
        
        # Check that it contains the Python version
        self.assertIn(f"Python Version: {platform.python_version()}", system_info)
        
        # Check that it contains the current directory
        self.assertIn(f"Current Directory: {os.getcwd()}", system_info)
        
        # Check memory and disk information format
        self.assertTrue(re.search(r"Total: \d+\.\d+ [KMGT]B", system_info))
        self.assertTrue(re.search(r"Available: \d+\.\d+ [KMGT]B", system_info))
        self.assertTrue(re.search(r"Used: \d+\.\d+ [KMGT]B \(\d+\.\d+%\)", system_info))

    def test_format_bytes(self):
        """Test the format_bytes function."""
        # Test various byte values
        self.assertEqual(format_bytes(500), "500.00 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.00 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.00 GB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 1024), "1.00 TB")
        
        # Test a more complex value
        self.assertEqual(format_bytes(1536 * 1024), "1.50 MB")

if __name__ == '__main__':
    unittest.main()
