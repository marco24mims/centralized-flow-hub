#!/bin/bash

# CFH Project - Systemd Service Installation Script

echo "=== CFH Project Systemd Service Installation ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run with sudo"
    echo "Usage: sudo ./install-service.sh"
    exit 1
fi

# Create log directory
echo "Creating log directory..."
mkdir -p /var/log/cfh-project
chown laraveluat:laraveluat /var/log/cfh-project
echo "✓ Log directory created"

# Copy service file to systemd
echo ""
echo "Installing systemd service..."
cp cfh-project.service /etc/systemd/system/
chmod 644 /etc/systemd/system/cfh-project.service
echo "✓ Service file installed"

# Reload systemd
echo ""
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd reloaded"

# Enable service (start on boot)
echo ""
echo "Enabling service to start on boot..."
systemctl enable cfh-project.service
echo "✓ Service enabled"

# Start the service
echo ""
echo "Starting CFH Project service..."
systemctl start cfh-project.service
echo "✓ Service started"

# Show status
echo ""
echo "=== Service Status ==="
systemctl status cfh-project.service --no-pager

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status cfh-project    # Check status"
echo "  sudo systemctl start cfh-project     # Start service"
echo "  sudo systemctl stop cfh-project      # Stop service"
echo "  sudo systemctl restart cfh-project   # Restart service"
echo "  sudo systemctl logs -u cfh-project   # View logs"
echo "  sudo journalctl -u cfh-project -f    # Follow logs in real-time"
echo ""
echo "Log files:"
echo "  /var/log/cfh-project/access.log      # Access logs"
echo "  /var/log/cfh-project/error.log       # Error logs"
echo ""
