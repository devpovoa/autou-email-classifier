#!/bin/bash

# Deployment Script for AutoU Email Classifier
# Handles production deployment with health checks and rollback capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
PORT="8000"
HEALTH_CHECK_URL="http://localhost:$PORT/health"
CONTAINER_NAME="autou-classifier-prod"
IMAGE_TAG="autou-classifier:production"
BACKUP_TAG="autou-classifier:backup"
DEPLOY_TIMEOUT=60
HEALTH_CHECK_RETRIES=12
HEALTH_CHECK_INTERVAL=5

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV     Target environment [default: production]"
    echo "  -p, --port PORT          Application port [default: 8000]"
    echo "  --timeout SECONDS        Deployment timeout [default: 60]"
    echo "  --no-backup             Skip creating backup of current image"
    echo "  --force                 Force deployment without health checks"
    echo "  -v, --verbose           Verbose output"
    echo "  -h, --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                      # Deploy to production"
    echo "  $0 --port 8080          # Deploy to custom port"
    echo "  $0 --no-backup          # Deploy without backup"
    echo "  $0 --force              # Force deploy without health checks"
}

# Parse command line arguments
SKIP_BACKUP=false
FORCE_DEPLOY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            HEALTH_CHECK_URL="http://localhost:$PORT/health"
            shift 2
            ;;
        --timeout)
            DEPLOY_TIMEOUT="$2"
            shift 2
            ;;
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --force)
            FORCE_DEPLOY=true
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

# Check if running container exists
check_existing_container() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        return 0
    else
        return 1
    fi
}

# Create backup of current running container
create_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        log INFO "Skipping backup as requested"
        return 0
    fi
    
    if check_existing_container; then
        log INFO "Creating backup of current deployment..."
        
        # Commit running container as backup
        docker commit "$CONTAINER_NAME" "$BACKUP_TAG" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log SUCCESS "Backup created: $BACKUP_TAG"
        else
            log WARNING "Failed to create backup, but continuing..."
        fi
    else
        log INFO "No existing container found, skipping backup"
    fi
}

# Build production image
build_production_image() {
    log INFO "Building production image..."
    
    if [ "$VERBOSE" = true ]; then
        docker build --target production -t "$IMAGE_TAG" .
    else
        docker build --target production -t "$IMAGE_TAG" . > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Production image built successfully"
    else
        log ERROR "Failed to build production image"
        exit 1
    fi
}

# Stop existing container
stop_existing_container() {
    if check_existing_container; then
        log INFO "Stopping existing container..."
        
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1
        
        log SUCCESS "Existing container stopped and removed"
    fi
}

# Deploy new container
deploy_container() {
    log INFO "Deploying new container..."
    
    # Start new container
    local container_id
    container_id=$(docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:8000" \
        --env-file .env \
        --restart unless-stopped \
        --health-cmd="curl -f http://localhost:8000/health || exit 1" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        "$IMAGE_TAG")
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Container deployed with ID: ${container_id:0:12}"
    else
        log ERROR "Failed to deploy container"
        exit 1
    fi
}

# Wait for application to be healthy
wait_for_health() {
    if [ "$FORCE_DEPLOY" = true ]; then
        log INFO "Skipping health checks as requested"
        return 0
    fi
    
    log INFO "Waiting for application to be healthy..."
    
    local retries=0
    local max_retries=$HEALTH_CHECK_RETRIES
    
    while [ $retries -lt $max_retries ]; do
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log SUCCESS "Application is healthy and ready"
            return 0
        fi
        
        retries=$((retries + 1))
        log INFO "Health check attempt $retries/$max_retries failed, retrying in ${HEALTH_CHECK_INTERVAL}s..."
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log ERROR "Application failed to become healthy after $max_retries attempts"
    return 1
}

# Rollback to previous version
rollback() {
    log ERROR "Deployment failed, initiating rollback..."
    
    # Stop failed deployment
    if check_existing_container; then
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1
    fi
    
    # Check if backup exists
    if docker image inspect "$BACKUP_TAG" > /dev/null 2>&1; then
        log INFO "Rolling back to previous version..."
        
        # Start backup container
        docker run -d \
            --name "$CONTAINER_NAME" \
            -p "$PORT:8000" \
            --env-file .env \
            --restart unless-stopped \
            "$BACKUP_TAG" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log SUCCESS "Rollback completed successfully"
        else
            log ERROR "Rollback failed"
            exit 1
        fi
    else
        log ERROR "No backup available for rollback"
        exit 1
    fi
}

# Clean up old images
cleanup_old_images() {
    log INFO "Cleaning up old images..."
    
    # Remove dangling images
    local dangling_images
    dangling_images=$(docker images -f "dangling=true" -q)
    
    if [ -n "$dangling_images" ]; then
        echo "$dangling_images" | xargs docker rmi > /dev/null 2>&1
        log SUCCESS "Removed dangling images"
    else
        log INFO "No dangling images to remove"
    fi
}

# Show deployment status
show_status() {
    echo ""
    log SUCCESS "Deployment completed successfully!"
    echo ""
    echo -e "${BLUE}Deployment Information:${NC}"
    echo "  Environment: $ENVIRONMENT"
    echo "  Port: $PORT"
    echo "  Container: $CONTAINER_NAME"
    echo "  Image: $IMAGE_TAG"
    echo "  Health URL: $HEALTH_CHECK_URL"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs: docker logs -f $CONTAINER_NAME"
    echo "  Check status: docker ps --filter name=$CONTAINER_NAME"
    echo "  Stop app: docker stop $CONTAINER_NAME"
    echo "  Restart app: docker restart $CONTAINER_NAME"
    echo ""
    echo -e "${GREEN}Application is now available at: http://localhost:$PORT${NC}"
}

# Main deployment process
main() {
    log INFO "Starting deployment process for $ENVIRONMENT environment..."
    
    # Deployment steps
    create_backup
    build_production_image
    stop_existing_container
    deploy_container
    
    # Health check with rollback on failure
    if ! wait_for_health; then
        if [ "$SKIP_BACKUP" = false ]; then
            rollback
            exit 1
        else
            log ERROR "Health check failed and no backup available"
            exit 1
        fi
    fi
    
    cleanup_old_images
    show_status
}

# Handle script interruption
trap 'log ERROR "Deployment interrupted"; exit 1' INT TERM

# Run main function
main
