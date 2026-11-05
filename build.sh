#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install production dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files with WhiteNoise
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Seed initial store data and admin user
python manage.py seed_data
