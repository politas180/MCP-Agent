"""Integration tests for Computer Use API endpoints."""
import os
import sys
import unittest
import json
import time
import pytest
from unittest.mock import patch

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the Flask app
from backend.app import app


@pytest.mark.integration
@pytest.mark.computer_use
class TestComputerUseAPI(unittest.TestCase):
    """Test cases for Computer Use API endpoints."""

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_computer_use_tools_endpoint(self):
        """Test the computer-use-tools endpoint."""
        response = self.app.get('/api/computer-use-tools')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['tools'], list)

        # Check that we have the expected tools
        tool_names = [tool['name'] for tool in data['tools']]
        expected_tools = ['execute_python', 'get_system_info', 'list_files', 'read_file']
        for tool in expected_tools:
            self.assertIn(tool, tool_names)

    def test_chat_with_computer_use_mode(self):
        """Test the chat endpoint with Computer Use mode enabled."""
        # Create a test session
        session_id = f"test_session_{int(time.time())}"

        # Send a message with Computer Use mode enabled
        response = self.app.post('/api/chat', json={
            'message': 'Get my system information',
            'session_id': session_id,
            'computer_use_mode': True
        })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Check that the response contains messages
        self.assertIn('messages', data)
        self.assertIsInstance(data['messages'], list)

        # Reset the conversation
        response = self.app.post('/api/reset', json={
            'session_id': session_id
        })
        self.assertEqual(response.status_code, 200)

    def test_computer_use_tool_execution(self):
        """Test that Computer Use tools are executed correctly."""
        # Create a test session
        session_id = f"test_session_{int(time.time())}"

        # First, check that the computer-use-tools endpoint returns the expected tools
        response = self.app.get('/api/computer-use-tools')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['tools'], list)

        # Check that we have the expected tools
        tool_names = [tool['name'] for tool in data['tools']]
        expected_tools = ['execute_python', 'get_system_info', 'list_files', 'read_file']
        for tool in expected_tools:
            self.assertIn(tool, tool_names)

        # Send a message with Computer Use mode enabled
        response = self.app.post('/api/chat', json={
            'message': 'What is my system information?',
            'session_id': session_id,
            'computer_use_mode': True
        })

        self.assertEqual(response.status_code, 200)

        # Reset the conversation
        response = self.app.post('/api/reset', json={
            'session_id': session_id
        })
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
