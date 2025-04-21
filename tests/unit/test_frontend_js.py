#!/usr/bin/env python
"""
Unit tests for the frontend JavaScript functionality.
"""
import sys
import os
import unittest
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path


@pytest.mark.unit
@pytest.mark.frontend
class TestFrontendJS(unittest.TestCase):
    """Test cases for the frontend JavaScript functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Set up the Chrome WebDriver with headless option
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the WebDriver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            pytest.skip(f"Failed to initialize WebDriver: {e}")
        
        # Set an implicit wait
        cls.driver.implicitly_wait(10)
        
        # Get the frontend path
        cls.frontend_path = Path(__file__).parent.parent.parent / 'frontend' / 'index.html'
        cls.frontend_url = f"file://{cls.frontend_path.absolute()}"

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        # Close the WebDriver if it was initialized
        if hasattr(cls, 'driver'):
            cls.driver.quit()

    def setUp(self):
        """Set up each test by navigating to the frontend."""
        self.driver.get(self.frontend_url)
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-input"))
        )

    def test_page_title(self):
        """Test that the page title is correct."""
        self.assertEqual(self.driver.title, "MCP Agent")

    def test_ui_elements_exist(self):
        """Test that all UI elements exist."""
        # Header elements
        self.assertIsNotNone(self.driver.find_element(By.TAG_NAME, "header"))
        self.assertIsNotNone(self.driver.find_element(By.TAG_NAME, "h1"))
        self.assertIsNotNone(self.driver.find_element(By.CLASS_NAME, "mode-toggle"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "mode-switch"))
        
        # Chat container elements
        self.assertIsNotNone(self.driver.find_element(By.CLASS_NAME, "chat-container"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "chat-messages"))
        self.assertIsNotNone(self.driver.find_element(By.CLASS_NAME, "chat-input"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "user-input"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "send-button"))
        
        # Footer elements
        self.assertIsNotNone(self.driver.find_element(By.TAG_NAME, "footer"))
        self.assertIsNotNone(self.driver.find_element(By.CLASS_NAME, "actions"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "reset-button"))
        self.assertIsNotNone(self.driver.find_element(By.ID, "status"))

    def test_advanced_mode_toggle(self):
        """Test that the advanced mode toggle works."""
        # Debug panel should be hidden by default
        debug_panel = self.driver.find_element(By.ID, "debug-panel")
        self.assertEqual(debug_panel.get_attribute("style"), "display: none;")
        
        # Toggle advanced mode
        mode_switch = self.driver.find_element(By.ID, "mode-switch")
        mode_switch.click()
        
        # Debug panel should be visible now
        self.assertTrue("advanced-mode" in self.driver.find_element(By.TAG_NAME, "body").get_attribute("class"))
        
        # Toggle back to normal mode
        mode_switch.click()
        
        # Debug panel should be hidden again
        self.assertFalse("advanced-mode" in self.driver.find_element(By.TAG_NAME, "body").get_attribute("class"))

    def test_user_input(self):
        """Test that user input works."""
        # Find the input field and send a message
        input_field = self.driver.find_element(By.ID, "user-input")
        input_field.send_keys("Hello, world!")
        
        # Check that the input field contains the message
        self.assertEqual(input_field.get_attribute("value"), "Hello, world!")
        
        # Clear the input field
        input_field.clear()
        
        # Check that the input field is empty
        self.assertEqual(input_field.get_attribute("value"), "")

    def test_message_formatting(self):
        """Test message formatting using JavaScript execution."""
        # Test the formatContent function directly
        formatted_content = self.driver.execute_script("""
            return formatContent("**Bold text** and *italic text* and `code`");
        """)
        
        # Check that the formatting was applied
        self.assertIn("<strong>Bold text</strong>", formatted_content)
        self.assertIn("<em>italic text</em>", formatted_content)
        self.assertIn("<code>code</code>", formatted_content)
        
        # Test code block formatting
        code_block = self.driver.execute_script("""
            return formatContent("```python\\nprint('Hello, world!')\\n```");
        """)
        
        # Check that the code block was formatted correctly
        self.assertIn("<pre><code class=\"language-python\">", code_block)
        self.assertIn("print('Hello, world!')", code_block)
        self.assertIn("</code></pre>", code_block)

    def test_add_message_to_chat(self):
        """Test adding messages to the chat."""
        # Add a user message
        self.driver.execute_script("""
            addMessageToChat('user', 'This is a test message');
        """)
        
        # Check that the message was added
        user_messages = self.driver.find_elements(By.CSS_SELECTOR, ".message.user")
        self.assertTrue(len(user_messages) > 0)
        self.assertIn("This is a test message", user_messages[-1].text)
        
        # Add an assistant message
        self.driver.execute_script("""
            addMessageToChat('assistant', 'This is a response');
        """)
        
        # Check that the message was added
        assistant_messages = self.driver.find_elements(By.CSS_SELECTOR, ".message.assistant")
        self.assertTrue(len(assistant_messages) > 0)
        self.assertIn("This is a response", assistant_messages[-1].text)


if __name__ == '__main__':
    unittest.main()
