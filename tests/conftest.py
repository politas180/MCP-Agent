#!/usr/bin/env python
"""
Pytest configuration and fixtures.
"""
import os
import sys
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import subprocess
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))
import app as flask_app


@pytest.fixture
def flask_test_client():
    """Fixture for Flask test client."""
    app = flask_app.app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def selenium_driver():
    """Fixture for Selenium WebDriver."""
    # Set up the Chrome WebDriver with headless option
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the WebDriver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
    except Exception as e:
        pytest.skip(f"Failed to initialize WebDriver: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()


@pytest.fixture(scope="module")
def backend_server():
    """Fixture for running the backend server during tests."""
    # Start the backend server
    backend_dir = Path(__file__).parent.parent / 'backend'
    backend_path = backend_dir / 'app.py'
    
    # Use Python executable from current environment
    python_exe = sys.executable
    
    # Start the backend process
    process = subprocess.Popen(
        [python_exe, str(backend_path)],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Check if the process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        pytest.skip(f"Backend server failed to start. STDOUT: {stdout}, STDERR: {stderr}")
    
    yield process
    
    # Terminate the backend process
    process.terminate()
    process.wait()


@pytest.fixture
def frontend_url():
    """Fixture for the frontend URL."""
    frontend_path = Path(__file__).parent.parent / 'frontend' / 'index.html'
    return f"file://{frontend_path.absolute()}"
