#!/usr/bin/env python
"""
Unit tests for the real weather tool functionality.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
from bs4 import BeautifulSoup

# Add the backend directory to the path so we can import the tools module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend'))

from tools import get_weather


@pytest.mark.unit
@pytest.mark.tools
class TestRealWeatherTool(unittest.TestCase):
    """Test cases for the real weather tool."""

    @patch('requests.get')
    def test_real_weather_scraping(self, mock_get):
        """Test that the weather tool correctly scrapes OpenWeather."""
        # Create mock responses for the initial search and city page
        search_response = MagicMock()
        search_response.text = """
        <html>
            <body>
                <table class="table-striped">
                    <tbody>
                        <tr>
                            <td><a href="/city/2643743">New York, US</a></td>
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
                <h2>New York, US</h2>
                <div class="current-container">
                    <div class="heading">25.5°C</div>
                    <div>Sunny</div>
                    <span class="bold">Humidity:</span> 65%
                    <span class="bold">Wind:</span> 12 km/h
                    <span class="bold">Rain:</span> 5%
                </div>
                <div class="day-list">
                    <div class="day-list__item">
                        <div class="day-list__item__date">Today</div>
                        <div class="day-list__item__temp">28°C</div>
                        <div class="day-list__item__temp">20°C</div>
                        <div class="day-list__item__condition">Sunny</div>
                    </div>
                    <div class="day-list__item">
                        <div class="day-list__item__date">Tue</div>
                        <div class="day-list__item__temp">27°C</div>
                        <div class="day-list__item__temp">19°C</div>
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

        # Call the function with a location that's not a special test case
        result = get_weather("New York")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "New York, US")
        self.assertEqual(result["data"]["temperature"], "25.5°C")
        self.assertEqual(result["data"]["condition"], "Sunny")
        self.assertEqual(result["data"]["precipitation"], "5%")
        self.assertEqual(result["data"]["humidity"], "65%")
        self.assertEqual(result["data"]["wind"], "12 km/h")
        self.assertEqual(len(result["data"]["forecast"]), 2)
        self.assertEqual(result["data"]["forecast"][0]["day"], "Today")
        self.assertEqual(result["data"]["forecast"][0]["max_temp"], "28°C")
        self.assertEqual(result["data"]["forecast"][0]["min_temp"], "20°C")
        self.assertEqual(result["data"]["forecast"][0]["condition"], "Sunny")
        self.assertEqual(result["data"]["forecast"][1]["day"], "Tue")
        self.assertEqual(result["data"]["forecast"][1]["max_temp"], "27°C")
        self.assertEqual(result["data"]["forecast"][1]["min_temp"], "19°C")
        self.assertEqual(result["data"]["forecast"][1]["condition"], "Partly Cloudy")

    @patch('requests.get')
    def test_alternative_selectors(self, mock_get):
        """Test that the weather tool uses alternative selectors when primary ones fail."""
        # Create mock responses for the initial search and city page
        search_response = MagicMock()
        search_response.text = """
        <html>
            <body>
                <table class="table-striped">
                    <tbody>
                        <tr>
                            <td><a href="/city/1850147">Tokyo, JP</a></td>
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
                <div class="weather-widget">
                    <div class="weather-widget__city-name">Tokyo, Japan</div>
                    <div class="weather-widget__temperature">30°C</div>
                    <div class="weather-widget__description">Clear</div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Humidity</div>
                        <div class="weather-widget__item-value">70%</div>
                    </div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Wind</div>
                        <div class="weather-widget__item-value">8 km/h</div>
                    </div>
                    <div class="weather-widget__item">
                        <div class="weather-widget__item-label">Rain</div>
                        <div class="weather-widget__item-value">0%</div>
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

        # Call the function with a location that's not a special test case
        result = get_weather("Tokyo")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "Tokyo, Japan")
        self.assertEqual(result["data"]["temperature"], "30°C")
        self.assertEqual(result["data"]["condition"], "Clear")
        self.assertEqual(result["data"]["humidity"], "70%")
        self.assertEqual(result["data"]["wind"], "8 km/h")
        self.assertEqual(result["data"]["precipitation"], "0%")

    @patch('requests.get')
    def test_fallback_extraction(self, mock_get):
        """Test that the weather tool falls back to text extraction when selectors fail."""
        # Create mock responses for the initial search and city page
        search_response = MagicMock()
        search_response.text = """
        <html>
            <body>
                <table class="table-striped">
                    <tbody>
                        <tr>
                            <td><a href="/city/2147714">Sydney, AU</a></td>
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
                <div>
                    <p>Weather in Sydney, Australia</p>
                    <p>The temperature is 22°C</p>
                    <p>It is currently Sunny</p>
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

        # Call the function with a location that's not a special test case
        result = get_weather("Sydney")

        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["location"], "Sydney, AU")
        self.assertEqual(result["data"]["temperature"], "22°C")
        self.assertEqual(result["data"]["condition"], "Sunny")

    @patch('requests.get')
    def test_location_not_found(self, mock_get):
        """Test that the weather tool handles location not found gracefully."""
        # Create a mock response with no city links
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <table class="table-striped">
                    <tbody>
                        <tr>
                            <td>No results found</td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function with a non-existent location
        result = get_weather("NonExistentLocation")

        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Could not find location", result["message"])

    @patch('requests.get')
    def test_connection_error(self, mock_get):
        """Test that the weather tool handles connection errors gracefully."""
        # Make the request raise an exception
        mock_get.side_effect = Exception("Connection error")

        # Call the function with any location
        result = get_weather("Berlin")

        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Error fetching weather data", result["message"])


if __name__ == '__main__':
    unittest.main()
