#!/usr/bin/env python
"""
Unit tests for the Wikipedia search tool functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest

# Add the backend directory to the path so we can import the tools module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

from tools import wiki_search, pretty_print_wiki_results


@pytest.mark.unit
@pytest.mark.tools
class TestWikiTool(unittest.TestCase):
    """Test cases for the Wikipedia search tool."""

    @patch('tools.wikipedia.search')
    @patch('tools.wikipedia.page')
    @patch('tools.wikipedia.summary')
    def test_wiki_search_success(self, mock_summary, mock_page, mock_search):
        """Test that the wiki search tool correctly returns results."""
        # Set up the mocks
        mock_search.return_value = ["Python (programming language)", "Python (mythology)"]
        
        mock_page1 = MagicMock()
        mock_page1.title = "Python (programming language)"
        mock_page1.url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
        
        mock_page2 = MagicMock()
        mock_page2.title = "Python (mythology)"
        mock_page2.url = "https://en.wikipedia.org/wiki/Python_(mythology)"
        
        # Make mock_page return different values based on input
        def get_page(title, **kwargs):
            if title == "Python (programming language)":
                return mock_page1
            elif title == "Python (mythology)":
                return mock_page2
            raise ValueError(f"Unexpected title: {title}")
        
        mock_page.side_effect = get_page
        
        # Make mock_summary return different values based on input
        def get_summary(title, **kwargs):
            if title == "Python (programming language)":
                return "Python is a high-level programming language."
            elif title == "Python (mythology)":
                return "In Greek mythology, Python was a serpent."
            raise ValueError(f"Unexpected title: {title}")
        
        mock_summary.side_effect = get_summary
        
        # Call the function
        result = wiki_search("Python", max_results=2, sentences=1)
        
        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query"], "Python")
        self.assertEqual(len(result["results"]), 2)
        
        self.assertEqual(result["results"][0]["title"], "Python (programming language)")
        self.assertEqual(result["results"][0]["url"], "https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.assertEqual(result["results"][0]["summary"], "Python is a high-level programming language.")
        
        self.assertEqual(result["results"][1]["title"], "Python (mythology)")
        self.assertEqual(result["results"][1]["url"], "https://en.wikipedia.org/wiki/Python_(mythology)")
        self.assertEqual(result["results"][1]["summary"], "In Greek mythology, Python was a serpent.")
        
        # Verify the mocks were called correctly
        mock_search.assert_called_once_with("Python", results=2)
        mock_page.assert_any_call("Python (programming language)", auto_suggest=False)
        mock_page.assert_any_call("Python (mythology)", auto_suggest=False)
        mock_summary.assert_any_call("Python (programming language)", sentences=1, auto_suggest=False)
        mock_summary.assert_any_call("Python (mythology)", sentences=1, auto_suggest=False)

    @patch('tools.wikipedia.search')
    def test_wiki_search_no_results(self, mock_search):
        """Test that the wiki search tool handles no results correctly."""
        # Set up the mock
        mock_search.return_value = []
        
        # Call the function
        result = wiki_search("NonexistentTopic")
        
        # Verify the result
        self.assertEqual(result["status"], "no_results")
        self.assertIn("No Wikipedia results found", result["message"])
        
        # Verify the mock was called correctly
        mock_search.assert_called_once_with("NonexistentTopic", results=3)

    @patch('tools.wikipedia.search')
    @patch('tools.wikipedia.page')
    @patch('tools.wikipedia.summary')
    def test_wiki_search_with_exceptions(self, mock_summary, mock_page, mock_search):
        """Test that the wiki search tool handles exceptions correctly."""
        # Set up the mocks
        mock_search.return_value = ["Python (programming language)", "Python (mythology)"]
        
        # Make mock_page raise an exception for the second title
        def get_page(title, **kwargs):
            if title == "Python (programming language)":
                mock_result = MagicMock()
                mock_result.title = "Python (programming language)"
                mock_result.url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
                return mock_result
            elif title == "Python (mythology)":
                from wikipedia.exceptions import DisambiguationError
                raise DisambiguationError("Python", ["Python (snake)", "Monty Python"])
            raise ValueError(f"Unexpected title: {title}")
        
        mock_page.side_effect = get_page
        
        # Make mock_summary return a value for the first title
        mock_summary.return_value = "Python is a high-level programming language."
        
        # Call the function
        result = wiki_search("Python", max_results=2)
        
        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["query"], "Python")
        self.assertEqual(len(result["results"]), 1)  # Only one result should be returned
        
        self.assertEqual(result["results"][0]["title"], "Python (programming language)")
        self.assertEqual(result["results"][0]["url"], "https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.assertEqual(result["results"][0]["summary"], "Python is a high-level programming language.")

    def test_pretty_print_wiki_results(self):
        """Test that the pretty print function formats wiki results correctly."""
        # Test with normal results
        result = {
            "status": "success",
            "query": "Python",
            "results": [
                {
                    "title": "Python (programming language)",
                    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                    "summary": "Python is a high-level programming language."
                },
                {
                    "title": "Python (mythology)",
                    "url": "https://en.wikipedia.org/wiki/Python_(mythology)",
                    "summary": "In Greek mythology, Python was a serpent."
                }
            ]
        }
        
        formatted = pretty_print_wiki_results(result)
        
        # Verify the formatting
        self.assertIn("Wikipedia results for 'Python'", formatted)
        self.assertIn("1. Python (programming language)", formatted)
        self.assertIn("https://en.wikipedia.org/wiki/Python_(programming_language)", formatted)
        self.assertIn("Python is a high-level programming language.", formatted)
        self.assertIn("2. Python (mythology)", formatted)
        
        # Test with error status
        error_result = {
            "status": "error",
            "message": "An error occurred"
        }
        
        error_formatted = pretty_print_wiki_results(error_result)
        self.assertEqual(error_formatted, "An error occurred")
        
        # Test with no results
        no_results = {
            "status": "no_results",
            "message": "No Wikipedia results found for 'NonexistentTopic'"
        }
        
        no_results_formatted = pretty_print_wiki_results(no_results)
        self.assertEqual(no_results_formatted, "No Wikipedia results found for 'NonexistentTopic'")


if __name__ == '__main__':
    unittest.main()
