"""Integration tests for system information in the app."""
import unittest
import os
import sys
import json
import platform
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app import get_system_prompt
from backend.system_info import get_system_info

class TestSystemInfoIntegration(unittest.TestCase):
    """Test cases for system information integration with the app."""

    def test_system_info_in_computer_use_prompt(self):
        """Test that system information is included in the computer use prompt."""
        # Get the system prompts
        prompts = get_system_prompt()
        computer_use_prompt = prompts["computer_use"]

        # Check that key system information sections are in the prompt
        self.assertIn("SYSTEM INFORMATION:", computer_use_prompt)
        self.assertIn("MEMORY:", computer_use_prompt)
        self.assertIn("DISK:", computer_use_prompt)

        # Check for specific system details
        self.assertIn(f"OS: {platform.system()}", computer_use_prompt)
        self.assertIn(f"Architecture: {platform.machine()}", computer_use_prompt)
        self.assertIn(f"Python Version: {platform.python_version()}", computer_use_prompt)

    def test_system_info_not_in_standard_prompt(self):
        """Test that system information is not included in the standard prompt."""
        # Get the system prompts
        prompts = get_system_prompt()
        standard_prompt = prompts["standard"]

        # Get the system info
        system_info = get_system_info()

        # Check that the system info is not included in the standard prompt
        self.assertNotIn(system_info, standard_prompt)

        # Check that key system information sections are not in the prompt
        self.assertNotIn("SYSTEM INFORMATION:", standard_prompt)
        self.assertNotIn("MEMORY:", standard_prompt)
        self.assertNotIn("DISK:", standard_prompt)

if __name__ == '__main__':
    unittest.main()
