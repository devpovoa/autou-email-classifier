#!/bin/bash

# Development Setup Script for AutoU Email Classifier
# This script sets up the complete development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    log INFO "Checking system requirements..."
    
    local missing_tools=()
    
    if ! command_exists docker; then
        missing_tools+=("docker")
    fi
    
    # Check for Docker Compose
    if ! docker compose version &> /dev/null; then
        missing_tools+=("docker compose plugin")
    fi
    
    if ! command_exists curl; then
        missing_tools+=("curl")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log ERROR "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Please install the missing tools:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Docker Compose: https://docs.docker.com/compose/install/"
        echo "  curl: Usually available via package manager (apt, yum, brew, etc.)"
        exit 1
    fi
    
    log SUCCESS "All required tools are installed"
}

# Check Docker service
check_docker() {
    log INFO "Checking Docker service..."
    
    if ! docker info > /dev/null 2>&1; then
        log ERROR "Docker is not running. Please start Docker service."
        exit 1
    fi
    
    log SUCCESS "Docker is running"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        log INFO "Creating .env file..."
        
        cat > .env << 'EOF'
# AutoU Email Classifier Environment Variables

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Application Configuration
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# AI Configuration
USE_HEURISTIC_FALLBACK=true
CONFIDENCE_THRESHOLD=0.7
HEURISTIC_KEYWORDS_URGENT=urgente,emergencia,asap,critico,imediato
HEURISTIC_KEYWORDS_THANKS=obrigado,agradeco,thanks,grateful,appreciate
HEURISTIC_KEYWORDS_NORMAL=informacao,consulta,duvida,question,inquiry

# Development specific
RELOAD=true
WORKERS=1
EOF
        
        log SUCCESS "Created .env file with default configuration"
        log WARNING "Please edit .env file and add your OpenAI API key"
    else
        log INFO ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    log INFO "Creating necessary directories..."
    
    local dirs=("logs" "coverage" "uploads")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log INFO "Created directory: $dir"
        fi
    done
    
    log SUCCESS "All directories created"
}

# Set up pre-commit hooks (optional)
setup_git_hooks() {
    if [ -d ".git" ]; then
        log INFO "Setting up git hooks..."
        
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to run code quality checks

echo "Running pre-commit checks..."

# Run linting
docker compose --profile lint run --rm lint

if [ $? -ne 0 ]; then
    echo "Pre-commit checks failed. Please fix the issues before committing."
    exit 1
fi

echo "Pre-commit checks passed!"
EOF
        
        chmod +x .git/hooks/pre-commit
        log SUCCESS "Git pre-commit hooks set up"
    else
        log INFO "Not a git repository, skipping git hooks setup"
    fi
}

# Build development environment
build_development() {
    log INFO "Building development environment..."
    
    # Pull base images to speed up builds
    docker pull python:3.12-slim
    
    # Build development image
    docker compose build app-dev
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Development environment built successfully"
    else
        log ERROR "Failed to build development environment"
        exit 1
    fi
}

# Run initial tests to verify setup
verify_setup() {
    log INFO "Running verification tests..."
    
    # Run tests to make sure everything works
    docker compose --profile test run --rm test
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Setup verification completed successfully"
    else
        log ERROR "Setup verification failed"
        exit 1
    fi
}

# Show usage instructions
show_usage() {
    echo ""
    log SUCCESS "Development environment setup completed!"
    echo ""
    echo -e "${BLUE}Quick Start Commands:${NC}"
    echo ""
    echo "  Start development server:"
    echo "    docker compose up app-dev"
    echo ""
    echo "  Run tests:"
    echo "    docker compose --profile test run --rm test"
    echo ""
    echo "  Run linting:"
    echo "    docker compose --profile lint run --rm lint"
    echo ""
    echo "  Run all tests and linting:"
    echo "    ./scripts/build-and-test.sh --lint"
    echo ""
    echo "  Access application:"
    echo "    http://localhost:8000"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Edit .env file and add your OpenAI API key"
    echo "2. Start the development server: docker compose up app-dev"
    echo "3. Open http://localhost:8000 in your browser"
    echo "4. Start developing!"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker compose logs -f app-dev"
    echo "  Rebuild: docker compose build app-dev"
    echo "  Clean up: docker compose down --volumes"
}

# Main execution
main() {
    log INFO "Setting up AutoU Email Classifier development environment..."
    
    # Run setup steps
    check_requirements
    check_docker
    create_env_file
    create_directories
    setup_git_hooks
    build_development
    verify_setup
    
    # Show usage instructions
    show_usage
}

# Handle script interruption
trap 'log ERROR "Setup interrupted"; exit 1' INT TERM

# Run main function
main
