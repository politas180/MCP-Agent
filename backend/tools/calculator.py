"""Calculator tool implementation."""
from __future__ import annotations

import math
import re
from typing import Any, Dict

import numpy as np
import sympy

def calculator(expression: str) -> Dict[str, Any]:
    """Evaluate a Python expression using math, numpy, and sympy libraries.

    This tool allows executing mathematical expressions and using functions from
    the math, numpy, and sympy libraries. It provides a safe sandbox for
    mathematical calculations.

    Args:
        expression: The Python expression to evaluate

    Returns:
        A dictionary with the result or error message
    """
    # Special case for __import__ which is a security risk
    if "__import__" in expression:
        return {
            "status": "error",
            "message": "Expression contains disallowed operations."
        }

    try:
        # Validate the expression to ensure it only contains allowed characters
        if not _is_safe_expression(expression):
            return {
                "status": "error",
                "message": "Expression contains disallowed characters or operations."
            }

        # Create a safe environment with only the allowed modules and functions
        # We need to include a minimal set of builtins for basic operations
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
            'enumerate': enumerate, 'filter': filter, 'float': float, 'int': int,
            'isinstance': isinstance, 'len': len, 'list': list, 'map': map,
            'max': max, 'min': min, 'range': range, 'round': round, 'set': set,
            'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple, 'zip': zip
        }

        safe_globals = {
            "__builtins__": safe_builtins,
            "math": math,
            "np": np,
            "sympy": sympy,
            # Common sympy functions and classes
            "Symbol": sympy.Symbol,
            "symbols": sympy.symbols,
            "solve": sympy.solve,
            "expand": sympy.expand,
            "factor": sympy.factor,
            "simplify": sympy.simplify,
            "integrate": sympy.integrate,
            "diff": sympy.diff,
            "Matrix": sympy.Matrix,
            "Eq": sympy.Eq,
            # Common math functions
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "exp": math.exp,
            "log": math.log,
            "log10": math.log10,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "e": math.e,
        }

        # Execute the expression
        # Special handling for expressions with semicolons
        if ";" in expression:
            # Split the expression into parts
            parts = expression.split(";", 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                expr_part = parts[1].strip()

                # Execute the variable assignment
                local_vars = {}
                exec(var_part, safe_globals, local_vars)

                # Then evaluate the expression with the local variables
                result = eval(expr_part, safe_globals, local_vars)
            else:
                result = eval(expression, safe_globals, {})
        else:
            result = eval(expression, safe_globals, {})

        # Handle different result types
        if isinstance(result, (int, float, np.int64, np.float64)):
            # Convert numpy numeric types to Python types
            if isinstance(result, np.int64):
                result = int(result)
            elif isinstance(result, np.float64):
                result = float(result)

            return {
                "status": "success",
                "result": result,
                "result_type": "numeric"
            }
        # Check for sympy types - we need to check for various sympy classes
        elif isinstance(result, sympy.Symbol) or hasattr(result, "_sympy_") or \
             isinstance(result, sympy.Expr) or str(type(result)).startswith("<class 'sympy."):
            # Handle sympy expressions and symbols
            return {
                "status": "success",
                "result": str(result),
                "result_type": "symbolic"
            }
        elif isinstance(result, np.ndarray):
            # Handle numpy arrays
            result_list = result.tolist()
            return {
                "status": "success",
                "result": result_list,
                "result_type": "array"
            }
        elif isinstance(result, list) and all(isinstance(x, (int, float, np.int64, np.float64)) for x in result):
            # Handle lists of numbers
            # Convert any numpy types to Python types
            result = [float(x) if isinstance(x, np.float64) else int(x) if isinstance(x, np.int64) else x for x in result]
            return {
                "status": "success",
                "result": result,
                "result_type": "array"
            }
        else:
            # Convert other types to string
            str_result = str(result)
            return {
                "status": "success",
                "result": str_result,
                "result_type": "other"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error evaluating expression: {str(e)}"
        }

def _is_safe_expression(expression: str) -> bool:
    """Check if the expression contains only allowed characters and operations.

    This function validates that the expression doesn't contain potentially
    dangerous operations like imports, file operations, etc.

    Args:
        expression: The expression to validate

    Returns:
        True if the expression is safe, False otherwise
    """
    # Check for disallowed keywords
    disallowed_keywords = [
        "import ", "exec(", "eval(", "compile(", "__builtins__", "globals(", "locals(",
        "getattr(", "setattr(", "delattr(", "open(", "file(", "os.", "sys.",
        "subprocess.", "input(", "print("
    ]

    for keyword in disallowed_keywords:
        if keyword in expression:
            return False

    # Special case for sympy expressions with semicolons
    if ";" in expression:
        # This is a special case for expressions like "x = sympy.Symbol('x'); x**2 + 2*x + 1"
        # or "x = Symbol('x'); solve(x**2 - 4, x)"
        # We'll allow it if it follows a specific pattern
        parts = expression.split(";", 1)
        if len(parts) == 2:
            var_part = parts[0].strip()
            expr_part = parts[1].strip()

            # Check if the first part is a variable assignment to a Symbol
            if "=" in var_part and ("Symbol" in var_part or "symbols" in var_part):
                var_name = var_part.split("=", 1)[0].strip()
                # Make sure the variable name is used in the expression part
                if var_name in expr_part:
                    return True

    # We'll be more permissive with the pattern to allow for more complex expressions
    # This includes allowing single quotes for strings and more special characters
    allowed_pattern = r'^[\w\s\d\+\-\*\/\%\(\)\[\]\{\}\,\.\:\=\<\>\!\^\&\|\~\'\"]*$'
    if not re.match(allowed_pattern, expression):
        return False

    return True

CALCULATOR_PARAMS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "The Python expression to evaluate. Can use math, numpy (as np), and sympy libraries.",
        }
    },
    "required": ["expression"],
}
