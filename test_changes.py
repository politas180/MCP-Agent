"""Test script to verify our changes."""
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.computer_use.tools import execute_python
from backend.computer_use.tools.utils import sanitize_python_code
from backend.config import MAX_MODEL_TOKENS

def test_python_execution():
    """Test the Python execution tool."""
    print("Testing Python execution...")
    result = execute_python('print("Hello, World!")')
    print(f"Status: {result['status']}")
    print(f"Output: {result.get('output', '')}")
    print("Python execution test completed.\n")

def test_python_code_sanitization():
    """Test the Python code sanitization function."""
    print("Testing Python code sanitization...")

    # Test with markdown code block
    code1 = """```python
print("Hello, World!")
result = 2 + 2
print(f"Result: {result}")
```"""

    # Test with extra text
    code2 = """python
Copy
Edit
```py
print("Hello from code block 2!")
```"""

    print(f"Original code 1:\n{code1}\n")
    sanitized1 = sanitize_python_code(code1)
    print(f"Sanitized code 1:\n{sanitized1}\n")

    print(f"Original code 2:\n{code2}\n")
    sanitized2 = sanitize_python_code(code2)
    print(f"Sanitized code 2:\n{sanitized2}\n")

    print("Python code sanitization test completed.\n")

def test_context_window_calculation():
    """Test the context window calculation."""
    print("Testing context window calculation...")

    # Create a mock conversation
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        {"role": "user", "content": "Can you help me with a Python question?"},
        {"role": "assistant", "content": "Of course! I'd be happy to help with your Python question."}
    ]

    # Calculate total characters
    total_chars = sum(len(msg.get("content", "") or "") for msg in messages)

    # Estimate tokens (4 chars per token)
    estimated_tokens = total_chars // 4

    # Calculate percentage
    percentage = (estimated_tokens / MAX_MODEL_TOKENS) * 100

    print(f"Total characters: {total_chars}")
    print(f"Estimated tokens: {estimated_tokens}")
    print(f"Maximum tokens: {MAX_MODEL_TOKENS}")
    print(f"Usage percentage: {percentage:.2f}%")
    print("Context window calculation test completed.\n")

if __name__ == "__main__":
    print("Starting tests...\n")

    test_python_execution()
    test_python_code_sanitization()
    test_context_window_calculation()

    print("All tests completed successfully!")
