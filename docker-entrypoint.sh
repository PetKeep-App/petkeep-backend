#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL..."

# Wait for PostgreSQL to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
