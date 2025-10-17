#!/usr/bin/env bash
set -e

python ./server/manage.py collectstatic --noinput

python ./server/manage.py makemigrations --noinput || true
python ./server/manage.py migrate --noinput

uwsgi --ini ./server/uwsgi.ini