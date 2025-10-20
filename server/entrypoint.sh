#!/usr/bin/env bash
set -e

cd /app/server

python ./manage.py collectstatic --noinput

python ./manage.py makemigrations --noinput || true
python ./manage.py migrate --noinput

if [ "$PROD" = "true" ]; then
  echo "Production mode detected."

  if [ "$RUN_APP" = "true" ]; then
    echo "Starting uwsgi server..."
    exec uwsgi --ini ./uwsgi.ini
  elif [ "$RUN_CELERY" = "true" ]; then
    echo "Starting Celery worker..."
    exec celery -A root worker --loglevel=INFO --pool=threads
  else
    echo "No RUN_APP or RUN_CELERY environment variable found."
    exit 1
  fi

else
  echo "Development mode detected. Running custom command..."
  exec "$@"
fi