# Computer Use Feature

The Computer Use feature allows users to control their computer using Python through a dedicated chat interface. This feature is separate from the general agent functionality and has its own set of tools specifically tailored for computer control.

## Features

- **Python Execution**: Execute Python code for computer control tasks
- **System Information**: Get information about your system
- **File Explorer**: List files and directories in a specified path
- **File Reader**: Read the contents of a file

## Usage

1. Click the "Computer Use" button in the top-left corner of the interface
2. The interface will switch to Computer Use mode with a new welcome message
3. Use natural language to interact with the agent and control your computer
4. Click the "Computer Use" button again to switch back to regular mode

## Example Commands

- "What's my current system information?"
- "List the files in my current directory"
- "Read the contents of a specific file"
- "Execute some Python code to print 'Hello, World!'"
- "Create a Python script that organizes files in a directory"

## Safety Measures

The Computer Use feature includes several safety measures to prevent potentially harmful operations:

1. **Restricted Python Execution**: The Python execution environment is restricted to prevent dangerous operations
2. **Dangerous Pattern Detection**: Code containing potentially dangerous patterns (like `shutil.rmtree`, `os.remove`, etc.) is blocked
3. **Limited Module Access**: Only safe modules are available in the execution environment

## Testing

To run the Computer Use tests:

```bash
python tests/run_computer_use_tests.py
```

Or use the main test runner with the `--component computer_use` flag:

```bash
python tests/run_tests.py --component computer_use
```
