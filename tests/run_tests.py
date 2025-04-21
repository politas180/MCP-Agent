#!/usr/bin/env python
"""
Main test runner script.
Runs all tests in the tests directory using pytest.
"""
import os
import sys
import argparse
import pytest

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests(test_type=None, component=None, html_report=False):
    """
    Run the tests using pytest.

    Args:
        test_type (str, optional): Type of tests to run ('unit', 'integration', or None for all).
        component (str, optional): Component to test ('frontend', 'backend', 'tools', or None for all).
        html_report (bool, optional): Whether to generate an HTML report.

    Returns:
        int: The pytest return code (0 for success, non-zero for failure).
    """
    # Build the pytest arguments
    pytest_args = ['-v']

    # Add markers based on test type and component
    markers = []
    if test_type:
        markers.append(test_type)
    if component:
        markers.append(component)

    if markers:
        pytest_args.append('-m ' + ' and '.join(markers))

    # Add HTML report if requested
    if html_report:
        pytest_args.append('--html=test-report.html')
        pytest_args.append('--self-contained-html')

    # Add coverage reporting
    pytest_args.append('--cov=backend')
    pytest_args.append('--cov=frontend')
    pytest_args.append('--cov-report=term')

    if html_report:
        pytest_args.append('--cov-report=html')

    # Print the command being run
    print(f"Running: pytest {' '.join(pytest_args)}")

    # Run pytest
    return pytest.main(pytest_args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tests for the MCP Agent.')
    parser.add_argument('--type', choices=['unit', 'integration'], help='Type of tests to run')
    parser.add_argument('--component', choices=['frontend', 'backend', 'tools', 'computer_use'], help='Component to test')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    args = parser.parse_args()

    exit_code = run_tests(args.type, args.component, args.html)
    sys.exit(exit_code)
