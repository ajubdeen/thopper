#!/bin/bash
# Kill any process using port 5000 before starting the server
# This prevents EADDRINUSE errors on restart

echo "Cleaning up port 5000..."
fuser -k 5000/tcp 2>/dev/null || true

# Small delay to ensure port is released
sleep 0.5

echo "Starting development server..."
NODE_ENV=development tsx server/index.ts
