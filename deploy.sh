#!/bin/bash

# Ihsane MVP Platform - Production Deployment Script
# Domain: ihsan-dz.duckdns.org
# Architecture: Caddy-only (no Nginx)

set -e  # Exit on any error
set -x  # Print commands for debugging

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
NC='\033[0m'

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.prod.example...${NC}"
    
    if [ -f .env.prod.example ]; then
        cp .env.prod.example .env
        
        # Generate secure defaults for required values
        GENERATED_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p -c 64 | head -n 1)
        GENERATED_PG_PASS=$(openssl rand -base64 24 2>/dev/null || head -c 32 /dev/urandom | base64 | head -c 24)
        
        sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${GENERATED_PG_PASS}|" .env
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${GENERATED_SECRET}|" .env
        
        echo -e "${GREEN}✅ .env created with generated secrets${NC}"
    else
        echo -e "${RED}❌ Error: Neither .env nor .env.prod.example found!${NC}"
        exit 1
    fi
fi

# Load environment variables safely (handle lines with spaces)
set +e
while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue
    # Export the variable
    export "$line" 2>/dev/null || true
done < .env
set -e

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

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "   Start with: sudo systemctl start docker"
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

echo -e "${GREEN}✅ Docker is installed and running (${COMPOSE_CMD})${NC}"

# Create required directories
echo ""
echo "📁 Creating directories..."
mkdir -p caddy_data caddy_config

# Pull latest images
echo ""
echo "📥 Pulling base images..."
${COMPOSE_CMD} -f docker-compose.prod.yml pull caddy postgres valkey || true

# Build backend image
echo ""
echo "🔨 Building backend image..."
${COMPOSE_CMD} -f docker-compose.prod.yml build backend

# Build frontend (creates static files in shared volume)
echo ""
echo "🎨 Building frontend..."
${COMPOSE_CMD} -f docker-compose.prod.yml run --rm frontend-build

echo -e "${GREEN}✅ Frontend build successful${NC}"

# Stop any existing services first (for clean restart)
echo ""
echo "🔄 Stopping any existing services..."
${COMPOSE_CMD} -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Forcefully remove specifically named containers to avoid daemon conflicts
docker rm -f ihsane-postgres ihsane-valkey ihsane-backend ihsane-celery-worker ihsane-celery-beat ihsane-caddy ihsane-frontend-build 2>/dev/null || true

# Start all services
echo ""
echo "🧹 Checking for port conflicts on 80/443..."

# Check if our ports are already in use
if sudo ss -tulnp | grep -E ':(80|443) ' | grep -q 'docker-proxy'; then
    echo "⚠️  A Docker container is using port 80/443! Stopping it..."
    for c in $(docker ps -q); do
        if docker port $c 2>/dev/null | grep -qE ':(80|443)$'; then
            echo "Stopping conflicting container: $c"
            docker stop $c
        fi
    done
fi

if command -v fuser >/dev/null; then
    sudo fuser -k 80/tcp 2>/dev/null || true
    sudo fuser -k 443/tcp 2>/dev/null || true
fi
sleep 2

echo "🚀 Starting all services..."
${COMPOSE_CMD} -f docker-compose.prod.yml up -d

# Wait for database to be ready
echo ""
echo "⏳ Waiting for database to be ready..."
for i in $(seq 1 15); do
    if ${COMPOSE_CMD} -f docker-compose.prod.yml exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres} &>/dev/null; then
        echo -e "${GREEN}✅ Database is ready${NC}"
        break
    fi
    echo "  Waiting... ($i/15)"
    sleep 2
done

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
if ${COMPOSE_CMD} -f docker-compose.prod.yml exec -T backend alembic upgrade head; then
    echo -e "${GREEN}✅ Database migrations completed${NC}"
else
    echo -e "${YELLOW}⚠️  Migration had issues (may need manual run later)${NC}"
fi

# Wait for services to stabilize
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
echo ""
echo "🏥 Checking service health..."
check_container() {
    local name=$1
    local container
    container=$(${COMPOSE_CMD} -f docker-compose.prod.yml ps -q "$name" 2>/dev/null || true)
    if [ -n "$container" ]; then
        local status
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✅ $name is running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  $name status: $status${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  $name container not found (may still be starting)${NC}"
        return 1
    fi
}

check_container "caddy" || true
check_container "backend" || true
check_container "postgres" || true
check_container "valkey" || true

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "🔗 Access your application:"
echo -e "   ${BLUE}🌐 Website:${NC}    https://ihsan-dz.duckdns.org"
echo -e "   ${BLUE}📚 API Docs:${NC}   https://ihsan-dz.duckdns.org/docs"
echo -e "   ${BLUE}💓 Health:${NC}     https://ihsan-dz.duckdns.org/api/health"
echo -e "   ${BLUE}🌐 HTTP (dev):${NC}  http://ihsan-dz.duckdns.org"
echo ""
echo "⚠️  Note: We are now using standard ports 80/443 for automatic Let's Encrypt certificates."
echo ""
echo "📋 Useful commands:"
echo -e "   ${BLUE}View logs:${NC}       ${COMPOSE_CMD} -f docker-compose.prod.yml logs -f"
echo -e "   ${BLUE}Stop services:${NC}   ${COMPOSE_CMD} -f docker-compose.prod.yml down"
echo -e "   ${BLUE}Restart:${NC}         ${COMPOSE_CMD} -f docker-compose.prod.yml restart"
echo ""
echo "🔒 HTTPS is auto-managed by Caddy (Let's Encrypt)"
echo -e "${YELLOW}⏰ SSL provisioning takes 1-2 min on first run${NC}"
echo ""