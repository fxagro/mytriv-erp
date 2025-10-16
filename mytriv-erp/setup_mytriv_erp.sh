#!/bin/bash

# ============================================================================
# MyTriv ERP Automated Setup Script
# ============================================================================
# This script automates the complete setup process for MyTriv ERP:
# - Clones the repository
# - Initializes Git repository
# - Sets up environment configuration
# - Builds and starts Docker containers
# - Verifies all services are running
#
# Usage: ./setup_mytriv_erp.sh
# ============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose first."
        exit 1
    fi

    print_success "Docker is available"
}

# Check if Git is installed
check_git() {
    print_status "Checking Git installation..."

    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi

    print_success "Git is available"
}

# Step 1: Clone the repository
clone_repository() {
    print_status "Cloning MyTriv ERP repository..."

    if [ -d "mytriv-erp" ]; then
        print_warning "Directory 'mytriv-erp' already exists. Removing it..."
        rm -rf mytriv-erp
    fi

    git clone https://github.com/fxagro/mytriv-erp.git
    cd mytriv-erp

    print_success "Repository cloned successfully"
}

# Step 2: Initialize Git repository
initialize_git() {
    print_status "Initializing fresh Git repository..."

    # Remove existing .git directory if it exists
    rm -rf .git

    # Initialize new Git repository
    git init
    git branch -M main

    print_success "Git repository initialized"
}

# Step 3: Create initial commit
create_initial_commit() {
    print_status "Creating initial commit..."

    # Add all files to Git
    git add .

    # Create commit with descriptive message
    git commit -m "Initial MyTriv ERP full-stack boilerplate commit

- Next.js 15 frontend with TypeScript and TailwindCSS
- Odoo 17 Community backend with custom REST API
- PostgreSQL 15 database
- Docker Compose multi-service setup
- Production-ready configuration
- Employee management API endpoints"

    print_success "Initial commit created"
}

# Step 4: Configure GitHub remote and push
setup_github_remote() {
    print_status "Setting up GitHub remote..."

    # Check if remote origin already exists
    if git remote | grep -q "origin"; then
        print_warning "Remote 'origin' already exists. Removing it..."
        git remote remove origin
    fi

    # Add GitHub remote
    git remote add origin https://github.com/fxagro/mytriv-erp.git

    print_success "GitHub remote configured"
}

# Step 5: Set up environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."

    if [ ! -f ".env.example" ]; then
        print_error ".env.example file not found!"
        exit 1
    fi

    if [ -f ".env" ]; then
        print_warning ".env file already exists. Skipping copy..."
    else
        cp .env.example .env
        print_success "Environment file created from .env.example"
    fi
}

# Step 6: Check for port conflicts
check_ports() {
    print_status "Checking for port conflicts..."

    # Check for existing Odoo port (8069)
    if lsof -i :8069 -sTCP:LISTEN >/dev/null 2>&1; then
        print_error "Port 8069 already in use (likely Odoo backend)."
        print_error "Please stop the existing service before running this script."
        print_status "You can check what's using the port with: lsof -i :8069"
        print_status "Or stop the service with: docker compose down (if it's a Docker container)"
        exit 1
    fi

    # Check for existing Frontend port (3000)
    if lsof -i :3000 -sTCP:LISTEN >/dev/null 2>&1; then
        print_error "Port 3000 already in use (likely React frontend)."
        print_error "Please stop the existing service before running this script."
        print_status "You can check what's using the port with: lsof -i :3000"
        print_status "Or stop the service with: docker compose down (if it's a Docker container)"
        exit 1
    fi

    # Check for existing PostgreSQL port (5432)
    if lsof -i :5432 -sTCP:LISTEN >/dev/null 2>&1; then
        print_warning "Port 5432 already in use (likely PostgreSQL database)."
        print_warning "This might conflict with the MyTriv ERP database container."
        print_status "If you encounter database issues, consider stopping the existing PostgreSQL service."
    fi

    print_success "Port availability check completed"
}

# Step 7: Build Docker containers
build_containers() {
    print_status "Building Docker containers..."

    # Use docker compose (newer syntax) or fallback to docker-compose
    if docker compose version &> /dev/null; then
        docker compose build
    else
        docker-compose build
    fi

    print_success "Docker containers built successfully"
}

# Step 8: Start services
start_services() {
    print_status "Starting all services..."

    # Use docker compose (newer syntax) or fallback to docker-compose
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    print_success "All services started in detached mode"
}

# Step 9: Verify running services
verify_services() {
    print_status "Verifying running containers..."

    # Wait a moment for services to fully start
    sleep 5

    # Check running containers
    if docker compose version &> /dev/null; then
        RUNNING_CONTAINERS=$(docker compose ps -q | wc -l)
    else
        RUNNING_CONTAINERS=$(docker-compose ps -q | wc -l)
    fi

    if [ "$RUNNING_CONTAINERS" -lt 3 ]; then
        print_warning "Expected 3 containers to be running, but found $RUNNING_CONTAINERS"
        print_status "Checking container status..."
        if docker compose version &> /dev/null; then
            docker compose ps
        else
            docker-compose ps
        fi
    else
        print_success "All containers are running"
    fi
}

# Step 10: Display access information
display_access_info() {
    echo ""
    echo -e "${GREEN}🎉 MyTriv ERP Setup Complete!${NC}"
    echo "================================================================"
    echo -e "${BLUE}📱 Frontend (React/Next.js):${NC} http://localhost:3000"
    echo -e "${BLUE}🧩 Backend (Odoo 17):${NC}        http://localhost:8069"
    echo -e "${BLUE}🔗 Employee API:${NC}              http://localhost:8069/api/v1/employees"
    echo -e "${BLUE}🌐 Generic API:${NC}               http://localhost:8069/api"
    echo -e "${BLUE}🗄️  Database (PostgreSQL):${NC}     localhost:5432"
    echo "================================================================"
    echo ""
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo "   View logs:        docker compose logs -f"
    echo "   Stop services:    docker compose down"
    echo "   Restart service:  docker compose restart [service-name]"
    echo ""
    echo -e "${GREEN}🚀 Happy coding with MyTriv ERP!${NC}"
}

# Main execution flow
main() {
    echo -e "${GREEN}🚀 Welcome to MyTriv ERP Automated Setup!${NC}"
    echo "=============================================="

    # Pre-flight checks
    check_docker
    check_git

    # Execute setup steps
    clone_repository
    initialize_git
    create_initial_commit
    setup_github_remote
    setup_environment
    check_ports
    build_containers
    start_services
    verify_services
    display_access_info

    print_success "Setup completed successfully!"
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"