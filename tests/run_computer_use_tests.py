"""Run all Computer Use tests."""
import os
import sys
import unittest

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the test modules
from tests.unit.test_computer_use_tools import TestComputerUseTools
from tests.integration.test_computer_use_api import TestComputerUseAPI


def run_tests():
    """Run all Computer Use tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestComputerUseTools))
    test_suite.addTest(unittest.makeSuite(TestComputerUseAPI))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Computer Use tests...")
    success = run_tests()
    
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)
