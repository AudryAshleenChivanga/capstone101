#!/bin/bash
# Quick status check script for H. pylori CDSS
# Run this on your Oracle instance anytime

clear

echo "╔════════════════════════════════════════════╗"
echo "║   H. pylori CDSS - Status Dashboard        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get instance IP
INSTANCE_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo "📍 Instance Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Public IP: $INSTANCE_IP"
echo "   Hostname: $(hostname)"
echo "   Uptime: $(uptime -p 2>/dev/null || uptime)"
echo ""

echo "🐳 Docker Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker info &>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Docker is running"
    
    # Container status
    cd ~/hpylori-cdss 2>/dev/null
    if [ -f docker-compose.yml ]; then
        CONTAINER_STATUS=$(docker-compose ps 2>/dev/null | grep "hpylori-cdss" | awk '{print $4}')
        if [ "$CONTAINER_STATUS" == "Up" ]; then
            echo -e "   ${GREEN}✓${NC} Container is running"
        else
            echo -e "   ${RED}✗${NC} Container is not running"
        fi
    fi
else
    echo -e "   ${RED}✗${NC} Docker is not running"
fi
echo ""

echo "🏥 Application Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -f -s http://localhost:8000/health &>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Application is healthy"
    HEALTH_DATA=$(curl -s http://localhost:8000/health)
    echo "   Response: $HEALTH_DATA"
else
    echo -e "   ${RED}✗${NC} Application is not responding"
fi
echo ""

echo "🌐 Access URLs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Main App: http://$INSTANCE_IP:8000"
echo "   Health: http://$INSTANCE_IP:8000/health"
echo "   API Docs: http://$INSTANCE_IP:8000/docs"
echo "   Login: http://$INSTANCE_IP:8000/ui/login.html"
echo ""

echo "💾 Resources"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Disk usage
DISK_USAGE=$(df -h / | tail -n 1 | awk '{print $5}')
DISK_AVAIL=$(df -h / | tail -n 1 | awk '{print $4}')
echo "   Disk: $DISK_USAGE used ($DISK_AVAIL available)"

# Memory
MEM_USAGE=$(free -h | grep Mem | awk '{print $3 "/" $2}')
echo "   Memory: $MEM_USAGE"

# Container resources
if docker stats --no-stream &>/dev/null; then
    CONTAINER_CPU=$(docker stats --no-stream --format "{{.CPUPerc}}" hpylori-cdss 2>/dev/null)
    CONTAINER_MEM=$(docker stats --no-stream --format "{{.MemUsage}}" hpylori-cdss 2>/dev/null)
    if [ -n "$CONTAINER_CPU" ]; then
        echo "   Container CPU: $CONTAINER_CPU"
        echo "   Container Mem: $CONTAINER_MEM"
    fi
fi
echo ""

echo "📊 Recent Activity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d ~/hpylori-cdss ]; then
    cd ~/hpylori-cdss
    echo "   Last 5 log entries:"
    docker-compose logs --tail=5 2>/dev/null | sed 's/^/   /'
else
    echo "   Application directory not found"
fi
echo ""

echo "🔧 Quick Commands"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   View logs:     docker-compose logs -f"
echo "   Restart:       docker-compose restart"
echo "   Stop:          docker-compose down"
echo "   Start:         docker-compose up -d"
echo "   Full check:    ./verify_deployment.sh"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║   Press any key to exit                    ║"
echo "╚════════════════════════════════════════════╝"

