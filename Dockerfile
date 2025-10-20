FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
&& apt-get install -y --no-install-recommends build-essential \
&& rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 24816 app \
&& adduser --system --uid 24816 --ingroup app --home /app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/

EXPOSE 8000

RUN chown -R app:app /app
USER app

ENTRYPOINT ["./server/entrypoint.sh"]