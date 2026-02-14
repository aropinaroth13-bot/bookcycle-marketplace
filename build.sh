#!/usr/bin/env bash
# Render build script

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Create and run migrations
echo "Creating new migrations..."
python manage.py makemigrations --no-input

echo "Running migrations..."
python manage.py migrate --no-input

echo "Build completed successfully!"
