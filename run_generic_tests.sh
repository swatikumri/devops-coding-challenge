#!/bin/bash

# Generic Bug Detection Tool - Test Runner Script
# This script provides easy commands to run generic image comparison tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CONFIG="generic_config.json"
OUTPUT_DIR="bug_reports"
BATCH_FILE="simple_batch.json"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Generic Bug Detection Tool - Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  compare          - Compare two images"
    echo "  batch            - Run batch comparison from file"
    echo "  setup            - Setup the testing environment"
    echo "  clean            - Clean up generated files"
    echo "  help             - Show this help message"
    echo ""
    echo "Options:"
    echo "  --reference FILE - Reference image path"
    echo "  --current FILE   - Current image path"
    echo "  --test-name NAME - Name for the test"
    echo "  --config FILE    - Configuration file (default: generic_config.json)"
    echo "  --output DIR     - Output directory (default: bug_reports)"
    echo "  --excel FILE     - Excel filename"
    echo "  --batch FILE     - Batch file with image pairs (default: simple_batch.json)"
    echo "  --no-diff        - Do not save difference images"
    echo ""
    echo "Examples:"
    echo "  $0 compare --reference ref.png --current current.png --test-name homepage"
    echo "  $0 batch --batch my_tests.json"
    echo "  $0 setup"
    echo "  $0 compare --reference ref.png --current current.png --excel my_report.xlsx"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up generic bug detection environment..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Create directories
    print_status "Creating directories..."
    mkdir -p bug_reports screenshots reference_images
    
    # Create sample batch file if it doesn't exist
    if [ ! -f "simple_batch.json" ]; then
        print_status "Creating sample batch file..."
        cat > simple_batch.json << EOF
[
  ["reference_images/sample_ref.png", "screenshots/sample_current.png", "sample_test"]
]
EOF
        print_warning "Created sample batch file. Please update with your actual image paths."
    fi
    
    print_success "Environment setup completed!"
}

# Function to compare two images
compare_images() {
    if [ -z "$REFERENCE" ] || [ -z "$CURRENT" ]; then
        print_error "Both --reference and --current are required for comparison"
        exit 1
    fi
    
    if [ ! -f "$REFERENCE" ]; then
        print_error "Reference image not found: $REFERENCE"
        exit 1
    fi
    
    if [ ! -f "$CURRENT" ]; then
        print_error "Current image not found: $CURRENT"
        exit 1
    fi
    
    print_status "Comparing images..."
    print_status "Reference: $REFERENCE"
    print_status "Current: $CURRENT"
    
    # Build command
    CMD="python3 generic_bug_detector.py \"$REFERENCE\" \"$CURRENT\""
    
    if [ -n "$TEST_NAME" ]; then
        CMD="$CMD --test-name \"$TEST_NAME\""
    fi
    
    if [ -n "$CONFIG" ]; then
        CMD="$CMD --config \"$CONFIG\""
    fi
    
    if [ -n "$OUTPUT_DIR" ]; then
        CMD="$CMD --output \"$OUTPUT_DIR\""
    fi
    
    if [ -n "$EXCEL_FILE" ]; then
        CMD="$CMD --excel \"$EXCEL_FILE\""
    fi
    
    if [ "$NO_DIFF" = true ]; then
        CMD="$CMD --no-diff"
    fi
    
    # Execute command
    eval $CMD
    
    print_success "Image comparison completed!"
}

# Function to run batch comparison
run_batch() {
    if [ ! -f "$BATCH_FILE" ]; then
        print_error "Batch file not found: $BATCH_FILE"
        exit 1
    fi
    
    print_status "Running batch comparison from: $BATCH_FILE"
    
    # Build command
    CMD="python3 generic_bug_detector.py --batch \"$BATCH_FILE\""
    
    if [ -n "$CONFIG" ]; then
        CMD="$CMD --config \"$CONFIG\""
    fi
    
    if [ -n "$OUTPUT_DIR" ]; then
        CMD="$CMD --output \"$OUTPUT_DIR\""
    fi
    
    if [ -n "$EXCEL_FILE" ]; then
        CMD="$CMD --excel \"$EXCEL_FILE\""
    fi
    
    if [ "$NO_DIFF" = true ]; then
        CMD="$CMD --no-diff"
    fi
    
    # Execute command
    eval $CMD
    
    print_success "Batch comparison completed!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up generated files..."
    
    # Remove generated files
    rm -rf bug_reports/* screenshots/* reference_images/*
    
    print_success "Cleanup completed!"
}

# Parse command line arguments
COMMAND=""
REFERENCE=""
CURRENT=""
TEST_NAME=""
EXCEL_FILE=""
NO_DIFF=false

while [[ $# -gt 0 ]]; do
    case $1 in
        compare|batch|setup|clean|help)
            COMMAND="$1"
            shift
            ;;
        --reference)
            REFERENCE="$2"
            shift 2
            ;;
        --current)
            CURRENT="$2"
            shift 2
            ;;
        --test-name)
            TEST_NAME="$2"
            shift 2
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --excel)
            EXCEL_FILE="$2"
            shift 2
            ;;
        --batch)
            BATCH_FILE="$2"
            shift 2
            ;;
        --no-diff)
            NO_DIFF=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    compare)
        compare_images
        ;;
    batch)
        run_batch
        ;;
    setup)
        setup_environment
        ;;
    clean)
        cleanup
        ;;
    help|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac