"""Unit tests for Terminal execution tool."""
import os
import sys
import unittest
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.computer_use.tools import (
    execute_terminal_command,
    pretty_print_execute_terminal_results
)


@pytest.mark.unit
@pytest.mark.computer_use
class TestTerminalExecutionTool(unittest.TestCase):
    """Test cases for Terminal execution tool."""

    @patch('subprocess.Popen')
    def test_execute_terminal_success(self, mock_popen):
        """Test executing terminal command successfully."""
        # Mock the Popen instance
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Command output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # Execute a simple command
        result = execute_terminal_command("echo Hello, World!")
        
        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "Command output")
        self.assertEqual(result["return_code"], 0)

    @patch('subprocess.Popen')
    def test_execute_terminal_error(self, mock_popen):
        """Test executing terminal command with an error."""
        # Mock the Popen instance
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "Command not found")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # Execute a command that should fail
        result = execute_terminal_command("invalid_command")
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_output"], "Command not found")
        self.assertEqual(result["return_code"], 1)

    @patch('subprocess.Popen')
    def test_execute_terminal_exception(self, mock_popen):
        """Test executing terminal command with an exception."""
        # Mock Popen to raise an exception
        mock_popen.side_effect = Exception("Test exception")

        # Execute a command that should raise an exception
        result = execute_terminal_command("echo Hello")
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Test exception", result["message"])
        self.assertEqual(result["return_code"], -1)

    def test_pretty_print_execute_terminal_results_success(self):
        """Test pretty printing terminal execution results."""
        result = {
            "status": "success",
            "output": "Hello, World!",
            "error_output": "",
            "return_code": 0
        }
        output = pretty_print_execute_terminal_results(result)
        self.assertIn("Command Output:", output)
        self.assertIn("Hello, World!", output)
        self.assertIn("Return Code: 0", output)

    def test_pretty_print_execute_terminal_results_error(self):
        """Test pretty printing terminal execution results with errors."""
        result = {
            "status": "error",
            "message": "Command execution failed",
            "output": "",
            "error_output": "Command not found",
            "return_code": 1
        }
        output = pretty_print_execute_terminal_results(result)
        self.assertIn("Error:", output)
        self.assertIn("Command execution failed", output)


if __name__ == '__main__':
    unittest.main()
