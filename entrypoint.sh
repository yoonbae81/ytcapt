#!/bin/sh

# Clone if repo not exists, else pull latest
if [ ! -d /app/.git ]; then
  git clone https://github.com/yoonbae81/ytcapt.git /app
else
  git -C /app pull origin main
fi

# Install dependencies only if requirements.txt changed
REQUIREMENTS_HASH_FILE="/tmp/requirements.hash"
CURRENT_HASH=$(md5sum /app/requirements.txt | cut -d' ' -f1)

if [ ! -f "$REQUIREMENTS_HASH_FILE" ] || [ "$(cat $REQUIREMENTS_HASH_FILE)" != "$CURRENT_HASH" ]; then
  echo "Installing dependencies..."
  pip install --no-cache-dir -r /app/requirements.txt
  echo "$CURRENT_HASH" > "$REQUIREMENTS_HASH_FILE"
else
  echo "Dependencies already up to date, skipping installation."
fi

# Run the app with port (default: 8001) in production mode (default: enabled)
PORT=${PORT:-8001}
PRODUCTION_MODE=${PRODUCTION_MODE:-true}

if [ "$PRODUCTION_MODE" = "true" ]; then
  echo "Starting in PRODUCTION mode..."
  python /app/src/app.py --port $PORT --production
else
  echo "Starting in DEVELOPMENT mode..."
  python /app/src/app.py --port $PORT
fi
