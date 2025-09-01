#!/bin/bash

# Screenshot Bug Detection Tool - Test Runner Script
# This script provides easy commands to run different types of tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
URL="http://localhost:8000"
CONFIG="config.json"
OUTPUT_DIR="bug_reports"

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
    echo "Screenshot Bug Detection Tool - Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup           - Setup the testing environment"
    echo "  start-app       - Start the Sudoku application"
    echo "  create-ref      - Create reference images"
    echo "  test-visual     - Run visual regression tests"
    echo "  test-sudoku     - Run Sudoku-specific tests"
    echo "  test-all        - Run all tests"
    echo "  docker-setup    - Setup using Docker"
    echo "  docker-test     - Run tests using Docker"
    echo "  clean           - Clean up generated files"
    echo "  help            - Show this help message"
    echo ""
    echo "Options:"
    echo "  --url URL       - URL to test (default: http://localhost:8000)"
    echo "  --config FILE   - Configuration file (default: config.json)"
    echo "  --output DIR    - Output directory (default: bug_reports)"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 start-app"
    echo "  $0 create-ref --url http://localhost:8000"
    echo "  $0 test-all --url http://localhost:8000"
    echo "  $0 docker-setup"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up testing environment..."
    
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
    mkdir -p screenshots reference_images bug_reports
    
    # Check if Chrome is installed
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
        print_warning "Chrome/Chromium not found. Please install Chrome or Chromium for screenshot testing."
    fi
    
    print_success "Environment setup completed!"
}

# Function to start the Sudoku application
start_application() {
    print_status "Starting Sudoku application..."
    
    if [ -f "index.html" ]; then
        print_status "Starting HTTP server on port 8000..."
        python3 -m http.server 8000 &
        SERVER_PID=$!
        echo $SERVER_PID > .server.pid
        print_success "Sudoku application started on http://localhost:8000 (PID: $SERVER_PID)"
        print_warning "Use 'kill $SERVER_PID' to stop the server"
    else
        print_error "index.html not found. Please run this script from the project directory."
        exit 1
    fi
}

# Function to create reference images
create_reference_images() {
    print_status "Creating reference images for $URL..."
    python3 test_runner.py --url "$URL" --test-type create_reference --config "$CONFIG"
    print_success "Reference images created!"
}

# Function to run visual regression tests
run_visual_tests() {
    print_status "Running visual regression tests for $URL..."
    python3 test_runner.py --url "$URL" --test-type visual_regression --config "$CONFIG" --output-dir "$OUTPUT_DIR"
    print_success "Visual regression tests completed!"
}

# Function to run Sudoku tests
run_sudoku_tests() {
    print_status "Running Sudoku-specific tests for $URL..."
    python3 test_runner.py --url "$URL" --test-type sudoku --config "$CONFIG" --output-dir "$OUTPUT_DIR"
    print_success "Sudoku tests completed!"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests for $URL..."
    python3 test_runner.py --url "$URL" --test-type all --config "$CONFIG" --output-dir "$OUTPUT_DIR"
    print_success "All tests completed!"
}

# Function to setup Docker environment
docker_setup() {
    print_status "Setting up Docker environment..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Building Docker images..."
    docker-compose build
    
    print_success "Docker environment setup completed!"
}

# Function to run tests with Docker
docker_test() {
    print_status "Running tests with Docker..."
    docker-compose up --abort-on-container-exit bug-detector
    print_success "Docker tests completed!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up generated files..."
    
    # Stop server if running
    if [ -f ".server.pid" ]; then
        SERVER_PID=$(cat .server.pid)
        if kill -0 $SERVER_PID 2>/dev/null; then
            print_status "Stopping server (PID: $SERVER_PID)..."
            kill $SERVER_PID
        fi
        rm -f .server.pid
    fi
    
    # Remove generated files
    rm -rf screenshots/* reference_images/* bug_reports/*
    
    # Remove Docker containers and images
    if command -v docker &> /dev/null; then
        print_status "Cleaning up Docker resources..."
        docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
    fi
    
    print_success "Cleanup completed!"
}

# Parse command line arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        setup|start-app|create-ref|test-visual|test-sudoku|test-all|docker-setup|docker-test|clean|help)
            COMMAND="$1"
            shift
            ;;
        --url)
            URL="$2"
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
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    setup)
        setup_environment
        ;;
    start-app)
        start_application
        ;;
    create-ref)
        create_reference_images
        ;;
    test-visual)
        run_visual_tests
        ;;
    test-sudoku)
        run_sudoku_tests
        ;;
    test-all)
        run_all_tests
        ;;
    docker-setup)
        docker_setup
        ;;
    docker-test)
        docker_test
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