#!/usr/bin/env bash
set -e

if [ -f "./server/.prod.env" ]; then
  export DOTENV_PATH="./server/.prod.env"
else
  export DOTENV_PATH="./server/.env"
fi

python ./server/manage.py collectstatic --noinput

python ./server/manage.py makemigrations --noinput || true
python ./server/manage.py migrate --noinput

uwsgi --ini ./server/uwsgi.ini