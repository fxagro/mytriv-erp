#!/bin/bash

# ============================================================================
# MyTriv ERP Backend Connection Test Script
# ============================================================================
# This script tests the connection to the MyTriv ERP backend services:
# - Tests Odoo server connectivity on port 8069
# - Tests PostgreSQL database connectivity on port 5432
# - Verifies that both services are responding correctly
#
# Usage: ./test_connection.sh
# ============================================================================

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

# Test Odoo server connection
test_odoo_connection() {
    print_status "Testing Odoo server connection on http://localhost:8069..."

    # Test basic HTTP connectivity
    if curl -s --max-time 10 http://localhost:8069 > /dev/null; then
        print_success "Odoo server is responding on port 8069"

        # Test if it's actually Odoo by checking for Odoo-specific content
        if curl -s http://localhost:8069 | grep -q "Odoo"; then
            print_success "Odoo server is serving content correctly"
        else
            print_warning "Odoo server is responding but content verification failed"
        fi
    else
        print_error "Cannot connect to Odoo server on port 8069"
        print_status "Make sure Odoo is running with: docker compose up -d"
        return 1
    fi
}

# Test PostgreSQL database connection
test_database_connection() {
    print_status "Testing PostgreSQL database connection on localhost:5432..."

    # Check if PostgreSQL port is open
    if nc -z localhost 5432 2>/dev/null; then
        print_success "PostgreSQL port 5432 is accessible"

        # Try to connect with psql (if available) or just test the port
        if command -v psql &> /dev/null; then
            if PGPASSWORD=odoo psql -h localhost -U odoo -d mytriv_erp -c "SELECT 1;" > /dev/null 2>&1; then
                print_success "PostgreSQL database connection successful"
            else
                print_warning "PostgreSQL port is open but authentication failed"
                print_status "Expected credentials: user='odoo', password='odoo', database='mytriv_erp'"
            fi
        else
            print_status "psql client not available, but port 5432 is accessible"
        fi
    else
        print_error "Cannot connect to PostgreSQL database on port 5432"
        print_status "Make sure PostgreSQL container is running"
        return 1
    fi
}

# Test Docker containers status
test_docker_containers() {
    print_status "Checking Docker containers status..."

    # Check if docker compose is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi

    # Check running containers
    if docker compose version &> /dev/null; then
        RUNNING=$(docker compose ps -q | wc -l)
        ALL=$(docker compose ps -a -q | wc -l)
    else
        RUNNING=$(docker-compose ps -q | wc -l)
        ALL=$(docker-compose ps -a -q | wc -l)
    fi

    if [ "$RUNNING" -eq 0 ]; then
        print_error "No containers are running"
        print_status "Start containers with: docker compose up -d"
        return 1
    elif [ "$RUNNING" -lt 2 ]; then
        print_warning "Only $RUNNING containers running (expected 2: odoo + postgres)"
    else
        print_success "All $RUNNING containers are running"
    fi

    # Show container status
    print_status "Container status:"
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
}

# Test API endpoints
test_api_endpoints() {
    print_status "Testing API endpoints..."

    # Test base API endpoint
    if curl -s --max-time 5 http://localhost:8069/api > /dev/null; then
        print_success "REST API base endpoint is accessible"
    else
        print_warning "REST API base endpoint not accessible (this may be normal if API modules aren't loaded yet)"
    fi

    # Test web client
    if curl -s --max-time 5 http://localhost:8069/web > /dev/null; then
        print_success "Odoo Web Client is accessible at http://localhost:8069/web"
    else
        print_warning "Odoo Web Client not accessible"
    fi
}

# Main execution
main() {
    echo -e "${GREEN}🔍 MyTriv ERP Backend Connection Test${NC}"
    echo "====================================="

    # Run all tests
    test_docker_containers
    echo ""

    test_odoo_connection
    echo ""

    test_database_connection
    echo ""

    test_api_endpoints
    echo ""

    # Summary
    echo -e "${GREEN}📊 Test Summary${NC}"
    echo "==============="
    print_success "Connection tests completed"
    print_status "Access your ERP at: http://localhost:8069"
    print_status "Default login: admin / admin"
}

# Handle script interruption
trap 'echo -e "\n${RED}Test interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"