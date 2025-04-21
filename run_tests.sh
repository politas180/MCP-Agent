#!/bin/bash
# Run tests for the MCP Agent
echo "Running MCP Agent tests..."

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate mcp

# Parse arguments
TYPE=""
COMPONENT=""
HTML=""

for arg in "$@"; do
    case $arg in
        --unit)
            TYPE="--type unit"
            ;;
        --integration)
            TYPE="--type integration"
            ;;
        --frontend)
            COMPONENT="--component frontend"
            ;;
        --backend)
            COMPONENT="--component backend"
            ;;
        --tools)
            COMPONENT="--component tools"
            ;;
        --html)
            HTML="--html"
            ;;
    esac
done

# Run the tests
python tests/run_tests.py $TYPE $COMPONENT $HTML

# Check the exit code
if [ $? -ne 0 ]; then
    echo "Tests failed with exit code $?"
    exit 1
else
    echo "All tests passed!"
fi
