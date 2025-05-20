"""Pretty printing functions for tool results."""
from __future__ import annotations

from typing import Any, Dict, List

def pretty_print_search_results(results: List[Dict[str, str]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"{i}. {r.get('title', 'No Title')}")
        output.append(f"   {r.get('url', '#')}")
        snippet = r.get('snippet', '')
        if snippet:
            output.append(f"   {snippet}\n")
        else:
            output.append("")  # Empty line between results

    return "\n".join(output)

def pretty_print_wiki_results(result: Dict[str, Any]) -> str:
    """Format Wikipedia search results for display."""
    if result.get("status") == "error" or result.get("status") == "no_results":
        return result.get("message", "An unknown error occurred while searching Wikipedia.")

    query = result.get('query', 'your query') # Added default for query
    results_list = result.get("results", [])
    if not results_list:
        return f"No Wikipedia results found for '{query}'."

    output = [f"Wikipedia results for '{query}':\n"]

    for i, r in enumerate(results_list, 1):
        output.append(f"{i}. {r.get('title', 'No Title')}")
        output.append(f"   {r.get('url', '#')}")
        output.append(f"   {r.get('summary', 'No summary available.')}\n")

    return "\n".join(output)

def pretty_print_weather_results(result: Dict[str, Any]) -> str:
    """Format weather results for display."""
    if result.get("status") == "error":
        return result.get("message", "An unknown error occurred while fetching weather data.")

    weather_data = result.get("data", {})
    if not weather_data:
        return "No weather data available."

    location = weather_data.get("location", "Unknown location")
    output = [f"Weather for {location}:\n"]

    # Current weather
    if "temperature" in weather_data: # Check existence before accessing
        output.append(f"Temperature: {weather_data.get('temperature', 'N/A')}")
    if "condition" in weather_data:
        output.append(f"Condition: {weather_data.get('condition', 'N/A')}")
    if "humidity" in weather_data:
        output.append(f"Humidity: {weather_data.get('humidity', 'N/A')}")
    if "wind" in weather_data:
        output.append(f"Wind: {weather_data.get('wind', 'N/A')}")
    if "precipitation" in weather_data: # Check before access
        output.append(f"Precipitation: {weather_data.get('precipitation', 'N/A')}")


    # Forecast
    forecast_list = weather_data.get("forecast", [])
    if forecast_list:
        output.append("\nForecast:")
        for day in forecast_list:
            day_info = []
            day_name = day.get("day", "Unknown Day")
            day_info.append(day_name)
            
            condition = day.get("condition", "N/A")
            day_info.append(condition)

            max_temp = day.get("max_temp", "N/A")
            min_temp = day.get("min_temp", "N/A")

            if max_temp != "N/A" and min_temp != "N/A":
                day_info.append(f"{max_temp}/{min_temp}")
            elif max_temp != "N/A":
                day_info.append(max_temp)
            elif min_temp != "N/A":
                day_info.append(min_temp)
            
            if len(day_info) > 1 or (len(day_info) == 1 and day_info[0] != "Unknown Day"): # Avoid printing just "Unknown Day"
                output.append(f"  - {', '.join(day_info)}")

    return "\n".join(output)

def pretty_print_calculator_results(result: Dict[str, Any]) -> str:
    """Format calculator results for display."""
    if result.get("status") == "error":
        return result.get("message", "An unknown error occurred during calculation.")

    result_value = result.get("result") # Keep this for typed checks
    result_type = result.get("result_type", "")

    if result_type == "numeric":
        # Format numeric results nicely
        if isinstance(result_value, int):
            return f"Result: {result_value}"
        elif isinstance(result_value, float): # Ensure it's a float for formatting
            return f"Result: {result_value:.10g}"
        else: # Fallback for other numeric types like complex
            return f"Result: {str(result.get('result', 'N/A'))}" 
    elif result_type == "symbolic":
        return f"Result: {str(result.get('result', 'N/A'))}"
    elif result_type == "array":
        # Format arrays nicely
        # result_value here is expected to be a list from the calculator tool's processing
        if isinstance(result_value, list):
            if len(result_value) > 10:
                # Truncate large arrays
                array_str = str(result_value[:10])[:-1] + ", ...]"
                return f"Result (array of size {len(result_value)}):\n{array_str}"
            else:
                return f"Result (array):\n{str(result_value)}" # Ensure it's stringified
        else: # Fallback if not a list as expected
            return f"Result: {str(result.get('result', 'N/A'))}"
    elif result_type == "special_float" or result_type == "symbolic_special" or result_type == "boolean" or result_type == "none" or result_type == "string":
        # These types are usually already strings or directly convertible and simple
        return f"Result: {str(result.get('result', 'N/A'))}"
    else: # Handles unknown result_type or if result_value itself is missing/problematic
        return f"Result: {str(result.get('result', 'N/A'))}"
