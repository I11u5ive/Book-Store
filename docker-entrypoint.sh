#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

until python -c "
import os
import psycopg
from urllib.parse import urlparse

url = os.environ['DATABASE_URL']
result = urlparse(url)

psycopg.connect(
    host=result.hostname,
    port=result.port,
    user=result.username,
    password=result.password,
    dbname=result.path.lstrip('/')
).close()
" 2>/dev/null
do
    sleep 1
done

echo "PostgreSQL is ready!"

echo "Running migrations..."

python manage.py migrate

echo "Collecting static files..."

python manage.py collectstatic --noinput

echo "Starting Django..."

exec python manage.py runserver 0.0.0.0:8000