"""Unit tests for Computer Use tools."""
import os
import sys
import unittest
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.computer_use.tools import (
    execute_python,
    get_system_info,
    list_files,
    read_file,
    pretty_print_execute_python_results,
    pretty_print_system_info,
    pretty_print_list_files,
    pretty_print_read_file
)


@pytest.mark.unit
@pytest.mark.computer_use
class TestComputerUseTools(unittest.TestCase):
    """Test cases for Computer Use tools."""

    def test_execute_python_success(self):
        """Test executing Python code successfully."""
        code = """
result = 2 + 2
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["output"], "4")
        self.assertEqual(result["variables"]["result"], "4")

    def test_execute_python_error(self):
        """Test executing Python code with an error."""
        code = """
result = 1 / 0
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("division by zero", result["message"])

    def test_execute_python_dangerous_code(self):
        """Test executing Python code with dangerous operations."""
        code = """
import shutil
shutil.rmtree('/tmp/test')
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("dangerous operation", result["message"])

    @patch('platform.platform')
    @patch('platform.system')
    @patch('platform.release')
    @patch('platform.version')
    @patch('platform.machine')
    @patch('platform.processor')
    @patch('platform.python_version')
    @patch('os.getlogin')
    @patch('os.path.expanduser')
    @patch('os.getcwd')
    def test_get_system_info(self, mock_getcwd, mock_expanduser, mock_getlogin,
                            mock_python_version, mock_processor, mock_machine,
                            mock_version, mock_release, mock_system, mock_platform):
        """Test getting system information."""
        # Set up mocks
        mock_platform.return_value = "Windows-10-10.0.19041-SP0"
        mock_system.return_value = "Windows"
        mock_release.return_value = "10"
        mock_version.return_value = "10.0.19041"
        mock_machine.return_value = "AMD64"
        mock_processor.return_value = "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
        mock_python_version.return_value = "3.9.7"
        mock_getlogin.return_value = "testuser"
        mock_expanduser.return_value = "C:\\Users\\testuser"
        mock_getcwd.return_value = "D:\\AI\\MCP\\DuckDuckGo"

        result = get_system_info()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["info"]["platform"], "Windows-10-10.0.19041-SP0")
        self.assertEqual(result["info"]["system"], "Windows")
        self.assertEqual(result["info"]["release"], "10")
        self.assertEqual(result["info"]["version"], "10.0.19041")
        self.assertEqual(result["info"]["machine"], "AMD64")
        self.assertEqual(result["info"]["processor"], "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel")
        self.assertEqual(result["info"]["python_version"], "3.9.7")
        self.assertEqual(result["info"]["username"], "testuser")
        self.assertEqual(result["info"]["home_directory"], "C:\\Users\\testuser")
        self.assertEqual(result["info"]["current_directory"], "D:\\AI\\MCP\\DuckDuckGo")

    @patch('os.path.exists')
    @patch('os.path.abspath')
    @patch('os.listdir')
    @patch('os.path.isdir')
    @patch('os.path.expanduser')
    def test_list_files(self, mock_expanduser, mock_isdir, mock_listdir, mock_abspath, mock_exists):
        """Test listing files and directories."""
        # Set up mocks
        mock_expanduser.return_value = "/home/testuser"
        mock_abspath.return_value = "/home/testuser/test"
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.py", "dir1", "dir2"]

        # Mock isdir to return True for directories and False for files
        def mock_isdir_side_effect(path):
            return "dir" in os.path.basename(path)

        mock_isdir.side_effect = mock_isdir_side_effect

        result = list_files("~/test")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["path"], "/home/testuser/test")
        self.assertEqual(set(result["files"]), {"file1.txt", "file2.py"})
        self.assertEqual(set(result["directories"]), {"dir1", "dir2"})

    @patch('os.path.exists')
    @patch('os.path.abspath')
    @patch('os.path.isfile')
    @patch('os.path.expanduser')
    def test_read_file_nonexistent(self, mock_expanduser, mock_isfile, mock_abspath, mock_exists):
        """Test reading a nonexistent file."""
        # Set up mocks
        mock_expanduser.return_value = "/home/testuser"
        mock_abspath.return_value = "/home/testuser/test.txt"
        mock_exists.return_value = False
        mock_isfile.return_value = True

        result = read_file("~/test.txt")
        self.assertEqual(result["status"], "error")
        self.assertIn("does not exist", result["message"])

    @patch('os.path.exists')
    @patch('os.path.abspath')
    @patch('os.path.isfile')
    @patch('os.path.expanduser')
    def test_read_file_not_a_file(self, mock_expanduser, mock_isfile, mock_abspath, mock_exists):
        """Test reading a path that is not a file."""
        # Set up mocks
        mock_expanduser.return_value = "/home/testuser"
        mock_abspath.return_value = "/home/testuser/dir"
        mock_exists.return_value = True
        mock_isfile.return_value = False

        result = read_file("~/dir")
        self.assertEqual(result["status"], "error")
        self.assertIn("not a file", result["message"])

    @patch('os.path.exists')
    @patch('os.path.abspath')
    @patch('os.path.isfile')
    @patch('os.path.expanduser')
    @patch('builtins.open')
    def test_read_file_success(self, mock_open, mock_expanduser, mock_isfile, mock_abspath, mock_exists):
        """Test reading a file successfully."""
        # Set up mocks
        mock_expanduser.return_value = "/home/testuser"
        mock_abspath.return_value = "/home/testuser/test.txt"
        mock_exists.return_value = True
        mock_isfile.return_value = True

        # Mock file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "Test file content"
        mock_open.return_value = mock_file

        result = read_file("~/test.txt")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["path"], "/home/testuser/test.txt")
        self.assertEqual(result["content"], "Test file content")

    def test_pretty_print_execute_python_results(self):
        """Test pretty printing execute_python results."""
        result = {
            "status": "success",
            "output": "4",
            "variables": {"result": "4", "x": "2", "y": "2"}
        }
        output = pretty_print_execute_python_results(result)
        self.assertIn("Output: 4", output)
        self.assertIn("Variables:", output)
        self.assertIn("- result: 4", output)
        self.assertIn("- x: 2", output)
        self.assertIn("- y: 2", output)

    def test_pretty_print_system_info(self):
        """Test pretty printing system_info results."""
        result = {
            "status": "success",
            "info": {
                "platform": "Windows-10",
                "system": "Windows",
                "python_version": "3.9.7"
            }
        }
        output = pretty_print_system_info(result)
        self.assertIn("System Information:", output)
        self.assertIn("- platform: Windows-10", output)
        self.assertIn("- system: Windows", output)
        self.assertIn("- python_version: 3.9.7", output)

    def test_pretty_print_list_files(self):
        """Test pretty printing list_files results."""
        result = {
            "status": "success",
            "path": "/home/user",
            "files": ["file1.txt", "file2.py"],
            "directories": ["dir1", "dir2"]
        }
        output = pretty_print_list_files(result)
        self.assertIn("Contents of /home/user:", output)
        self.assertIn("Directories:", output)
        self.assertIn("- 📁 dir1", output)
        self.assertIn("- 📁 dir2", output)
        self.assertIn("Files:", output)
        self.assertIn("- 📄 file1.txt", output)
        self.assertIn("- 📄 file2.py", output)

    def test_pretty_print_read_file(self):
        """Test pretty printing read_file results."""
        result = {
            "status": "success",
            "path": "/home/user/test.txt",
            "content": "Test file content"
        }
        output = pretty_print_read_file(result)
        self.assertIn("Contents of file /home/user/test.txt:", output)
        self.assertIn("Test file content", output)


if __name__ == '__main__':
    unittest.main()
