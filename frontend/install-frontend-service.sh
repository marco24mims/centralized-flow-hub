#!/bin/bash

# CFH Project - Frontend Systemd Service Installation Script

echo "=== CFH Project Frontend Systemd Service Installation ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run with sudo"
    echo "Usage: sudo ./install-frontend-service.sh"
    exit 1
fi

# Check if 'serve' is installed globally
if ! command -v serve &> /dev/null; then
    echo "Error: 'serve' is not installed globally"
    echo "Please install it first:"
    echo "  sudo npm install -g serve"
    exit 1
fi

# Check if build directory exists
if [ ! -d "build" ]; then
    echo "Error: build directory not found"
    echo "Please build the React app first:"
    echo "  npm run build"
    exit 1
fi

# Log directory should already exist from backend installation
# But create it if it doesn't
if [ ! -d "/var/log/cfh-project" ]; then
    echo "Creating log directory..."
    mkdir -p /var/log/cfh-project
    chown laraveluat:laraveluat /var/log/cfh-project
    echo "[OK] Log directory created"
fi

# Copy service file to systemd
echo ""
echo "Installing systemd service..."
cp cfh-frontend.service /etc/systemd/system/
chmod 644 /etc/systemd/system/cfh-frontend.service
echo "[OK] Service file installed"

# Reload systemd
echo ""
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "[OK] Systemd reloaded"

# Enable service (start on boot)
echo ""
echo "Enabling service to start on boot..."
systemctl enable cfh-frontend.service
echo "[OK] Service enabled"

# Start the service
echo ""
echo "Starting CFH Project Frontend service..."
systemctl start cfh-frontend.service
echo "[OK] Service started"

# Show status
echo ""
echo "=== Service Status ==="
systemctl status cfh-frontend.service --no-pager

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status cfh-frontend    # Check status"
echo "  sudo systemctl start cfh-frontend     # Start service"
echo "  sudo systemctl stop cfh-frontend      # Stop service"
echo "  sudo systemctl restart cfh-frontend   # Restart service"
echo "  sudo journalctl -u cfh-frontend -f    # Follow logs in real-time"
echo ""
echo "Frontend will be available at:"
echo "  http://localhost:3000"
echo "  http://10.50.10.68:3000 (from other machines)"
echo ""
