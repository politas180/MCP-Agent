"""Unit tests for Python execution tool."""
import os
import sys
import unittest
import pytest
import io
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.computer_use.tools import (
    execute_python,
    pretty_print_execute_python_results
)
from backend.computer_use.tools.utils import sanitize_python_code


@pytest.mark.unit
@pytest.mark.computer_use
class TestPythonExecutionTool(unittest.TestCase):
    """Test cases for Python execution tool."""

    def test_execute_python_success(self):
        """Test executing Python code successfully."""
        code = """
result = 2 + 2
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertTrue("4" in result["output"] or result["variables"]["result"] == "4")

    def test_execute_python_error(self):
        """Test executing Python code with an error."""
        code = """
result = 1 / 0
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("division by zero", result["message"])

    def test_execute_python_with_imports(self):
        """Test executing Python code with various imports."""
        code = """
import shutil
import os
result = "Successfully imported modules"
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["variables"]["result"], "Successfully imported modules")

    def test_execute_python_with_print(self):
        """Test executing Python code with print statements."""
        code = """
print("Hello, world!")
result = 42
"""
        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertIn("Hello, world!", result["output"])
        self.assertEqual(result["variables"]["result"], "42")

    @patch('matplotlib.pyplot.savefig')
    def test_execute_python_with_matplotlib(self, mock_savefig):
        """Test executing Python code with matplotlib."""
        # This test verifies that matplotlib figures are captured
        code = """
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1, 2, 3, 4])
plt.title('Test Plot')
result = "Plot created"
"""
        # Mock the savefig method
        mock_savefig.return_value = None

        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["variables"]["result"], "Plot created")
        # Verify savefig was called (figure was captured)
        mock_savefig.assert_called_once()

    def test_pretty_print_execute_python_results(self):
        """Test pretty printing execute_python results."""
        result = {
            "status": "success",
            "output": "Hello, world!",
            "variables": {"result": "42", "x": "2", "y": "2"},
            "error_output": None
        }
        output = pretty_print_execute_python_results(result)
        self.assertIn("Hello, world!", output)
        self.assertIn("Variables:", output)
        self.assertIn("- x: 2", output)
        self.assertIn("- y: 2", output)

    def test_pretty_print_execute_python_with_error(self):
        """Test pretty printing execute_python results with errors."""
        result = {
            "status": "success",
            "output": "Some output",
            "variables": {"x": "2"},
            "error_output": "Warning: something went wrong"
        }
        output = pretty_print_execute_python_results(result)
        self.assertIn("Some output", output)
        self.assertIn("Errors/Warnings:", output)
        self.assertIn("Warning: something went wrong", output)

    def test_pretty_print_execute_python_with_figure(self):
        """Test pretty printing execute_python results with figure."""
        result = {
            "status": "success",
            "output": "Plot created",
            "variables": {"result": "Plot created"},
            "figure": "base64encodeddata"
        }
        output = pretty_print_execute_python_results(result)
        self.assertIn("Plot created", output)
        self.assertIn("<img src=\"data:image/png;base64,base64encodeddata\" />", output)

    def test_sanitize_python_code_markdown_block(self):
        """Test sanitizing Python code with markdown code block formatting."""
        code = """```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(-2 * np.pi, 2 * np.pi, 1000)
s = np.sin(t)

plt.figure(figsize=(8, 5))
plt.plot(t, s, label='sin(t)', color='blue')
plt.title('Sine Wave from -2π to 2π')
plt.xlabel('t (radians)')
plt.ylabel('sin(t)')
plt.legend()

image_path = 'sine_wave.png'
plt.savefig(image_path, dpi=300)
plt.close()
```"""
        sanitized = sanitize_python_code(code)
        self.assertNotIn("```python", sanitized)
        self.assertNotIn("```", sanitized)
        self.assertIn("import numpy as np", sanitized)
        self.assertIn("plt.savefig(image_path, dpi=300)", sanitized)

    def test_sanitize_python_code_with_extra_text(self):
        """Test sanitizing Python code with extra text like 'python', 'Copy', 'Edit'."""
        code = """python
Copy
Edit
```py
print('Hello, world!')
result = 42
```"""
        sanitized = sanitize_python_code(code)
        self.assertNotIn("python", sanitized)
        self.assertNotIn("Copy", sanitized)
        self.assertNotIn("Edit", sanitized)
        self.assertNotIn("```py", sanitized)
        self.assertNotIn("```", sanitized)
        self.assertIn("print('Hello, world!')", sanitized)
        self.assertIn("result = 42", sanitized)

    def test_execute_python_with_markdown_formatting(self):
        """Test executing Python code with markdown formatting."""
        code = """```python
result = 2 + 2
```"""
        result = execute_python(code)
        self.assertEqual(result["status"], "success")
        self.assertTrue("4" in result["output"] or result["variables"]["result"] == "4")


if __name__ == '__main__':
    unittest.main()
