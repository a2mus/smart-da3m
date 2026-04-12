#!/bin/bash

# Ihsane MVP Platform - Post-Deployment Health Check
# Tests all endpoints to verify deployment

set -e

DOMAIN="ihsan-dz.duckdns.org"
BASE_URL="https://${DOMAIN}"

echo "🏥 Ihsane MVP Platform - Health Check"
echo "======================================"
echo "Domain: ${DOMAIN}"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing ${name}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ OK (${response})${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (${response})${NC}"
        return 1
    fi
}

# Test main endpoints
test_endpoint "Main Website" "${BASE_URL}/"
test_endpoint "API Health" "${BASE_URL}/api/health"
test_endpoint "API Docs" "${BASE_URL}/docs"
test_endpoint "OpenAPI Schema" "${BASE_URL}/openapi.json"

echo ""
echo "======================================"

# Check if running locally via docker
if command -v docker-compose &> /dev/null; then
    echo ""
    echo "🐳 Docker Services Status:"
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "   (Services not running or not in prod mode)"
fi

echo ""
echo "✨ All checks complete!"
echo ""
echo "Access your application:"
echo "  🌐 ${BASE_URL}"
echo "  📚 ${BASE_URL}/docs"
echo ""
