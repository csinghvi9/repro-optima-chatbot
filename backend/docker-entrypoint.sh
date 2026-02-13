#!/bin/bash
# Start MongoDB in background
mongod --dbpath /data/db --bind_ip 127.0.0.1 &

# Wait for Mongo to be ready (basic check)
sleep 5

# Start FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port 8001
