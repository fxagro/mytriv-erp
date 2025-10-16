#!/bin/bash

# ============================================================================
# MyTriv ERP Backend Setup Script
# ============================================================================
# This script automates the setup process for MyTriv ERP Backend:
# - Sets up Odoo 17 as Git submodule
# - Builds and starts Docker containers (Odoo + PostgreSQL)
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

# Step 1: Set up Odoo submodule
setup_odoo_submodule() {
    print_status "Setting up Odoo 17 submodule..."

    # Check if odoo directory already exists
    if [ -d "odoo" ]; then
        print_warning "Odoo directory already exists. Checking if it's a proper submodule..."

        # Check if it's already a git submodule
        if [ -f ".gitmodules" ] && git submodule status | grep -q "odoo"; then
            print_status "Odoo is already configured as a submodule. Updating..."
            git submodule update --init --recursive
            cd odoo && git checkout 17.0 && cd ..
        else
            print_warning "Odoo directory exists but is not a submodule. Removing and re-creating..."
            rm -rf odoo
            setup_odoo_submodule_fresh
        fi
    else
        setup_odoo_submodule_fresh
    fi

    print_success "Odoo submodule setup completed"
}

# Fresh Odoo submodule setup
setup_odoo_submodule_fresh() {
    print_status "Cloning Odoo 17 as Git submodule..."

    # Add Odoo as submodule
    git submodule add https://github.com/odoo/odoo.git odoo

    # Initialize and checkout the 17.0 branch
    git submodule update --init --recursive
    cd odoo && git checkout 17.0 && cd ..

    print_success "Odoo 17 submodule cloned and configured"
}

# Step 2: Check for port conflicts
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

    # Check for existing PostgreSQL port (5432)
    if lsof -i :5432 -sTCP:LISTEN >/dev/null 2>&1; then
        print_warning "Port 5432 already in use (likely PostgreSQL database)."
        print_warning "This might conflict with the MyTriv ERP database container."
        print_status "If you encounter database issues, consider stopping the existing PostgreSQL service."
    fi

    print_success "Port availability check completed"
}

# Step 3: Build Docker containers
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

# Step 4: Start services
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

# Step 5: Verify running services
verify_services() {
    print_status "Verifying running containers..."

    # Wait a moment for services to fully start
    sleep 10

    # Check running containers
    if docker compose version &> /dev/null; then
        RUNNING_CONTAINERS=$(docker compose ps -q | wc -l)
    else
        RUNNING_CONTAINERS=$(docker-compose ps -q | wc -l)
    fi

    if [ "$RUNNING_CONTAINERS" -lt 2 ]; then
        print_warning "Expected 2 containers to be running, but found $RUNNING_CONTAINERS"
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

# Step 6: Display access information
display_access_info() {
    echo ""
    echo -e "${GREEN}🎉 MyTriv ERP Backend Setup Complete!${NC}"
    echo "================================================================"
    echo -e "${BLUE}🧩 Backend (Odoo 17):${NC}        http://localhost:8069"
    echo -e "${BLUE}🔗 REST API Base:${NC}             http://localhost:8069/api"
    echo -e "${BLUE}🗄️  Database (PostgreSQL):${NC}     localhost:5432"
    echo "================================================================"
    echo ""
    echo -e "${YELLOW}💡 Default Odoo Admin Access:${NC}"
    echo "   Username: admin"
    echo "   Password: admin"
    echo ""
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo "   View logs:        docker compose logs -f"
    echo "   Stop services:    docker compose down"
    echo "   Restart service:  docker compose restart [service-name]"
    echo "   Enter Odoo shell: docker compose exec odoo odoo shell"
    echo ""
    echo -e "${GREEN}🚀 MyTriv ERP Backend is ready for development!${NC}"
}

# Main execution flow
main() {
    echo -e "${GREEN}🚀 Welcome to MyTriv ERP Backend Setup!${NC}"
    echo "======================================"

    # Pre-flight checks
    check_docker
    check_git

    # Execute setup steps
    setup_odoo_submodule
    check_ports
    build_containers
    start_services
    verify_services
    display_access_info

    print_success "Backend setup completed successfully!"
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"