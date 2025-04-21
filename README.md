# MCP Agent Web Application

A web-based intelligent assistant powered by a local LLM that can perform web searches, Wikipedia searches, get weather information, perform calculations, and even control your computer with Python.

## Features

### Core Features
- Chat-based interface with the MCP Agent
- Responsive design that works on desktop and mobile devices
- Dark/light mode support based on system preferences
- Session persistence (conversations are saved between page reloads)

### Operation Modes
- **Normal Mode**: Streamlined interface for everyday use
- **Advanced Mode**: Detailed view with debug and timing information
- **Computer Use Mode**: Special mode that allows controlling your computer with Python

### Tool Integration
- **Web Search**: Search the web using DuckDuckGo
- **Wikipedia Search**: Search Wikipedia and get article summaries
- **Weather**: Get current weather and forecast for a location
- **Calculator**: Evaluate mathematical expressions with support for:
  - Basic arithmetic operations
  - Advanced math functions (via Python's math library)
  - Scientific computing (via NumPy)
  - Symbolic mathematics (via SymPy)

### Computer Use Tools (in Computer Use Mode)
- **Python Execution**: Run Python code directly from the chat
- **System Information**: Get details about your operating system and hardware
- **File Explorer**: List files and directories in any path
- **File Reader**: Read the contents of files

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
│   ├── tools.py              # Standard tool implementations
│   └── computer_use/         # Computer Use mode tools
│       ├── __init__.py       # Package initialization
│       ├── tools.py          # Computer control tools
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
  - Recommended model: **Qwen2.5-7B-Instruct-1M-GGUF/Qwen2.5-7B-Instruct-1M-Q4_K_M.gguf**
  - This model has been tested and performs well with all features
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
   - Download and install [LM Studio](https://lmstudio.ai/)
   - Download the recommended model: **Qwen2.5-7B-Instruct-1M-GGUF/Qwen2.5-7B-Instruct-1M-Q4_K_M.gguf**
   - Load the model in LM Studio
   - Start the local server on port 1234 (default setting)

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

- **Weather**: Get real-time weather and forecast for a location
  - Usage: Ask questions like "What's the weather in London?" or "Get me the forecast for Tokyo"
  - Returns current conditions and forecast by scraping OpenWeather
  - No API key required - works with any location available on OpenWeather

- **Calculator**: Evaluate mathematical expressions
  - Usage: Ask questions like "Calculate 2^10 * 5" or "Solve the equation x^2 + 2x + 1"
  - Supports basic arithmetic, advanced math functions, NumPy, and SymPy

### Computer Use Tools

- **Python Execution**: Run Python code directly from the chat
  - Usage: Say "Execute Python code to list all files in a directory" or "Run Python to create a simple plot"
  - Executes Python code in a controlled environment

- **System Information**: Get details about your operating system and hardware
  - Usage: Ask "What's my system information?" or "Tell me about my computer"
  - Returns platform, OS, Python version, and other system details

- **File Explorer**: List files and directories in any path
  - Usage: Say "List files in my downloads folder" or "Show me what's in the current directory"
  - Returns a formatted list of files and directories

- **File Reader**: Read the contents of files
  - Usage: Ask "Read the contents of config.py" or "Show me what's in README.md"
  - Returns the text content of the specified file

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
  - `tests/unit/test_backend_app.py`: Tests for the Flask application
  - `tests/unit/test_llm_client.py`: Tests for the LLM client
  - `tests/unit/test_frontend_js.py`: Tests for the frontend JavaScript

- **Integration Tests**: Test components working together
  - `tests/integration/test_backend_api.py`: Tests for the backend API
  - `tests/integration/test_frontend_rendering.py`: Tests for the frontend rendering

Always run tests after adding new features or making changes to ensure everything works correctly.

## Security Considerations

- The Computer Use mode allows executing Python code on your machine. Use with caution.
- The calculator tool has safeguards to prevent dangerous operations but is not completely sandboxed.
- The application communicates with a local LLM, so your conversations stay on your machine.
- No data is sent to external servers except when using the web search and weather tools.

## Known Issues

- There's a UI bug where toggling agent mode shows computer tools instead of general agent tools.
- The LLM may occasionally produce unexpected responses or fail to use tools correctly.
- Web scraping for weather data may break if OpenWeather changes their website structure.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT
