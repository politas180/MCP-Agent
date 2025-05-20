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
import ast

# AST based validation
ALLOWED_NODE_TYPES = (
    ast.Expression, ast.Call, ast.Name, ast.Load, ast.Constant, ast.Num, ast.Str, ast.NameConstant, # ast.Constant for 3.8+
    ast.BinOp, ast.UnaryOp, ast.Compare, ast.Attribute, ast.IfExp,
    ast.Subscript, ast.Index, ast.Slice, ast.List, ast.Tuple,
    # Operators
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.USub, ast.UAdd,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.And, ast.Or, ast.Not, ast.In, ast.NotIn,
    ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert, ast.LShift, ast.RShift, # Bitwise ops
)

ALLOWED_BUILTINS = {
    'abs', 'round', 'len', 'float', 'int', 'str', 'list', 'dict', 'tuple', 'set', 'sum', 'min', 'max', 'pow', 'range',
    'any', 'all', 'sorted', 'True', 'False', 'None', 'complex', 'divmod', 'isinstance', 'bool', 'enumerate', 'filter', 'map', 'zip'
}

ALLOWED_MODULES = {
    'math': {
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sqrt', 'exp', 'log', 'log10', 'log2',
        'pow', 'fabs', 'pi', 'e', 'degrees', 'radians', 'gamma', 'lgamma', 'erf', 'erfc',
        'ceil', 'floor', 'trunc', 'isinf', 'isnan', 'factorial', 'copysign', 'fmod', 'frexp',
        'isfinite', 'isqrt', 'ldexp', 'modf', 'perm', 'comb'
    },
    'np': {  # For numpy
        'array', 'mean', 'std', 'sum', 'min', 'max', 'sqrt', 'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'arctan2',
        'exp', 'log', 'log10', 'log2', 'power', 'abs', 'absolute', 'arange', 'linspace', 'dot', 'ndarray',
        'matrix', 'transpose', 'reshape', 'concatenate', 'vstack', 'hstack', 'eye', 'zeros', 'ones', 'full',
        'pi', 'e', 'inf', 'nan', 'average', 'median', 'percentile', 'corrcoef', 'cov', 'sort', 'argsort',
        'prod', 'cumsum', 'cumprod', 'diff', 'gradient', 'ceil', 'floor', 'round', 'fix', 'trunc', 'deg2rad', 'rad2deg',
        'real', 'imag', 'conjugate', 'angle', 'unwrap', 'clip', 'where', 'select', 'any', 'all', 'linalg',
        'fft', 'random' # Note: random module itself might be too broad, consider specific functions if needed
    },
    'sympy': {
        'Symbol', 'symbols', 'S', 'solve', 'solveset', 'simplify', 'expand', 'factor', 'collect', 'cancel',
        'apart', 'trigsimp', 'diff', 'integrate', 'limit', 'series', 'Eq', 'Ne', 'Lt', 'Le', 'Gt', 'Ge',
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'sqrt', 'exp', 'log', 'pi', 'E', 'I', 'oo',
        'Matrix', 'Function', 'Lambda', 'Derivative', 'Integral', 'Sum', 'Product', 'N', 'Rational',
        'Integer', 'Float', 'FiniteSet', 'Interval', 'ConditionSet', 'sympify', 'lambdify', 'expr', 'Expr',
        'Wild', 'WildFunction', 'Dummy', 'Subs', 'Tuple', 'List', 'Dict', 'Set', 'Mod', 'Rel', 'And', 'Or', 'Not', 'Xor',
        'ITE', 'Piecewise', 'UnevaluatedExpr', 'degree', 'LC', 'LM', 'LT', 'pdiv', 'prem', 'pexquo',
        'groebner', 'resultant', 'discriminant', 'roots', 'real_roots', 'CRootOf', 'Poly', 'PurePoly',
        'linsolve', 'nonlinsolve', 'dsolve', 'classify_ode', 'checkodesol', 'homogeneous_order',
        'series', 'nsolve', 'intersection', 'Union', 'Complement', 'SymmetricDifference',
        'Contains', 'Element', 'FiniteField', 'GF', 'ZZ', 'QQ', 'RR', 'CC'
    }
}
# Whitelist common constants from modules as well
ALLOWED_MODULE_CONSTANTS = {
    'math': {'pi', 'e', 'tau', 'inf', 'nan'},
    'np': {'pi', 'e', 'inf', 'nan'},
    'sympy': {'pi', 'E', 'I', 'oo', 'S.true', 'S.false', 'S.EmptySet', 'S.UniversalSet', 'S.Complexes', 
              'S.Reals', 'S.Integers', 'S.Naturals', 'S.Naturals0'} # S.true etc. are attributes
}


def _is_safe_ast_node(node, expression_string_for_debugging=""):
    """Recursively validate AST nodes."""
    # print(f"Validating node: {ast.dump(node)} from expression: {expression_string_for_debugging}")
    if not isinstance(node, ALLOWED_NODE_TYPES):
        # print(f"Disallowed node type: {type(node)}")
        return False

    if isinstance(node, ast.Name):
        if not isinstance(node.ctx, ast.Load):
            # print(f"Disallowed context for ast.Name: {type(node.ctx)}")
            return False # Disallow storing/deleting names in eval part
        if node.id not in ALLOWED_BUILTINS and \
           node.id not in ALLOWED_MODULES and \
           node.id not in ALLOWED_MODULE_CONSTANTS.get('math', set()) and \
           node.id not in ALLOWED_MODULE_CONSTANTS.get('np', set()) and \
           node.id not in ALLOWED_MODULE_CONSTANTS.get('sympy', set()):
            # print(f"Disallowed ast.Name id: {node.id}")
            return False
    
    elif isinstance(node, ast.Attribute):
        if not isinstance(node.ctx, ast.Load):
            # print(f"Disallowed context for ast.Attribute: {type(node.ctx)}")
            return False # Disallow storing/deleting attributes
        
        # The value of an attribute must be a Name (module) or another Attribute (submodule)
        current_val = node.value
        module_path_parts = []
        while isinstance(current_val, ast.Attribute):
            module_path_parts.insert(0, current_val.attr)
            current_val = current_val.value
        
        if not isinstance(current_val, ast.Name):
            # print(f"Attribute base is not ast.Name: {ast.dump(current_val)}")
            return False # e.g. (lambda: 0).attr
        
        module_name = current_val.id
        full_attribute_path = [module_name] + module_path_parts + [node.attr]

        # Check for sympy.S.true like constants
        if module_name == 'sympy' and full_attribute_path[1] == 'S':
            sympy_s_attr = "S." + ".".join(full_attribute_path[2:])
            if sympy_s_attr in ALLOWED_MODULE_CONSTANTS.get('sympy', set()):
                 pass # Allowed
            # Also allow functions under sympy.S like S.Reals()
            elif full_attribute_path[-1] in ALLOWED_MODULES.get(module_name, {}): # e.g. sympy.S.Reals
                pass
            else:
                # print(f"Disallowed sympy.S attribute: {sympy_s_attr}")
                return False
        elif module_name not in ALLOWED_MODULES:
            # print(f"Disallowed module in ast.Attribute: {module_name}")
            return False
        
        # Check if the attribute is an allowed function or constant in that module
        # For now, only one level of attribute is checked for functions (e.g. math.sin, not math.submodule.func)
        # This needs to be more robust for submodules like np.linalg.det
        
        # Simplified check: if module_name is allowed, and attr is in its allowed list
        # This part needs to be improved if we want to support np.linalg.det etc.
        # For now, we assume functions are top-level in the whitelisted module dictionary.
        # Constants can be multi-level like sympy.S.true
        
        # Check if the direct attribute is a whitelisted function for that module
        if node.attr not in ALLOWED_MODULES.get(module_name, set()) and \
           node.attr not in ALLOWED_MODULE_CONSTANTS.get(module_name, set()):
            # print(f"Disallowed attribute '{node.attr}' for module '{module_name}'")
            return False

    elif isinstance(node, ast.Call):
        # Ensure the function being called is safe
        if isinstance(node.func, ast.Name): # e.g. abs(x)
            if node.func.id not in ALLOWED_BUILTINS:
                # print(f"Disallowed function call (ast.Name): {node.func.id}")
                return False
        elif isinstance(node.func, ast.Attribute): # e.g. math.sin(x)
            if not _is_safe_ast_node(node.func, expression_string_for_debugging): # Recursively validate the attribute itself
                # print(f"Function call attribute is not safe: {ast.dump(node.func)}")
                return False
        else:
            # print(f"Disallowed function call type: {type(node.func)}")
            return False # Disallow calls on other things like (lambda x: x+1)(3) for now

    elif isinstance(node, (ast.Num, ast.Str, ast.NameConstant, ast.Constant)): # Constants are safe
        pass # ast.Constant covers Num, Str, NameConstant in Python 3.8+

    # For other node types in ALLOWED_NODE_TYPES, we assume they are safe if their children are safe.
    # This is implicitly handled by ast.walk.

    return True

def _is_safe_expression(expression_to_eval: str) -> bool:
    """Check if the expression_to_eval is safe using AST parsing."""
    if not expression_to_eval.strip(): # Empty expression is not valid for eval
        return False
    try:
        tree = ast.parse(expression_to_eval, mode='eval')
    except SyntaxError:
        # print(f"SyntaxError parsing expression: {expression_to_eval}")
        return False

    for node in ast.walk(tree):
        if not _is_safe_ast_node(node, expression_to_eval):
            # print(f"Unsafe node found: {ast.dump(node)} in expression: {expression_to_eval}")
            return False
    return True

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
    # Basic check for __import__ as a preliminary defense
    if "__import__" in expression or "getattr" in expression or "setattr" in expression or "eval" in expression:
        return {
            "status": "error",
            "message": "Expression contains explicitly disallowed keywords."
        }

    # Create a safe environment with only the allowed modules and functions
    # This safe_globals is primarily for the exec part.
    safe_builtins = {name: __builtins__[name] for name in ALLOWED_BUILTINS if name in __builtins__}
    
    safe_globals = {
        "__builtins__": safe_builtins,
        "math": math,
        "np": np,
        "sympy": sympy,
    }
    # Add common sympy functions and classes directly to globals for convenience in exec
    # if they are in the sympy whitelist
    for item_name in ALLOWED_MODULES.get('sympy', set()):
        if hasattr(sympy, item_name):
            safe_globals[item_name] = getattr(sympy, item_name)
    # Add common math functions to globals
    for item_name in ALLOWED_MODULES.get('math', set()):
         if hasattr(math, item_name):
            safe_globals[item_name] = getattr(math, item_name)


    try:
        local_vars = {} # For exec context
        result = None

        if ";" in expression:
            parts = expression.split(";", 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                expr_part = parts[1].strip()

                # The var_part is executed with exec. It should ideally be simple assignments.
                # We rely on safe_globals to restrict what exec can do.
                # A more robust solution might involve AST parsing var_part with mode='exec'
                # and applying stricter rules, but for now, we trust safe_globals.
                # For example, ensure var_part is only assignments to new variables.
                # For now, we will not AST validate var_part but rely on safe_globals.

                if not _is_safe_expression(expr_part):
                    return {
                        "status": "error",
                        "message": "Eval part of expression contains disallowed operations or characters after AST validation."
                    }
                
                # Execute the variable assignment part
                exec(var_part, safe_globals, local_vars)
                
                # Then evaluate the expression part with the combined context
                # Make sure local_vars from exec are available to eval
                combined_globals_for_eval = {**safe_globals, **local_vars}
                result = eval(expr_part, combined_globals_for_eval, {}) # eval uses its own locals if not specified or if globals has them
            else: # Single part, but contains a semicolon oddly. Treat as full expression for eval.
                if not _is_safe_expression(expression):
                    return {
                        "status": "error",
                        "message": "Expression contains disallowed operations or characters after AST validation."
                    }
                result = eval(expression, safe_globals, local_vars) # local_vars will be empty here
        else:
            if not _is_safe_expression(expression):
                return {
                    "status": "error",
                    "message": "Expression contains disallowed operations or characters after AST validation."
                }
            result = eval(expression, safe_globals, local_vars) # local_vars will be empty here

        # Handle different result types
        if isinstance(result, (int, float, complex, np.int_, np.float_, np.complex_)):
            # Convert numpy numeric types to Python types
            if isinstance(result, (np.int_, np.integer)): # Catches np.int32, np.int64 etc.
                result = int(result)
            elif isinstance(result, (np.float_, np.floating)): # Catches np.float32, np.float64 etc.
                result = float(result)
            elif isinstance(result, (np.complex_, np.complexfloating)):
                result = complex(result)
            
            # Check for NaN/Infinity after potential conversion
            if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
                 return {"status": "success", "result": str(result), "result_type": "special_float"}


            return {
                "status": "success",
                "result": result,
                "result_type": "numeric"
            }
        # Check for sympy types
        elif hasattr(result, "_sympy_") or isinstance(result, sympy.Expr) or str(type(result)).startswith("<class 'sympy."):
            # Handle sympy expressions and symbols
            # Check for NaN/Infinity in Sympy objects if possible (e.g. sympy.nan, sympy.oo)
            if result is sympy.nan or result is sympy.oo or result is sympy.zoo or result is sympy.Ioo:
                 return {"status": "success", "result": str(result), "result_type": "symbolic_special"}
            return {
                "status": "success",
                "result": str(result), # Convert sympy objects to string for JSON compatibility
                "result_type": "symbolic"
            }
        elif isinstance(result, np.ndarray):
            # Handle numpy arrays
            # Check for object arrays which might contain unsafe types
            if result.dtype == object:
                try:
                    # Attempt to convert to a safe type, e.g., float, if possible and all elements are suitable
                    # This is a basic attempt; complex object arrays might still pose risks.
                    # A common case is an array of sympy objects.
                    if all(hasattr(x, "_sympy_") or isinstance(x, (sympy.Expr, type(None))) for x in result.flatten()):
                        result_list = [str(x) if x is not None else None for x in result.tolist()]
                    else: # If not all sympy, try to convert to float, then string as fallback
                         result_list = [str(x) for x in result.tolist()] # Fallback to string for safety
                except Exception: # pylint: disable=broad-except
                     return {"status": "error", "message": "Cannot serialize numpy object array with mixed/unsafe types."}
            else:
                result_list = result.tolist()

            # Handle potential NaN/Infinity in numpy arrays
            if any(isinstance(x, list) for x in result_list): # Multidimensional
                contains_nan_inf = False
                for sublist in result_list:
                    if any(isinstance(val, float) and (math.isnan(val) or math.isinf(val)) for val in sublist):
                        contains_nan_inf = True; break
                if contains_nan_inf:
                     return {"status": "success", "result": [[str(v) if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v for v in sl] for sl in result_list], "result_type": "array_special_float"}
            else: # 1D array
                if any(isinstance(val, float) and (math.isnan(val) or math.isinf(val)) for val in result_list):
                     return {"status": "success", "result": [str(v) if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v for v in result_list], "result_type": "array_special_float"}
            
            return {
                "status": "success",
                "result": result_list,
                "result_type": "array"
            }
        elif isinstance(result, (list, tuple)):
            # Handle lists/tuples of numbers or sympy objects
            processed_list = []
            is_special_float_list = False
            for x in result:
                if isinstance(x, (np.int_, np.integer)): x = int(x)
                elif isinstance(x, (np.float_, np.floating)): x = float(x)
                elif isinstance(x, (np.complex_, np.complexfloating)): x = complex(x)
                elif hasattr(x, "_sympy_") or isinstance(x, sympy.Expr): x = str(x)
                
                if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
                    processed_list.append(str(x))
                    is_special_float_list = True
                elif not isinstance(x, (int, float, complex, str, type(None))): # Allow None in lists
                    # If type is still not basic, convert to string as a fallback safety measure
                    processed_list.append(str(x)) 
                else:
                    processed_list.append(x)
            
            return {
                "status": "success",
                "result": processed_list,
                "result_type": "array_special_float" if is_special_float_list else "array"
            }
        elif isinstance(result, (bool, type(None))):
            return {
                "status": "success",
                "result": result,
                "result_type": "boolean" if isinstance(result, bool) else "none"
            }
        else:
            # Convert other safe types to string
            # This path should be hit by things like sympy.Matrix, or other sympy structures
            str_result = str(result)
            # Ensure the string result isn't excessively long
            if len(str_result) > 2000: # Limit output length
                str_result = str_result[:2000] + " ... (truncated)"
            return {
                "status": "success",
                "result": str_result,
                "result_type": "string" # Changed from "other" to "string"
            }
    except SyntaxError as se:
        return {"status": "error", "message": f"Syntax error in expression: {str(se)}"}
    except NameError as ne:
        return {"status": "error", "message": f"Name error in expression: {str(ne)}. Ensure variables are defined or part of allowed libraries."}
    except TypeError as te:
        return {"status": "error", "message": f"Type error in expression: {str(te)}"}
    except ZeroDivisionError:
        return {"status": "error", "message": "Error: Division by zero."}
    except Exception as e: # pylint: disable=broad-except
        # Catch any other exceptions during evaluation
        return {
            "status": "error",
            "message": f"Error evaluating expression: {str(e)}"
        }

# (The _is_safe_expression function using AST is defined above the calculator function)

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
