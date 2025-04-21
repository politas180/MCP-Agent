# MCP Agent Web Application

A web-based intelligent assistant that can perform web searches, Wikipedia searches, and get weather information.

## Features

- Chat-based interface with the MCP Agent
- Normal and Advanced modes
- Tool integration:
  - Web search (DuckDuckGo)
  - Wikipedia search
  - Weather information (web scraping)
- Timing information in Advanced mode
- Current date and time awareness

## Project Structure

```
/
├── backend/
│   ├── app.py           # Flask application
│   ├── config.py        # Configuration
│   ├── llm_client.py    # LLM communication
│   └── tools.py         # Tool implementations
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── css/             # Stylesheets
│   │   └── style.css
│   └── js/              # JavaScript files
│       └── app.js
├── tests/
│   ├── unit/            # Unit tests
│   │   └── test_weather_tool.py
│   ├── integration/     # Integration tests
│   │   ├── test_backend_api.py
│   │   └── test_frontend_rendering.py
│   └── run_tests.py     # Test runner script
├── environment.yml      # Conda environment file
├── run.py               # Application runner script
└── README.md            # Documentation
```

## Requirements

- Python 3.10+
- Conda environment "mcp"
- Local LLM running on http://127.0.0.1:1234 (e.g., LM Studio)

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

1. Type your message in the input field and press Enter or click the Send button
2. Toggle between Normal and Advanced modes using the switch in the header
3. In Advanced mode, you'll see:
   - Debug information showing LLM inputs/outputs and tool calls
   - Timing information for LLM calls, tool executions, and total processing time
4. Use the Reset button to start a new conversation

## Tools

- **Web Search**: Search the web using DuckDuckGo
- **Wikipedia Search**: Search Wikipedia and get article summaries
- **Weather**: Get current weather and forecast for a location

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

## License

MIT
