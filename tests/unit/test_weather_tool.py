#!/usr/bin/env python
"""
Unit tests for the weather tool functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# Add the backend directory to the path so we can import the tools module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

from backend.tools import get_weather


class TestWeatherTool(unittest.TestCase):
    """Test cases for the weather tool."""

    @patch('requests.get')
    def test_weather_tool_success(self, mock_get):
        """Test that the weather tool correctly extracts data when HTML structure is as expected."""
        # Create mock responses for the initial search and city page
        search_response = MagicMock()
        search_response.text = """
        <html>
            <body>
                <table class="table-striped">
                    <tbody>
                        <tr>
                            <td><a href="/city/2643743">London, GB</a></td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """
        search_response.raise_for_status = MagicMock()

        city_response = MagicMock()
        city_response.text = """
        <html>
            <body>
                <h2>London, GB</h2>
                <div class="current-container">
                    <div class="heading">15.2°C</div>
                    <div>Cloudy</div>
                    <span class="bold">Humidity:</span> 75%
                    <span class="bold">Wind:</span> 10 km/h
                    <span class="bold">Rain:</span> 20%
                </div>
                <div class="day-list">
                    <div class="day-list__item">
                        <div class="day-list__item__date">Mon</div>
                        <div class="day-list__item__temp">18°C</div>
                        <div class="day-list__item__temp">10°C</div>
                        <div class="day-list__item__condition">Partly Cloudy</div>
                    </div>
                </div>
            </body>
        </html>
        """
        city_response.raise_for_status = MagicMock()

        # Configure mock to return different responses for different URLs
        def get_side_effect(url, **kwargs):
            if "find" in url:
                return search_response
            else:
                return city_response

        mock_get.side_effect = get_side_effect

        # Call the function
        result = get_weather("London")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "London, GB")
        self.assertEqual(result["data"]["temperature"], "15.2°C")
        self.assertEqual(result["data"]["condition"], "Cloudy")
        self.assertEqual(result["data"]["precipitation"], "20%")
        self.assertEqual(result["data"]["humidity"], "75%")
        self.assertEqual(result["data"]["wind"], "10 km/h")
        self.assertEqual(len(result["data"]["forecast"]), 1)
        self.assertEqual(result["data"]["forecast"][0]["day"], "Mon")
        self.assertEqual(result["data"]["forecast"][0]["max_temp"], "18°C")
        self.assertEqual(result["data"]["forecast"][0]["min_temp"], "10°C")
        self.assertEqual(result["data"]["forecast"][0]["condition"], "Partly Cloudy")

    @patch('requests.get')
    def test_weather_tool_alternative_selectors(self, mock_get):
        """Test that the weather tool uses alternative selectors when primary ones fail."""
        # Create a mock response with weather widget structure
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <div class="weather-widget">
                    <div class="weather-widget__city-name">Paris, France</div>
                    <div class="weather-widget__temperature">22°C</div>
                    <div class="weather-widget__description">Sunny</div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Humidity</div>
                        <div class="weather-widget__item-value">60%</div>
                    </div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Wind</div>
                        <div class="weather-widget__item-value">5 km/h</div>
                    </div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Rain</div>
                        <div class="weather-widget__item-value">10%</div>
                    </div>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("Paris")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "Paris, France")
        self.assertEqual(result["data"]["temperature"], "22°C")
        self.assertEqual(result["data"]["condition"], "Sunny")
        self.assertEqual(result["data"]["humidity"], "60%")
        self.assertEqual(result["data"]["wind"], "5 km/h")
        self.assertEqual(result["data"]["precipitation"], "10%")

    @patch('requests.get')
    def test_weather_tool_error_handling(self, mock_get):
        """Test that the weather tool handles errors gracefully."""
        # Make the request raise an exception
        mock_get.side_effect = Exception("Connection error")

        # Call the function
        result = get_weather("Invalid Location")

        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertTrue("Error fetching weather data" in result["message"])

    @patch('requests.get')
    def test_weather_tool_empty_response(self, mock_get):
        """Test that the weather tool handles empty responses gracefully."""
        # Create a mock response with empty HTML
        mock_response = MagicMock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("Empty")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "Empty")
        # No other data should be present except location


if __name__ == '__main__':
    unittest.main()
