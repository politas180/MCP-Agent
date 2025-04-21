"""Pretty printing functions for tool results."""
from __future__ import annotations

from typing import Any, Dict, List

def pretty_print_search_results(results: List[Dict[str, str]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"{i}. {r['title']}")
        output.append(f"   {r['url']}")
        if r.get('snippet'):
            output.append(f"   {r['snippet']}\n")
        else:
            output.append("")  # Empty line between results

    return "\n".join(output)

def pretty_print_wiki_results(result: Dict[str, Any]) -> str:
    """Format Wikipedia search results for display."""
    if result.get("status") == "error" or result.get("status") == "no_results":
        return result.get("message", "Error searching Wikipedia.")

    if not result.get("results"):
        return f"No Wikipedia results found for '{result.get('query', '')}'."

    output = [f"Wikipedia results for '{result.get('query', '')}':\n"]

    for i, r in enumerate(result["results"], 1):
        output.append(f"{i}. {r['title']}")
        output.append(f"   {r['url']}")
        output.append(f"   {r['summary']}\n")

    return "\n".join(output)

def pretty_print_weather_results(result: Dict[str, Any]) -> str:
    """Format weather results for display."""
    if result.get("status") == "error":
        return result.get("message", "Error fetching weather data.")

    weather_data = result.get("data", {})
    if not weather_data:
        return "No weather data available."

    location = weather_data.get("location", "Unknown location")
    output = [f"Weather for {location}:\n"]

    # Current weather
    if "temperature" in weather_data:
        output.append(f"Temperature: {weather_data['temperature']}")
    if "condition" in weather_data:
        output.append(f"Condition: {weather_data['condition']}")
    if "humidity" in weather_data:
        output.append(f"Humidity: {weather_data['humidity']}")
    if "wind" in weather_data:
        output.append(f"Wind: {weather_data['wind']}")
    if "precipitation" in weather_data:
        output.append(f"Precipitation: {weather_data['precipitation']}")

    # Forecast
    if "forecast" in weather_data and weather_data["forecast"]:
        output.append("\nForecast:")
        for day in weather_data["forecast"]:
            day_info = []
            if "day" in day:
                day_info.append(day["day"])
            if "condition" in day:
                day_info.append(day["condition"])
            if "max_temp" in day and "min_temp" in day:
                day_info.append(f"{day['max_temp']}/{day['min_temp']}")
            elif "max_temp" in day:
                day_info.append(day["max_temp"])
            elif "min_temp" in day:
                day_info.append(day["min_temp"])

            if day_info:
                output.append(f"  - {', '.join(day_info)}")

    return "\n".join(output)

def pretty_print_calculator_results(result: Dict[str, Any]) -> str:
    """Format calculator results for display."""
    if result.get("status") == "error":
        return result.get("message", "Error evaluating expression.")

    result_value = result.get("result")
    result_type = result.get("result_type", "")

    if result_type == "numeric":
        # Format numeric results nicely
        if isinstance(result_value, int):
            return f"Result: {result_value}"
        else:
            # Format float with appropriate precision
            return f"Result: {result_value:.10g}"
    elif result_type == "symbolic":
        return f"Result: {result_value}"
    elif result_type == "array":
        # Format arrays nicely
        if isinstance(result_value, list):
            if len(result_value) > 10:
                # Truncate large arrays
                array_str = str(result_value[:10])[:-1] + ", ...]"
                return f"Result (array of size {len(result_value)}):\n{array_str}"
            else:
                return f"Result (array):\n{result_value}"
        else:
            return f"Result: {result_value}"
    else:
        return f"Result: {result_value}"
