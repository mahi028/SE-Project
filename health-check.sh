#!/bin/bash

# Health check script for EZCare application

set -e

echo "🏥 EZCare Health Check"
echo "====================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name=$1
    echo -n "Checking container $container_name... "
    
    if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    echo -n "Checking database connection... "
    
    if $COMPOSE_CMD exec -T db pg_isready -U ezcare_user -d ezcare > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Connection failed${NC}"
        return 1
    fi
}

# Main health check
main() {
    local all_healthy=true
    
    echo -e "${YELLOW}Checking Docker containers:${NC}"
    check_container "ezcare_db" || all_healthy=false
    check_container "ezcare_backend" || all_healthy=false
    check_container "ezcare_frontend" || all_healthy=false
    check_container "ezcare_caddy" || all_healthy=false
    
    echo ""
    echo -e "${YELLOW}Checking database:${NC}"
    check_database || all_healthy=false
    
    echo ""
    echo -e "${YELLOW}Checking HTTP endpoints:${NC}"
    check_service "Backend Health" "http://localhost:5000/health" || all_healthy=false
    check_service "Frontend" "http://localhost:8080" || all_healthy=false
    # GraphQL endpoint expects POST requests, so we test with a simple introspection query
    echo -n "Checking GraphQL Endpoint... "
    if curl -s -X POST -H "Content-Type: application/json" -d '{"query":"{ __schema { types { name } } }"}' "http://localhost:5000/graphql" | grep -q "data"; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        all_healthy=false
    fi
    
    echo ""
    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}🎉 All services are healthy!${NC}"
        echo ""
        echo -e "${YELLOW}Access your application:${NC}"
        echo "🌐 Frontend: http://localhost:8080"
        echo "🔧 Backend API: http://localhost:5000"
        echo "📊 GraphQL Playground: http://localhost:5000/graphql"
        exit 0
    else
        echo -e "${RED}❌ Some services are unhealthy!${NC}"
        echo ""
        echo -e "${YELLOW}Troubleshooting steps:${NC}"
        echo "1. Check logs: $COMPOSE_CMD logs -f"
        echo "2. Check service status: $COMPOSE_CMD ps"
        echo "3. Restart services: $COMPOSE_CMD restart"
        echo "4. View detailed logs: $COMPOSE_CMD logs [service_name]"
        exit 1
    fi
}

# Check if docker-compose is available
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}❌ Docker Compose is not available${NC}"
    exit 1
fi

if ! docker ps &> /dev/null; then
    if sudo docker ps &> /dev/null; then
        echo -e "${YELLOW}⚠️  Using sudo for Docker commands${NC}"
        # Update compose command with sudo
        if [[ $COMPOSE_CMD == "docker-compose" ]]; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    else
        echo -e "${RED}❌ Cannot access Docker daemon${NC}"
        exit 1
    fi
fi

# Run main function
main
