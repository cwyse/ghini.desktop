#!/bin/sh
set -e
# entrypoint.sh  (top of the file)
[ -f /VERSION_ENV ] && export $(cat /VERSION_ENV)

echo "💡 Entry point: DEBUG=$DEBUG"

if [ "$DEBUG" = "true" ]; then
    echo "🔍 Starting with debugpy..."
    exec python3 -m debugpy --wait-for-client --log-to /app/debugpy.log --listen 0.0.0.0:5678 -m /app/scripts/ghini
else
    echo "🚀 Starting normally..."
    exec /app/scripts/ghini
fi
