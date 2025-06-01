#!/bin/bash
# Local Development Script

echo "🛠️ STARTING LOCAL DEVELOPMENT..."

# Install dependencies
pip install -r requirements.txt

# Start Redis (if Docker is available)
if command -v docker >/dev/null 2>&1; then
    echo "🔴 Starting Redis with Docker..."
    docker run -d --name redis-dev -p 6379:6379 redis:7-alpine || echo "Redis container already running"
fi

# Start the application
echo "🚀 Starting application..."
python main_app.py
