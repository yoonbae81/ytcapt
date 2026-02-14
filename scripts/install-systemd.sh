#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_NAME="ytcapt"

echo "ytcapt - Systemd Service Installation"
echo "=============================================="
echo "Project directory: $PROJECT_DIR"
echo ""

# Load environment variables from .env
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
    echo "Environment variables loaded from .env"
else
    echo "Warning: .env file not found"
fi

# Create systemd directory
echo "Setting up systemd service..."
mkdir -p "$SYSTEMD_USER_DIR"

# Create service file from template
echo "Creating $SERVICE_NAME.service from template..."
sed "s|{{PROJECT_ROOT}}|$PROJECT_DIR|g" "$SCRIPT_DIR/systemd/$SERVICE_NAME.service" > "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"

echo "Systemd files installed"
echo ""

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl --user daemon-reload

# Enable linger for the user
echo "Enabling linger for user $USER..."
loginctl enable-linger "$USER"

# Enable and start service
echo "Enabling and starting service..."
systemctl --user enable "$SERVICE_NAME.service"
systemctl --user start "$SERVICE_NAME.service"

echo ""
echo "Installation completed!"
echo ""
echo "Useful commands:"
echo "  • Check service status:  systemctl --user status $SERVICE_NAME.service"
echo "  • Check service logs:    journalctl --user -u $SERVICE_NAME.service"
echo "  • Follow logs:           journalctl --user -u $SERVICE_NAME.service -f"
