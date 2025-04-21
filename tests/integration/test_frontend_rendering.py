#!/usr/bin/env python
"""
Integration tests for the frontend rendering functionality.
Tests the syntax highlighting and LaTeX rendering features.
"""
import os
import sys
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestFrontendRendering(unittest.TestCase):
    """Test cases for frontend rendering features."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment by starting the backend server."""
        # Start the backend server
        backend_dir = Path(__file__).parent.parent.parent / 'backend'
        backend_path = backend_dir / 'app.py'

        # Use Python executable from current environment
        python_exe = sys.executable

        # Start the backend process
        cls.backend_process = subprocess.Popen(
            [python_exe, str(backend_path)],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for the server to start
        time.sleep(2)

        # Check if the process is still running
        if cls.backend_process.poll() is not None:
            stdout, stderr = cls.backend_process.communicate()
            raise Exception(f"Backend server failed to start. STDOUT: {stdout}, STDERR: {stderr}")

        # Set up the Chrome WebDriver with headless option
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            cls.tearDownClass()
            raise Exception(f"Failed to initialize WebDriver: {e}")

        # Set an implicit wait
        cls.driver.implicitly_wait(10)

        # Get the frontend path
        cls.frontend_path = Path(__file__).parent.parent.parent / 'frontend' / 'index.html'
        cls.frontend_url = f"file://{cls.frontend_path.absolute()}"

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests by stopping the backend server and closing the browser."""
        # Close the WebDriver if it was initialized
        if hasattr(cls, 'driver'):
            cls.driver.quit()

        # Terminate the backend process
        if hasattr(cls, 'backend_process'):
            cls.backend_process.terminate()
            cls.backend_process.wait()

    def setUp(self):
        """Set up each test by navigating to the frontend."""
        self.driver.get(self.frontend_url)
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-input"))
        )

    def test_syntax_highlighting(self):
        """Test that code blocks are properly syntax highlighted."""
        # Find the input field and send a message with a code block
        input_field = self.driver.find_element(By.ID, "user-input")
        input_field.send_keys("Here's a Python code block:\n```python\ndef hello_world():\n    print('Hello, world!')\n\nhello_world()\n```\n\nAnd a JavaScript code block:\n```javascript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconsole.log(greet('World'));\n```")

        # Click the send button
        send_button = self.driver.find_element(By.ID, "send-button")
        send_button.click()

        # Wait for the message to be processed and displayed
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".message.assistant"))
        )

        # Check if the Python code block is properly highlighted
        highlighted_python = self.driver.find_elements(By.CSS_SELECTOR, "code.language-python.hljs")
        self.assertTrue(len(highlighted_python) > 0, "Python code block was not properly highlighted")

        # Check if the JavaScript code block is properly highlighted
        highlighted_js = self.driver.find_elements(By.CSS_SELECTOR, "code.language-javascript.hljs")
        self.assertTrue(len(highlighted_js) > 0, "JavaScript code block was not properly highlighted")

        # Check if language labels are added
        language_labels = self.driver.find_elements(By.CSS_SELECTOR, ".code-language")
        self.assertTrue(len(language_labels) >= 2, "Language labels were not added to code blocks")

        # Verify the content of the language labels
        label_texts = [label.text.lower() for label in language_labels]
        self.assertTrue("python" in label_texts, "Python language label not found")
        self.assertTrue("javascript" in label_texts, "JavaScript language label not found")

    def test_latex_rendering(self):
        """Test that LaTeX expressions are properly rendered."""
        # Find the input field and send a message with LaTeX expressions
        input_field = self.driver.find_element(By.ID, "user-input")
        input_field.send_keys("Here's an inline LaTeX expression: $E = mc^2$ and a display LaTeX expression: $$\\int_{a}^{b} f(x) dx$$\n\nHere are some more complex LaTeX expressions:\n\n1. Maxwell's equations: $\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}$\n\n2. The Schrödinger equation: $$i\\hbar\\frac{\\partial}{\\partial t}\\Psi(\\vec{r},t) = \\hat{H}\\Psi(\\vec{r},t)$$")

        # Click the send button
        send_button = self.driver.find_element(By.ID, "send-button")
        send_button.click()

        # Wait for the message to be processed and displayed
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".message.assistant"))
        )

        # Check if the LaTeX expressions are properly rendered
        # The katex class should be applied to the rendered elements
        rendered_latex = self.driver.find_elements(By.CSS_SELECTOR, ".katex")
        self.assertTrue(len(rendered_latex) >= 4, "Not all LaTeX expressions were properly rendered")

        # Check for inline and display LaTeX
        inline_latex = self.driver.find_elements(By.CSS_SELECTOR, ".latex-inline .katex")
        display_latex = self.driver.find_elements(By.CSS_SELECTOR, ".latex-display .katex")

        self.assertTrue(len(inline_latex) >= 2, "Inline LaTeX expressions were not properly rendered")
        self.assertTrue(len(display_latex) >= 2, "Display LaTeX expressions were not properly rendered")


if __name__ == '__main__':
    unittest.main()
