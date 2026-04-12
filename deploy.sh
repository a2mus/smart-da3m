#!/bin/bash

# Ihsane MVP Platform - Production Deployment Script
# Domain: ihsan-dz.duckdns.org
# Architecture: Caddy-only (no Nginx)

set -e  # Exit on any error

echo "🚀 Ihsane MVP Platform - Production Deployment"
echo "================================================"
echo "Domain: ihsan-dz.duckdns.org"
echo "Architecture: Caddy-only (HTTPS + Static Files + Reverse Proxy)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.prod.example...${NC}"
    
    if [ -f .env.prod.example ]; then
        cp .env.prod.example .env
        
        # Generate secure defaults for required values
        GENERATED_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p -c 64 | head -n 1)
        GENERATED_PG_PASS=$(openssl rand -base64 24 2>/dev/null || head -c 32 /dev/urandom | base64 | head -c 24)
        
        # Replace placeholder values with generated values
        sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${GENERATED_PG_PASS}|" .env
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${GENERATED_SECRET}|" .env
        
        echo -e "${GREEN}✅ .env created with generated secrets${NC}"
    else
        echo -e "${RED}❌ Error: Neither .env nor .env.prod.example found!${NC}"
        echo "   Cannot continue without environment configuration."
        exit 1
    fi
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Validate required variables
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo -e "${RED}❌ Error: POSTGRES_PASSWORD is not set in .env${NC}"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ ${#SECRET_KEY} -lt 32 ]; then
    echo -e "${RED}❌ Error: SECRET_KEY must be at least 32 characters${NC}"
    echo "   Generate one with: openssl rand -hex 32"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Install with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check Docker Compose (v2 or v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed (${COMPOSE_CMD})${NC}"

# Check if ports are available
echo ""
echo "🔍 Checking port availability..."
PORT_80_IN_USE=false
PORT_443_IN_USE=false

if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ':80 '; then
    echo -e "${YELLOW}⚠️  Port 80 is already in use${NC}"
    PORT_80_IN_USE=true
fi

if lsof -Pi :443 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ':443 '; then
    echo -e "${YELLOW}⚠️  Port 443 is already in use${NC}"
    PORT_443_IN_USE=true
fi

if [ "$PORT_80_IN_USE" = true ] || [ "$PORT_443_IN_USE" = true ]; then
    echo -e "${YELLOW}   You may need to stop another web server (nginx, apache, etc.)${NC}"
    echo "   Or the previous deployment is still running"
    echo ""
    # Skip prompt in non-interactive (CI) mode
    if [ -t 0 ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${YELLOW}   Running in non-interactive mode, continuing...${NC}"
    fi
fi

# Create required directories
echo ""
echo "📁 Creating directories..."
mkdir -p caddy_data caddy_config

# Pull latest images
echo ""
echo "📥 Pulling base images..."
${COMPOSE_CMD} -f docker-compose.prod.yml pull caddy postgres valkey

# Build backend image
echo ""
echo "🔨 Building backend image..."
${COMPOSE_CMD} -f docker-compose.prod.yml build backend

# Build frontend first (this creates the static files)
echo ""
echo "🎨 Building frontend..."
${COMPOSE_CMD} -f docker-compose.prod.yml run --rm frontend-build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

# Start all services
echo ""
echo "🚀 Starting all services..."
${COMPOSE_CMD} -f docker-compose.prod.yml up -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
${COMPOSE_CMD} -f docker-compose.prod.yml exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database migrations completed${NC}"
else
    echo -e "${YELLOW}⚠️  Migration command had issues, but continuing...${NC}"
    echo "   You may need to run migrations manually later"
fi

# Check service health
echo ""
echo "🏥 Checking service health..."
sleep 5

# Function to check if container is running
check_container() {
    local name=$1
    local container=$(${COMPOSE_CMD} -f docker-compose.prod.yml ps -q $name 2>/dev/null)
    if [ -n "$container" ]; then
        local status=$(docker inspect --format='{{.State.Status}}' $container 2>/dev/null)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✅ $name is running${NC}"
            return 0
        else
            echo -e "${RED}❌ $name status: $status${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $name container not found${NC}"
        return 1
    fi
}

check_container "caddy"
check_container "backend"
check_container "postgres"
check_container "valkey"

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "🔗 Access your application:"
echo -e "   ${BLUE}🌐 Website:${NC}    https://ihsan-dz.duckdns.org"
echo -e "   ${BLUE}📚 API Docs:${NC}   https://ihsan-dz.duckdns.org/docs"
echo -e "   ${BLUE}💓 Health:${NC}     https://ihsan-dz.duckdns.org/api/health"
echo ""
echo "📋 Useful commands:"
echo -e "   ${BLUE}View logs:${NC}       ${COMPOSE_CMD} -f docker-compose.prod.yml logs -f"
echo -e "   ${BLUE}Stop services:${NC}   ${COMPOSE_CMD} -f docker-compose.prod.yml down"
echo -e "   ${BLUE}Restart:${NC}         ${COMPOSE_CMD} -f docker-compose.prod.yml restart"
echo -e "   ${BLUE}Update:${NC}          ./deploy.sh"
echo ""
echo "🔒 Security Notes:"
echo "   - HTTPS is automatically managed by Caddy"
echo "   - SSL certificates will auto-renew"
echo "   - Make sure your firewall allows ports 80 and 443"
echo ""
echo -e "${YELLOW}⏰ Note: SSL certificate provisioning may take 1-2 minutes on first run${NC}"
echo ""
