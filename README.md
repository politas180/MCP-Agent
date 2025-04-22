# MCP Python Executor

A web-based Python code execution tool powered by a local LLM. This tool allows you to run Python code through a natural language interface.

## Features

### Core Features
- Chat-based interface with the MCP Agent
- Responsive design that works on desktop and mobile devices
- Dark/light mode support based on system preferences
- Session persistence (conversations are saved between page reloads)
- Context window usage indicator showing token usage
- Automatic system information gathering for Computer Use mode

### Operation Modes
- **Normal Mode**: Streamlined interface for everyday use
- **Advanced Mode**: Detailed view with debug and timing information
- **Python Execution Mode**: Execute Python code through a natural language interface

### Python Execution Features
- Run any Python code directly from the chat interface without restrictions
- Unrestricted access to all Python libraries and system resources
- Full file system access for reading and writing files
- Network access for web requests and API calls
- System command execution capabilities
- Capture and display print statements
- Show execution results and variable values
- Display matplotlib visualizations inline

### Developer Features
- Tool preferences panel to enable/disable specific tools
- Timing information in Advanced mode
- Debug panel showing LLM inputs/outputs and tool calls
- Syntax highlighting for code blocks
- LaTeX rendering for mathematical expressions

## Project Structure

```
/
├── backend/
│   ├── app.py                # Flask application
│   ├── config.py             # Configuration
│   ├── llm_client.py         # LLM communication
│   ├── system_info.py        # System information gathering
│   ├── tools/                # Standard tools directory
│   └── computer_use/         # Computer Use mode tools
│       ├── __init__.py       # Package initialization
│       ├── tools/            # Computer control tools directory
│       │   ├── __init__.py   # Tools initialization
│       │   ├── python_execution.py # Python execution tool
│       │   ├── terminal_execution.py # Terminal execution tool
│       │   ├── schemas.py    # Tool schemas
│       │   ├── utils.py      # Utility functions
│       │   └── formatting.py # Output formatting
│       └── README.md         # Documentation for Computer Use mode
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── css/                  # Stylesheets
│   │   └── style.css         # Main CSS file
│   └── js/                   # JavaScript files
│       └── app.js            # Main application logic
├── tests/
│   ├── unit/                 # Unit tests
│   │   ├── test_weather_tool.py
│   │   ├── test_search_tool.py
│   │   ├── test_wiki_tool.py
│   │   ├── test_calculator_tool.py
│   │   ├── test_computer_use_tools.py
│   │   ├── test_backend_app.py
│   │   ├── test_llm_client.py
│   │   ├── test_frontend_js.py
│   │   └── test_tool_preferences.py
│   ├── integration/          # Integration tests
│   │   ├── test_backend_api.py
│   │   ├── test_computer_use_api.py
│   │   └── test_frontend_rendering.py
│   ├── frontend/             # Frontend-specific tests
│   │   └── test_computer_use_ui.js
│   ├── conftest.py           # Test configuration
│   ├── pytest.ini            # PyTest configuration
│   ├── run_tests.py          # Main test runner script
│   └── run_computer_use_tests.py # Computer Use mode tests
├── environment.yml           # Conda environment file
├── requirements.txt          # Pip requirements file
├── pytest.ini               # Project-level PyTest configuration
├── run.py                   # Application runner script
├── run_tests.bat            # Windows test runner
├── run_tests.sh             # Unix test runner
└── README.md                # Documentation
```

## Requirements

- Python 3.10+ (3.12 recommended)
- Conda environment "mcp"
- Local LLM running on http://127.0.0.1:1234 (e.g., LM Studio)
- Modern web browser with JavaScript enabled
- Internet connection for web search and weather tools

## Setup

1. Make sure you have Conda installed
2. Create and activate the Conda environment:

```bash
conda create -n mcp python=3.12
conda activate mcp
```

3. Install the required packages using the environment file:

```bash
conda env update -f environment.yml
```

Or manually install the packages:

```bash
conda activate mcp
pip install flask flask-cors requests beautifulsoup4 wikipedia duckduckgo-search selenium webdriver-manager
```

4. Start your local LLM server (e.g., LM Studio) on port 1234

## Running the Application

### Option 1: Using the run script (recommended)

```bash
conda activate mcp
python run.py
```

This will start the backend server and automatically open the frontend in your default web browser.

### Option 2: Manual startup

1. Start the backend server:

```bash
conda activate mcp
cd backend
python app.py
```

2. Open the frontend in a web browser:
   - Simply open `frontend/index.html` in your browser
   - Or use a simple HTTP server:

```bash
cd frontend
python -m http.server 8000
```

Then navigate to http://localhost:8000 in your browser.

## Usage

### Basic Usage

1. Type your message in the input field and press Enter or click the Send button
2. The agent will respond to your query, using tools when appropriate
3. Use the Reset button to start a new conversation

### Mode Switching

1. **Normal/Advanced Mode**:
   - Toggle between Normal and Advanced modes using the switch in the header
   - In Advanced mode, you'll see:
     - Debug panel showing LLM inputs/outputs and tool calls
     - Timing panel showing processing times for various operations

2. **Computer Use Mode**:
   - Click the "Computer Use" button in the header to toggle Computer Use mode
   - In this mode, the agent can execute Python code and interact with your file system
   - Use with caution as this mode has access to your computer

### Tool Management

1. Click the "Tools" button in the header to open the Tools panel
2. Toggle individual tools on/off to control which ones the agent can use
3. Tool preferences are saved between sessions

## Tools

### Standard Tools

- **Web Search**: Search the web using DuckDuckGo
  - Usage: Ask questions like "Search for latest AI developments" or "Find information about climate change"
  - Returns top search results with titles, URLs, and snippets

- **Wikipedia Search**: Search Wikipedia and get article summaries
  - Usage: Ask questions like "Tell me about quantum computing from Wikipedia" or "What does Wikipedia say about the Roman Empire?"
  - Returns article summaries with links to full articles

- **Weather**: Get current weather and forecast for a location
  - Usage: Ask questions like "What's the weather in London?" or "Get me the forecast for Tokyo"
  - Returns current conditions and a 5-day forecast

- **Calculator**: Evaluate mathematical expressions
  - Usage: Ask questions like "Calculate 2^10 * 5" or "Solve the equation x^2 + 2x + 1"
  - Supports basic arithmetic, advanced math functions, NumPy, and SymPy

### Computer Use Tools

- **Python Code Execution**: Run Python code directly from the chat
  - Usage: Say "Execute Python code to calculate fibonacci numbers" or "Run Python to create a simple plot"
  - Executes Python code without restrictions with access to all libraries
  - Example: "Create a scatter plot of random data using matplotlib"
  - Example: "Write a function to calculate the factorial of a number"
  - Example: "Analyze this CSV data using pandas"

- **Terminal Command Execution**: Run terminal commands directly from the chat
  - Usage: Say "List all files in the current directory" or "Check system information"
  - Executes terminal commands without restrictions
  - Example: "Show me the running processes"
  - Example: "Create a new directory called 'test'"
  - Example: "Check the IP configuration of this machine"

## Testing

The project includes comprehensive unit and integration tests to verify all functionality. Tests are organized by component (frontend, backend, tools) and type (unit, integration).

### Running Tests

To run all tests:

```bash
conda activate mcp
./run_tests.sh  # On Linux/Mac
run_tests.bat   # On Windows
```

You can also run specific test types or components:

```bash
# Run only unit tests
./run_tests.sh --unit

# Run only integration tests
./run_tests.sh --integration

# Run only frontend tests
./run_tests.sh --frontend

# Run only backend tests
./run_tests.sh --backend

# Run only tool tests
./run_tests.sh --tools

# Combine filters
./run_tests.sh --unit --backend

# Generate HTML report
./run_tests.sh --html
```

### Test Coverage

The tests include coverage reporting to ensure all code is properly tested. When you run tests with the `--html` flag, a coverage report is generated in the `htmlcov` directory.

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - `tests/unit/test_weather_tool.py`: Tests for the weather tool
  - `tests/unit/test_search_tool.py`: Tests for the search tool
  - `tests/unit/test_wiki_tool.py`: Tests for the Wikipedia tool
  - `tests/unit/test_system_info.py`: Tests for the system information module
  - `tests/unit/test_backend_app.py`: Tests for the Flask application
  - `tests/unit/test_llm_client.py`: Tests for the LLM client
  - `tests/unit/test_frontend_js.py`: Tests for the frontend JavaScript

- **Integration Tests**: Test components working together
  - `tests/integration/test_backend_api.py`: Tests for the backend API
  - `tests/integration/test_frontend_rendering.py`: Tests for the frontend rendering
  - `tests/integration/test_system_info_integration.py`: Tests for system information integration
  - `tests/integration/test_computer_use_api.py`: Tests for the Computer Use API

Always run tests after adding new features or making changes to ensure everything works correctly.

## Security Considerations

- The Computer Use mode allows executing Python code on your machine. Use with caution.
- The calculator tool has safeguards to prevent dangerous operations but is not completely sandboxed.
- The application communicates with a local LLM, so your conversations stay on your machine.
- No data is sent to external servers except when using the web search and weather tools.

## Known Issues

- **UI Issues**:
  - Toggling agent mode shows computer tools instead of general agent tools
  - Users cannot see and choose available tools in both computer use and general agent tools

- **LLM Issues**:
  - The LLM model (Qwen2.5-7B-Instruct-1M) may occasionally generate repetitive nonsensical output
  - The LLM may fail to execute Python code correctly in some cases

- **Security Considerations**:
  - With unrestricted execution, be careful when running code that modifies your system
  - Always review code before execution, especially when it involves system modifications or file operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT
