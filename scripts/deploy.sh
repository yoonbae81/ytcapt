#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
SERVICE_NAME="ytcapt"

echo "Starting deployment for $SERVICE_NAME..."

# 1. Pull latest code
echo "Pulling latest changes from git..."
git pull origin main

# 2. Update dependencies
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Updating dependencies..."
    "$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
fi

# 3. Restart services
echo "Restarting service..."
systemctl --user restart "$SERVICE_NAME.service"

echo "Deployment completed successfully!"
