#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Create superuser
if [ "$CREATE_SUPERUSER" = "true" ]; then
  export DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD"
  python manage.py createsuperuser \
      --noinput \
      --username "$SUPERUSER_USERNAME" \
      --email "$SUPERUSER_EMAIL" || true
fi