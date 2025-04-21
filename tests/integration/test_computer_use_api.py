"""Integration tests for Python Execution API endpoints."""
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
class TestPythonExecutionAPI(unittest.TestCase):
    """Test cases for Python Execution API endpoints."""

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_python_execution_tools_endpoint(self):
        """Test the computer-use-tools endpoint."""
        response = self.app.get('/api/computer-use-tools')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['tools'], list)

        # Check that we have only the execute_python tool
        tool_names = [tool['name'] for tool in data['tools']]
        self.assertEqual(len(tool_names), 1)
        self.assertEqual(tool_names[0], 'execute_python')

    def test_chat_with_python_execution_mode(self):
        """Test the chat endpoint with Python Execution mode enabled."""
        # Create a test session
        session_id = f"test_session_{int(time.time())}"

        # Send a message with Python Execution mode enabled
        response = self.app.post('/api/chat', json={
            'message': 'Calculate the factorial of 5',
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

    def test_python_execution_tool(self):
        """Test that Python execution tool works correctly."""
        # Create a test session
        session_id = f"test_session_{int(time.time())}"

        # First, check that the computer-use-tools endpoint returns only the execute_python tool
        response = self.app.get('/api/computer-use-tools')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['tools'], list)

        # Check that we have only the execute_python tool
        tool_names = [tool['name'] for tool in data['tools']]
        self.assertEqual(len(tool_names), 1)
        self.assertEqual(tool_names[0], 'execute_python')

        # Send a message with Python Execution mode enabled
        response = self.app.post('/api/chat', json={
            'message': 'Write a Python function to calculate the factorial of a number',
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
