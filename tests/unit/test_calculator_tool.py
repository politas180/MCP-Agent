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

    def test_safe_expressions_ast(self):
        """Test safe expressions that should pass AST validation."""
        safe_expressions = [
            "1 + 1",
            "2.0 - 3.5 * (4/2)",
            "math.sin(math.pi / 2)",
            "np.array([1, 2, 3]) + np.array([4,5,6])",
            "np.mean([1,2,3,4,5])",
            "sympy.Symbol('x')**2 + sympy.log(sympy.Symbol('y'))",
            "'hello' + ' ' + 'world'",
            "abs(-5)",
            "round(3.14159, 2)",
            "len([1, 2, 3])",
            "str(123)",
            "float('3.14')",
            "int(2.7)",
            "pow(2, 3)",
            "max(1, 5, 2)",
            "min(-1, -5, 0)",
            "{'a': 1, 'b': 2}['a']", # Dictionary access
            "[1, 2, 3][0]", # List access
            "(1, 2, 3)[1]", # Tuple access
            "True and False or None",
            "1 if True else 0",
            "complex(1, 2)",
            "divmod(10, 3)",
            "math.factorial(5)",
            "np.linalg.det(np.array([[1,2],[3,4]]))", # Example of submodule access
            "sympy.S.Reals", # Accessing sympy.S attributes
            "sympy.cos(sympy.pi).evalf()",
            "list(map(lambda x: x*x, [1,2,3]))", # Safe lambda use with map
            "sorted([3,1,2])"
        ]
        for expr in safe_expressions:
            with self.subTest(expression=expr):
                result = calculator(expr)
                self.assertEqual(result["status"], "success", f"Expression failed: {expr}, Message: {result.get('message')}")

    def test_unsafe_expressions_ast(self):
        """Test unsafe expressions that should be caught by AST validation."""
        unsafe_expressions = [
            "import os",
            "os.system('echo unsafe')", # AST should catch this if 'os' is not whitelisted for direct use
            "open('file.txt', 'w')",
            "eval('1+1')", # eval itself
            "exec('print(1)')", # exec itself
            "__import__('os').system('echo unsafe')",
            "lambda: os.system('echo unsafe')", # using os in lambda
            "lambda: __import__('os').system('echo unsafe')",
            "[x for x in [1,2] if __import__('os') is None]", # arbitrary call in list comprehension
            "getattr(obj, 'attr')", # getattr
            "setattr(obj, 'attr', 1)", # setattr
            "delattr(obj, 'attr')", # delattr
            "object.__subclasses__()[0].__init__.__globals__['__builtins__'].eval('1+1')", # complex attack
            "compile('1+1', '<string>', 'eval')", # compile
            "locals()", # locals
            "globals()", # globals
            "__builtins__['eval']('1+1')",
            "__builtins__.__dict__['eval']('print(1)')",
            "my_var = 1; my_var.__class__.__bases__[0].__subclasses__()[0].__init__.__globals__['sys'].exit(1)", # trying to access sys via object hierarchy
            "def my_func(): pass; my_func.__globals__['os']", # trying to access globals via function
            "a = {}; a.__setitem__('__builtins__', None)", # Modifying dict in a way that might affect builtins
            "(lambda x: x.__class__.__bases__[0].__subclasses__()) (0)", # trying to get all classes
            "foo.bar", # foo is not whitelisted
            "some_random_function()", # not whitelisted
            "math.non_existent_function()", # non-whitelisted attribute of whitelisted module
            "np.random.Generator(np.random.PCG64()).bytes(10)" # np.random.Generator not on list
        ]
        for expr in unsafe_expressions:
            with self.subTest(expression=expr):
                result = calculator(expr)
                self.assertEqual(result["status"], "error", f"Expression passed: {expr}")
                self.assertTrue(
                    "disallowed" in result["message"].lower() or \
                    "ast validation" in result["message"].lower() or \
                    "syntax error" in result["message"].lower(), # SyntaxError can also be a valid outcome for malformed unsafe attempts
                    f"Unexpected error message for {expr}: {result['message']}"
                )

    def test_expression_with_assignment_safety_ast(self):
        """Test safety for expressions with assignments (semicolon pattern)."""
        # Safe assignment, safe eval
        expr_safe_safe = "x = sympy.Symbol('x'); x**2 + 1"
        result = calculator(expr_safe_safe)
        self.assertEqual(result["status"], "success", f"Expression failed: {expr_safe_safe}, Message: {result.get('message')}")
        self.assertEqual(result["result"], "x**2 + 1")

        # Safe assignment, unsafe eval (caught by AST validation on the eval part)
        expr_safe_unsafe_eval = "x = 1; __import__('os')"
        result = calculator(expr_safe_unsafe_eval)
        self.assertEqual(result["status"], "error", f"Expression passed: {expr_safe_unsafe_eval}")
        self.assertIn("disallowed operation", result["message"].lower(), f"Message: {result['message']}") # AST error

        expr_safe_unsafe_eval_2 = "x = 1; open('file.txt')"
        result = calculator(expr_safe_unsafe_eval_2)
        self.assertEqual(result["status"], "error", f"Expression passed: {expr_safe_unsafe_eval_2}")
        self.assertIn("disallowed operation", result["message"].lower(), f"Message: {result['message']}") # AST error

        # Unsafe assignment (relies on safe_globals for exec), safe eval
        # The __import__ in exec part should be blocked by safe_globals not having __import__
        # If it somehow passed, _is_safe_expression for eval part would catch x.system if x was os module
        expr_unsafe_assign_safe_eval = "x = __import__('os'); x" # 'x' is eval part
        result = calculator(expr_unsafe_assign_safe_eval)
        # This error comes from 'exec' due to restricted globals
        self.assertEqual(result["status"], "error", f"Expression passed: {expr_unsafe_assign_safe_eval}")
        self.assertTrue(
            "name '__import__' is not defined" in result["message"].lower() or # From exec
            "disallowed" in result["message"].lower(), # Or from AST if x was somehow set to os
             f"Message: {result['message']}"
        )
        
        expr_unsafe_assign_unsafe_eval = "x = __import__('os'); x.system('echo unsafe')"
        result = calculator(expr_unsafe_assign_unsafe_eval)
        self.assertEqual(result["status"], "error", f"Expression passed: {expr_unsafe_assign_unsafe_eval}")
        # Error could be from exec (NameError for __import__) or from eval (AST validation for x.system)
        self.assertTrue(
            "name '__import__' is not defined" in result["message"].lower() or \
            "disallowed" in result["message"].lower(),
            f"Unexpected error message for {expr_unsafe_assign_unsafe_eval}: {result['message']}"
        )

        # Test that the var_part of exec cannot call __builtins__ directly
        expr_exec_builtins = "x = __builtins__; x"
        result = calculator(expr_exec_builtins)
        self.assertEqual(result["status"], "error")
        self.assertIn("name '__builtins__' is not defined", result["message"].lower())


if __name__ == '__main__':
    unittest.main()
