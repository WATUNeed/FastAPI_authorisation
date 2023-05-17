#!/bin/sh

# Collect static files
echo "Collect static files"
alembic revision --autogenerate -m "init"

# Apply database migrations
echo "Apply database migrations"
alembic upgrade head

# Start server
echo "Starting server"
python3 /main.py