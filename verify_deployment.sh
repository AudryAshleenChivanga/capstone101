#!/bin/bash
# ================================================
# Deployment Verification Script
# ================================================
# Run this on your Oracle instance to verify deployment

set -e

echo "================================================"
echo "  H. pylori CDSS - Deployment Verification"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[i] $1${NC}"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" &> /dev/null; then
        print_success "PASS"
        ((TESTS_PASSED++))
        return 0
    else
        print_error "FAIL"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "System Checks:"
echo "----------------------------------------"

# 1. Docker installed
run_test "Docker installed" "docker --version"

# 2. Docker Compose installed
run_test "Docker Compose installed" "docker-compose --version"

# 3. Docker daemon running
run_test "Docker daemon running" "docker info"

echo ""
echo "Application Checks:"
echo "----------------------------------------"

# 4. Application directory exists
run_test "Application directory exists" "test -d ~/hpylori-cdss"

# 5. .env file exists
cd ~/hpylori-cdss 2>/dev/null || true
run_test ".env file exists" "test -f .env"

# 6. Required files exist
run_test "docker-compose.yml exists" "test -f docker-compose.yml"
run_test "Dockerfile exists" "test -f Dockerfile"
run_test "requirements.txt exists" "test -f requirements.txt"
run_test "main.py exists" "test -f main.py"

# 7. Models directory exists
run_test "Models directory exists" "test -d models"

# 8. UI directory exists
run_test "UI directory exists" "test -d ui"

echo ""
echo "Container Checks:"
echo "----------------------------------------"

# 9. Container running
if docker-compose ps | grep -q "Up"; then
    print_success "Container is running"
    ((TESTS_PASSED++))
else
    print_error "Container is not running"
    ((TESTS_FAILED++))
fi

# 10. Health check endpoint
if curl -f http://localhost:8000/health &> /dev/null; then
    print_success "Health check endpoint responding"
    ((TESTS_PASSED++))
    
    # Display health check response
    echo ""
    print_info "Health check response:"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    print_error "Health check endpoint not responding"
    ((TESTS_FAILED++))
fi

echo ""
echo "Network Checks:"
echo "----------------------------------------"

# 11. Port 8000 listening
if ss -tlnp 2>/dev/null | grep -q ":8000" || netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    print_success "Port 8000 is listening"
    ((TESTS_PASSED++))
else
    print_error "Port 8000 is not listening"
    ((TESTS_FAILED++))
fi

# 12. Firewall rules
print_info "Checking firewall rules..."
if sudo ufw status | grep -q "8000.*ALLOW"; then
    print_success "Firewall allows port 8000"
    ((TESTS_PASSED++))
else
    print_warning "Firewall may not allow port 8000"
    ((TESTS_FAILED++))
fi

echo ""
echo "Security Checks:"
echo "----------------------------------------"

# 13. .env file permissions
if [ -f .env ]; then
    PERMS=$(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null)
    if [ "$PERMS" == "600" ]; then
        print_success ".env file has secure permissions (600)"
        ((TESTS_PASSED++))
    else
        print_warning ".env file permissions are $PERMS (should be 600)"
        print_info "Fix with: chmod 600 .env"
        ((TESTS_FAILED++))
    fi
fi

# 14. Default SECRET_KEY check
if grep -q "your-super-secret-key-change-this" .env 2>/dev/null; then
    print_error "DEFAULT SECRET_KEY detected - CHANGE THIS!"
    ((TESTS_FAILED++))
else
    print_success "SECRET_KEY appears to be customized"
    ((TESTS_PASSED++))
fi

echo ""
echo "Resource Usage:"
echo "----------------------------------------"

# Disk space
print_info "Disk usage:"
df -h / | tail -n 1

# Memory
print_info "Memory usage:"
free -h | grep Mem

# Docker stats
print_info "Container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "  Not available"

echo ""
echo "Endpoint Tests:"
echo "----------------------------------------"

# Test root endpoint
if curl -f -s http://localhost:8000/ &> /dev/null; then
    print_success "Root endpoint (/) accessible"
    ((TESTS_PASSED++))
else
    print_warning "Root endpoint (/) not accessible"
    ((TESTS_FAILED++))
fi

# Test UI
if curl -f -s http://localhost:8000/ui/index.html &> /dev/null; then
    print_success "UI index page accessible"
    ((TESTS_PASSED++))
else
    print_error "UI index page not accessible"
    ((TESTS_FAILED++))
fi

# Test API docs
if curl -f -s http://localhost:8000/docs &> /dev/null; then
    print_success "API documentation accessible"
    ((TESTS_PASSED++))
else
    print_warning "API documentation not accessible"
    ((TESTS_FAILED++))
fi

echo ""
echo "================================================"
echo "  Verification Summary"
echo "================================================"
echo ""
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your deployment is healthy!${NC}"
    echo ""
    echo "Access your application at:"
    echo "  Main App: http://$(curl -s ifconfig.me):8000"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please review the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  1. Restart containers: docker-compose restart"
    echo "  2. Check logs: docker-compose logs -f"
    echo "  3. Rebuild: docker-compose down && docker-compose up -d --build"
    echo ""
    exit 1
fi

