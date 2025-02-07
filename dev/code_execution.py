import io
import sys
import traceback
import contextlib
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def execute_python_code(code_string, global_vars=None, local_vars=None):
    """
    Executes a string of Python code, captures output/errors, and handles return values.

    (Docstring from previous version is mostly the same, with additions below)

    Now uses the `ast` module for more accurate expression detection and
    `compile` for separate execution and evaluation.  Distinguishes between
    syntax and runtime errors.  Logs output/errors using the `logging` module.
    """
    if global_vars is None:
        global_vars = {}
    if local_vars is None:
        local_vars = global_vars

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    return_value = None
    exception = None
    traceback_str = None
    error_type = None  # "syntax" or "runtime"

    try:
        # --- 1. Parse the code using ast ---
        tree = ast.parse(code_string)

        # --- 2. Separate the last statement if it's an expression ---
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_stmt = tree.body[-1]
            tree.body = tree.body[:-1]  # Remove the expression from the main body
            expression_code = compile(ast.Expression(last_stmt.value), '<string>', 'eval')
        else:
            expression_code = None

        # --- 3. Compile the main body (statements) ---
        main_code = compile(tree, '<string>', 'exec')


        # --- 4. Execute and Evaluate ---
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            exec(main_code, global_vars, local_vars)  # Execute statements
            if expression_code:
                return_value = eval(expression_code, global_vars, local_vars)  # Eval expression

    except SyntaxError as e:  # Catch syntax errors during compile time
        exception = e
        traceback_str = traceback.format_exc()
        error_type = "syntax"
        logger.error(f"Syntax error in code: {e}")

    except Exception as e:  # Catch runtime errors
        exception = e
        traceback_str = traceback.format_exc()
        error_type = "runtime"
        logger.error(f"Runtime error in code: {e}")

    finally:
        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()
        logger.info(f"Code execution stdout: {stdout.strip()}")
        if stderr: # Only log stderr if it contains something.
            logger.error(f"Code execution stderr: {stderr.strip()}")


    return {
        'stdout': stdout,
        'stderr': stderr,
        'return_value': return_value,
        'exception': exception,
        'traceback': traceback_str,
        'error_type': error_type  # Added error_type
    }



def execute_python_function(func, *args, **kwargs):
    """
    Executes a Python function and captures its output and errors.

    (Docstring mostly unchanged, but logging is now integrated)
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    return_value = None
    exception = None
    traceback_str = None
    error_type = "runtime"  # Function execution errors are always runtime

    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            return_value = func(*args, **kwargs)
    except Exception as e:
        exception = e
        traceback_str = traceback.format_exc()
        logger.error(f"Runtime error in function {func.__name__}: {e}")
    finally:
        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()
        logger.info(f"Function execution stdout: {stdout.strip()}")
        if stderr:  # Only log stderr if non-empty
            logger.error(f"Function execution stderr: {stderr.strip()}")

    return {
        'stdout': stdout,
        'stderr': stderr,
        'return_value': return_value,
        'exception': exception,
        'traceback': traceback_str,
        'error_type': error_type
    }


# --- Unit Tests (using unittest) ---
import unittest

class TestExecutePythonCode(unittest.TestCase):

    def test_simple_execution(self):
        code = "print('Hello')"
        result = execute_python_code(code)
        self.assertEqual(result['stdout'], "Hello\n")
        self.assertIsNone(result['exception'])

    def test_return_value(self):
        code = "x = 5\nx * 2"
        result = execute_python_code(code)
        self.assertEqual(result['return_value'], 10)

    def test_syntax_error(self):
        code = "print('Hello'"  # Missing closing parenthesis
        result = execute_python_code(code)
        self.assertEqual(result['error_type'], 'syntax')
        self.assertIsInstance(result['exception'], SyntaxError)

    def test_runtime_error(self):
        code = "1 / 0"
        result = execute_python_code(code)
        self.assertEqual(result['error_type'], 'runtime')
        self.assertIsInstance(result['exception'], ZeroDivisionError)

    def test_global_vars(self):
        code = "x = x + 5"
        global_vars = {'x': 10}
        result = execute_python_code(code, global_vars=global_vars)
        self.assertEqual(global_vars['x'], 15)

    def test_local_vars(self):
        code = "y = 20"
        local_vars = {}
        result = execute_python_code(code, local_vars=local_vars)
        self.assertEqual(local_vars['y'], 20)

    def test_no_return(self):
        code = "x = 5"  # No expression at the end
        result = execute_python_code(code)
        self.assertIsNone(result['return_value'])

    def test_multiline_expression(self):
        code = """
x = 10
y = 20
x + y
"""
        result = execute_python_code(code)
        self.assertEqual(result['return_value'], 30)

    def test_multiline_with_comments(self):
        code = """
# This is a comment
x = 5
# Another comment
x * 2
"""
        result = execute_python_code(code)
        self.assertEqual(result['return_value'], 10)

    def test_empty_code(self):
        code = ""
        result = execute_python_code(code)
        self.assertEqual(result['stdout'], "")
        self.assertIsNone(result['return_value'])

    def test_code_with_function_definition(self):
      code = """
def my_func(a,b):
  return a + b
my_func(5,5)
"""
      result = execute_python_code(code)
      self.assertEqual(result['return_value'], 10)

    def test_code_with_if_statement(self):
        code = """
if True:
    x = 10
else:
    x = 20
x
"""
        result = execute_python_code(code)
        self.assertEqual(result['return_value'], 10)

    def test_code_with_try_except(self):
        code = """
try:
    1 / 0
except ZeroDivisionError:
    print("Caught division by zero")
"""
        result = execute_python_code(code)
        self.assertEqual(result['stdout'], "Caught division by zero\n")
        self.assertIsNone(result['return_value'])  # No return value
        self.assertIsNone(result['exception']) # Exception was handled.

    def test_import_statement(self):
        code = """
import math
math.sqrt(16)
"""
        result = execute_python_code(code)
        self.assertEqual(result['return_value'], 4.0)

class TestExecutePythonFunction(unittest.TestCase):

    def test_simple_function(self):
        def my_func(a, b):
            return a + b

        result = execute_python_function(my_func, 5, 3)
        self.assertEqual(result['return_value'], 8)
        self.assertIsNone(result['exception'])

    def test_function_with_print(self):
        def my_func():
            print("Hello from function")

        result = execute_python_function(my_func)
        self.assertEqual(result['stdout'], "Hello from function\n")

    def test_function_with_error(self):
        def my_func():
            1 / 0

        result = execute_python_function(my_func)
        self.assertEqual(result['error_type'], 'runtime')
        self.assertIsInstance(result['exception'], ZeroDivisionError)

    def test_function_with_kwargs(self):
      def my_func(a, b=10):
          return a + b
      result = execute_python_function(my_func, 5, b=20)
      self.assertEqual(result['return_value'], 25)

if __name__ == '__main__':
    unittest.main(verbosity=2)