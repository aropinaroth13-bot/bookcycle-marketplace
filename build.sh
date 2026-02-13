#!/usr/bin/env bash
# Render build script

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate --no-input

# Seed demo data (only runs if data doesn't exist)
python manage.py seed_data || echo "Seed data already exists or failed"
