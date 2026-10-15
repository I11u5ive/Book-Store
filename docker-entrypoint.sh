#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
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
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "Starting service: $*"
exec "$@"
