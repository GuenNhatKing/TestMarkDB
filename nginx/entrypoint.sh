#!/usr/bin/env sh
set -e

if [ "$PROD" = "true" ]; then
  export UPSTREAM="127.0.0.1:8000"
else
  export UPSTREAM="web:8000"
fi

mkdir -p /etc/nginx
envsubst '$UPSTREAM' < /etc/nginx/templates/nginx.conf.tmpl > /etc/nginx/nginx.conf
exec nginx -g 'daemon off;'