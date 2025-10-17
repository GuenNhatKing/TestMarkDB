FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential libpq-dev uwsgi-plugin-python3
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/

RUN chmod +x ./server/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./server/entrypoint.sh"]