"""Unit tests for tool preferences functionality."""
import json
import unittest

from backend.app import app


class TestToolPreferences(unittest.TestCase):
    """Test the tool preferences API endpoints and functionality."""

    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_get_tool_preferences_default(self):
        """Test getting default tool preferences."""
        response = self.app.get('/api/tools?session_id=test_session')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('tools', data)

        # All tools should be enabled by default
        tools = data['tools']
        self.assertIn('search', tools)
        self.assertIn('wiki_search', tools)
        self.assertIn('get_weather', tools)
        self.assertIn('calculator', tools)
        self.assertTrue(tools['search'])
        self.assertTrue(tools['wiki_search'])
        self.assertTrue(tools['get_weather'])
        self.assertTrue(tools['calculator'])

    def test_update_tool_preferences(self):
        """Test updating tool preferences."""
        # First, disable the search tool
        response = self.app.post(
            '/api/tools?session_id=test_session',
            json={'tools': {'search': False}}
        )
        self.assertEqual(response.status_code, 200)

        # Then get the preferences to verify the update
        response = self.app.get('/api/tools?session_id=test_session')
        data = json.loads(response.data)
        tools = data['tools']

        # Search should be disabled, others enabled
        self.assertFalse(tools['search'])
        self.assertTrue(tools['wiki_search'])
        self.assertTrue(tools['get_weather'])
        self.assertTrue(tools['calculator'])

        # Update multiple tools
        response = self.app.post(
            '/api/tools?session_id=test_session',
            json={'tools': {'search': True, 'wiki_search': False}}
        )
        self.assertEqual(response.status_code, 200)

        # Verify the updates
        response = self.app.get('/api/tools?session_id=test_session')
        data = json.loads(response.data)
        tools = data['tools']

        self.assertTrue(tools['search'])
        self.assertFalse(tools['wiki_search'])
        self.assertTrue(tools['get_weather'])
        self.assertTrue(tools['calculator'])

    def test_reset_conversation_resets_tools(self):
        """Test that resetting a conversation resets tool preferences."""
        # First, disable some tools
        self.app.post(
            '/api/tools?session_id=test_reset',
            json={'tools': {'search': False, 'wiki_search': False}}
        )

        # Verify they're disabled
        response = self.app.get('/api/tools?session_id=test_reset')
        data = json.loads(response.data)
        tools = data['tools']
        self.assertFalse(tools['search'])
        self.assertFalse(tools['wiki_search'])

        # Reset the conversation
        self.app.post(
            '/api/reset',
            json={'session_id': 'test_reset'}
        )

        # Verify tools are reset to enabled
        response = self.app.get('/api/tools?session_id=test_reset')
        data = json.loads(response.data)
        tools = data['tools']
        self.assertTrue(tools['search'])
        self.assertTrue(tools['wiki_search'])
        self.assertTrue(tools['get_weather'])
        self.assertTrue(tools['calculator'])

    def test_tool_preferences_in_chat_request(self):
        """Test that tool preferences are properly handled in chat requests."""
        # Disable the search tool
        self.app.post(
            '/api/tools?session_id=test_chat',
            json={'tools': {'search': False}}
        )

        # Send a chat message with tool preferences
        response = self.app.post(
            '/api/chat',
            json={
                'message': 'Hello',
                'session_id': 'test_chat',
                'tool_preferences': {'search': False, 'wiki_search': True}
            }
        )

        # Verify the response is successful
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('messages', data)


if __name__ == '__main__':
    unittest.main()
