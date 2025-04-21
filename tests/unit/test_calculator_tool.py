#!/usr/bin/env python
"""
Unit tests for the calculator tool functionality.
"""
import sys
import os
import unittest
import pytest

# Add the backend directory to the path so we can import the tools module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

from backend.tools import calculator, pretty_print_calculator_results


@pytest.mark.unit
@pytest.mark.tools
class TestCalculatorTool(unittest.TestCase):
    """Test cases for the calculator tool."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        # Test addition
        result = calculator("2 + 2")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 4)
        self.assertEqual(result["result_type"], "numeric")

        # Test subtraction
        result = calculator("10 - 5")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 5)

        # Test multiplication
        result = calculator("3 * 4")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 12)

        # Test division
        result = calculator("20 / 4")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 5.0)

        # Test modulo
        result = calculator("17 % 5")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 2)

        # Test exponentiation
        result = calculator("2 ** 3")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 8)

        # Test complex expression
        result = calculator("(2 + 3) * 4 / 2 - 1")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 9.0)

    def test_mathematical_functions(self):
        """Test mathematical functions from the math library."""
        # Test sin
        result = calculator("math.sin(math.pi/2)")
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 1.0, places=10)

        # Test cos
        result = calculator("math.cos(0)")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 1.0)

        # Test sqrt
        result = calculator("math.sqrt(16)")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 4.0)

        # Test log
        result = calculator("math.log(math.e)")
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 1.0, places=10)

        # Test constants
        result = calculator("math.pi")
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 3.14159265359, places=10)

    def test_numpy_operations(self):
        """Test numpy operations."""
        # Test array creation
        result = calculator("np.array([1, 2, 3, 4, 5])")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_type"], "array")
        self.assertEqual(result["result"], [1, 2, 3, 4, 5])

        # Test array operations
        result = calculator("np.array([1, 2, 3]) + np.array([4, 5, 6])")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], [5, 7, 9])

        # Test numpy functions
        result = calculator("np.mean([1, 2, 3, 4, 5])")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 3.0)

        # Test matrix operations
        result = calculator("np.dot(np.array([1, 2]), np.array([3, 4]))")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 11)

    def test_sympy_operations(self):
        """Test sympy operations."""
        # Test symbolic variables
        result = calculator("sympy.Symbol('x')")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_type"], "symbolic")
        self.assertEqual(result["result"], "x")

        # Test symbolic expressions
        result = calculator("x = sympy.Symbol('x'); x**2 + 2*x + 1")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result_type"], "symbolic")
        self.assertEqual(result["result"], "x**2 + 2*x + 1")

        # Test solving equations with sympy.solve
        result = calculator("x = sympy.Symbol('x'); sympy.solve(x**2 - 4, x)")
        self.assertEqual(result["status"], "success")
        # The result should be a list of solutions: [-2, 2]
        self.assertTrue("[-2, 2]" in result["result"] or "[2, -2]" in result["result"])

        # Test using solve directly
        result = calculator("x = Symbol('x'); solve(x**2 - 4, x)")
        self.assertEqual(result["status"], "success")
        # The result should be a list of solutions: [-2, 2]
        self.assertTrue("[-2, 2]" in result["result"] or "[2, -2]" in result["result"])

    def test_error_handling(self):
        """Test error handling for invalid expressions."""
        # Test division by zero
        result = calculator("1/0")
        self.assertEqual(result["status"], "error")
        self.assertIn("division by zero", result["message"].lower())

        # Test invalid syntax
        result = calculator("2 +* 3")
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result["message"].lower())

        # Test disallowed operations
        result = calculator("import os")
        self.assertEqual(result["status"], "error")
        self.assertIn("disallowed", result["message"].lower())

        result = calculator("open('file.txt')")
        self.assertEqual(result["status"], "error")
        self.assertIn("disallowed", result["message"].lower())

        result = calculator("__import__('os')")
        self.assertEqual(result["status"], "error")
        self.assertIn("disallowed", result["message"].lower())

    def test_pretty_print_calculator_results(self):
        """Test the pretty print function for calculator results."""
        # Test numeric result
        result = {
            "status": "success",
            "result": 42,
            "result_type": "numeric"
        }
        formatted = pretty_print_calculator_results(result)
        self.assertEqual(formatted, "Result: 42")

        # Test float result
        result = {
            "status": "success",
            "result": 3.14159265359,
            "result_type": "numeric"
        }
        formatted = pretty_print_calculator_results(result)
        self.assertEqual(formatted, "Result: 3.141592654")

        # Test symbolic result
        result = {
            "status": "success",
            "result": "x**2 + 2*x + 1",
            "result_type": "symbolic"
        }
        formatted = pretty_print_calculator_results(result)
        self.assertEqual(formatted, "Result: x**2 + 2*x + 1")

        # Test array result
        result = {
            "status": "success",
            "result": [1, 2, 3, 4, 5],
            "result_type": "array"
        }
        formatted = pretty_print_calculator_results(result)
        self.assertEqual(formatted, "Result (array):\n[1, 2, 3, 4, 5]")

        # Test error result
        result = {
            "status": "error",
            "message": "Error evaluating expression: division by zero"
        }
        formatted = pretty_print_calculator_results(result)
        self.assertEqual(formatted, "Error evaluating expression: division by zero")


if __name__ == '__main__':
    unittest.main()
