#!/bin/bash
# ==============================================
# H. pylori CDSS - Deployment Script
# ==============================================

set -e  # Exit on error

echo "================================================"
echo "  H. pylori CDSS - Production Deployment"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo "Please create .env file from env.template:"
    echo "  cp env.template .env"
    echo "  nano .env  # Edit with your actual values"
    exit 1
fi

print_success ".env file found"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

print_success "Docker Compose is installed"

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
print_success "Containers stopped"

# Build the Docker image
echo ""
echo "Building Docker image..."
docker-compose build --no-cache
print_success "Docker image built"

# Start the containers
echo ""
echo "Starting containers..."
docker-compose up -d
print_success "Containers started"

# Wait for the application to be ready
echo ""
echo "Waiting for application to be ready..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000/health &> /dev/null; then
    print_success "Application is running!"
else
    print_warning "Application may not be ready yet. Checking logs..."
    docker-compose logs --tail=50
fi

echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "Access your application at:"
echo "  🌐 http://localhost:8000"
echo "  📊 Dashboard: http://localhost:8000/ui/dashboard_new.html"
echo "  🔐 Login: http://localhost:8000/ui/login.html"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop the application:"
echo "  docker-compose down"
echo ""

