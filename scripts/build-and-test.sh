#!/bin/bash

# Build and Test Script for AutoU Email Classifier
# Usage: ./scripts/build-and-test.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TARGET="development"
RUN_TESTS=true
RUN_LINT=false
VERBOSE=false

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --target TARGET    Build target (development|production) [default: development]"
    echo "  --no-tests            Skip running tests"
    echo "  --lint                Run linting checks"
    echo "  -v, --verbose         Verbose output"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                           # Build and test (development)"
    echo "  $0 --target production       # Build production image"
    echo "  $0 --lint --no-tests        # Only run linting"
    echo "  $0 -v                       # Verbose output"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            BUILD_TARGET="$2"
            shift 2
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        --lint)
            RUN_LINT=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${timestamp} - $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} - $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${timestamp} - $message"
            ;;
    esac
}

# Function to build Docker image
build_image() {
    local target=$1
    local tag="autou-classifier:$target"
    
    log INFO "Building Docker image with target: $target"
    
    if [ "$VERBOSE" = true ]; then
        docker build --target "$target" -t "$tag" .
    else
        docker build --target "$target" -t "$tag" . > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Docker image built successfully: $tag"
    else
        log ERROR "Failed to build Docker image"
        exit 1
    fi
}

# Function to run linting
run_lint() {
    log INFO "Running code quality checks..."
    
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose --profile lint run --rm lint
    else
        log WARNING "docker compose not found, running lint in Docker..."
        docker run --rm -v "$(pwd):/app" autou-classifier:development \
            sh -c "pip install flake8 black isort && \
                   black --check app/ tests/ main.py && \
                   isort --check-only app/ tests/ main.py && \
                   flake8 app/ tests/ main.py --max-line-length=88"
    fi
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Code quality checks passed"
    else
        log ERROR "Code quality checks failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    log INFO "Running tests..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose --profile test run --rm test
    else
        log WARNING "docker-compose not found, running tests in Docker..."
        docker run --rm -v "$(pwd):/app" autou-classifier:development
    fi
    
    if [ $? -eq 0 ]; then
        log SUCCESS "All tests passed"
    else
        log ERROR "Tests failed"
        exit 1
    fi
}

# Function to test application startup
test_startup() {
    if [ "$BUILD_TARGET" = "production" ]; then
        log INFO "Testing application startup..."
        
        # Start container in background
        CONTAINER_ID=$(docker run -d -p 8001:8000 autou-classifier:production)
        
        # Wait for startup
        sleep 10
        
        # Test health endpoint
        if curl -f http://localhost:8001/health > /dev/null 2>&1; then
            log SUCCESS "Application started successfully"
        else
            log ERROR "Application failed to start"
            docker logs $CONTAINER_ID
            docker stop $CONTAINER_ID > /dev/null 2>&1
            exit 1
        fi
        
        # Cleanup
        docker stop $CONTAINER_ID > /dev/null 2>&1
    fi
}

# Main execution
main() {
    log INFO "Starting build and test process..."
    log INFO "Target: $BUILD_TARGET"
    log INFO "Run tests: $RUN_TESTS"
    log INFO "Run lint: $RUN_LINT"
    
    # Build Docker image
    build_image "$BUILD_TARGET"
    
    # Run linting if requested
    if [ "$RUN_LINT" = true ]; then
        run_lint
    fi
    
    # Run tests if requested and target is development
    if [ "$RUN_TESTS" = true ] && [ "$BUILD_TARGET" = "development" ]; then
        run_tests
    fi
    
    # Test startup for production builds
    test_startup
    
    log SUCCESS "Build and test process completed successfully!"
    
    # Show usage instructions
    if [ "$BUILD_TARGET" = "production" ]; then
        echo ""
        log INFO "To run the application:"
        echo "  docker run -p 8000:8000 autou-classifier:production"
        echo ""
        log INFO "Or use docker-compose:"
        echo "  docker-compose up app"
    else
        echo ""
        log INFO "To run development server:"
        echo "  docker-compose up app-dev"
        echo ""
        log INFO "To run tests:"
        echo "  docker-compose --profile test run --rm test"
    fi
}

# Run main function
main
