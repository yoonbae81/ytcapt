#!/bin/sh

# Clone if repo not exists, else pull latest
if [ ! -d /app/.git ]; then
  git clone https://github.com/yoonbae81/ytcapt.git /app
else
  git -C /app pull origin main
fi

# Install dependencies every time for simplicity (optional, can optimize)
pip install --no-cache-dir -r /app/requirements.txt

# Run the app with port (default: 8001)
PORT=${PORT:-8001}
python /app/src/app.py --port $PORT
