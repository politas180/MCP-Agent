#!/usr/bin/env python
"""
Unit tests for the search tool functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest

# Add the backend directory to the path so we can import the tools module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

from backend.tools import search, pretty_print_search_results


@pytest.mark.unit
@pytest.mark.tools
class TestSearchTool(unittest.TestCase):
    """Test cases for the search tool."""

    @patch('backend.tools.search.DDGS')
    def test_search_success(self, mock_ddgs):
        """Test that the search tool correctly returns results."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        # Mock search results
        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "This is the first test result."
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "This is the second test result."
            }
        ]
        mock_instance.text.return_value = mock_results

        # Call the function
        results = search("test query", max_results=2)

        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Test Result 1")
        self.assertEqual(results[0]["url"], "https://example.com/1")
        self.assertEqual(results[0]["snippet"], "This is the first test result.")
        self.assertEqual(results[1]["title"], "Test Result 2")
        self.assertEqual(results[1]["url"], "https://example.com/2")
        self.assertEqual(results[1]["snippet"], "This is the second test result.")

        # Verify the mock was called correctly
        mock_instance.text.assert_called_once_with(
            "test query",
            region="wt-wt",
            safesearch="moderate",
            timelimit="y",
            max_results=2
        )

    @patch('backend.tools.search.DDGS')
    def test_search_empty_results(self, mock_ddgs):
        """Test that the search tool handles empty results correctly."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        # Mock empty search results
        mock_instance.text.return_value = []

        # Call the function
        results = search("nonexistent query")

        # Verify the results
        self.assertEqual(len(results), 0)

    @patch('backend.tools.search.DDGS')
    def test_search_missing_fields(self, mock_ddgs):
        """Test that the search tool handles results with missing fields."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_instance

        # Mock search results with missing fields
        mock_results = [
            {
                # Missing title
                "href": "https://example.com/1",
                "body": "This is the first test result."
            },
            {
                "title": "Test Result 2",
                # Missing href
                "body": "This is the second test result."
            },
            {
                "title": "Test Result 3",
                "href": "https://example.com/3",
                # Missing body
            }
        ]
        mock_instance.text.return_value = mock_results

        # Call the function
        results = search("test query", max_results=3)

        # Verify the results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["title"], "<no title>")
        self.assertEqual(results[0]["url"], "https://example.com/1")
        self.assertEqual(results[0]["snippet"], "This is the first test result.")

        self.assertEqual(results[1]["title"], "Test Result 2")
        self.assertEqual(results[1]["url"], "<no link>")
        self.assertEqual(results[1]["snippet"], "This is the second test result.")

        self.assertEqual(results[2]["title"], "Test Result 3")
        self.assertEqual(results[2]["url"], "https://example.com/3")
        self.assertEqual(results[2]["snippet"], "")

    def test_pretty_print_search_results(self):
        """Test that the pretty print function formats search results correctly."""
        # Test with normal results
        results = [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "snippet": "This is the first test result."
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "snippet": "This is the second test result."
            }
        ]

        formatted = pretty_print_search_results(results)

        # Verify the formatting
        self.assertIn("1. Test Result 1", formatted)
        self.assertIn("https://example.com/1", formatted)
        self.assertIn("This is the first test result.", formatted)
        self.assertIn("2. Test Result 2", formatted)
        self.assertIn("https://example.com/2", formatted)
        self.assertIn("This is the second test result.", formatted)

        # Test with empty results
        empty_formatted = pretty_print_search_results([])
        self.assertEqual(empty_formatted, "No results found.")


if __name__ == '__main__':
    unittest.main()
