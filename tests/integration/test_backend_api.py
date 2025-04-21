#!/usr/bin/env python
"""
Integration tests for the backend API.
Tests the API endpoints and tool functionality.
"""
import os
import sys
import unittest
import time
import json
import requests
import subprocess
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestBackendAPI(unittest.TestCase):
    """Test cases for the backend API."""

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

        cls.api_base_url = "http://localhost:5000/api"

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests by stopping the backend server."""
        # Terminate the backend process
        if hasattr(cls, 'backend_process'):
            cls.backend_process.terminate()
            cls.backend_process.wait()

    def test_health_endpoint(self):
        """Test that the health endpoint returns a 200 status code."""
        response = requests.get(f"{self.api_base_url}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_chat_endpoint(self):
        """Test that the chat endpoint processes messages correctly."""
        # Create a test session
        session_id = "test_session_123"

        # Send a message to the chat endpoint
        response = requests.post(
            f"{self.api_base_url}/chat",
            json={
                "message": "Hello, world!",
                "session_id": session_id,
                "advanced_mode": True
            }
        )

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("messages", data)
        self.assertIn("timing", data)
        self.assertIn("debug_info", data)

        # Check that there's at least one assistant message
        assistant_messages = [msg for msg in data["messages"] if msg["role"] == "assistant"]
        self.assertTrue(len(assistant_messages) > 0)

    def test_reset_endpoint(self):
        """Test that the reset endpoint resets a conversation."""
        # Create a test session
        session_id = "test_session_456"

        # Send a message to the chat endpoint
        requests.post(
            f"{self.api_base_url}/chat",
            json={
                "message": "Remember this message.",
                "session_id": session_id,
                "advanced_mode": False
            }
        )

        # Reset the conversation
        response = requests.post(
            f"{self.api_base_url}/reset",
            json={
                "session_id": session_id
            }
        )

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        # Send another message to verify the conversation was reset
        response = requests.post(
            f"{self.api_base_url}/chat",
            json={
                "message": "Was the previous message remembered?",
                "session_id": session_id,
                "advanced_mode": True
            }
        )

        # The response should not reference the previous message
        data = response.json()
        assistant_messages = [msg["content"] for msg in data["messages"] if msg["role"] == "assistant"]
        for message in assistant_messages:
            self.assertNotIn("remember", message.lower())

    def test_direct_tool_call(self):
        """Test direct tool calls to verify tool functionality."""
        from backend.tools import get_weather, pretty_print_weather_results

        # Test the weather tool directly
        weather_result = get_weather("London")

        # Check that the result has the expected structure
        self.assertEqual(weather_result["status"], "success")
        self.assertIn("data", weather_result)
        self.assertIn("location", weather_result["data"])

        # Test the pretty print function
        formatted_result = pretty_print_weather_results(weather_result)
        self.assertIsInstance(formatted_result, str)
        self.assertTrue(formatted_result.startswith("Weather for"))




if __name__ == '__main__':
    unittest.main()
