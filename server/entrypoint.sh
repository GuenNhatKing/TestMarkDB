#!/usr/bin/env bash
set -e

cd /app/server

python ./manage.py collectstatic --noinput

python ./manage.py makemigrations --noinput || true
python ./manage.py migrate --noinput

echo $@