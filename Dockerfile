FROM python:3.11.14-slim-bookworm AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài uWSGI
RUN pip install --no-cache-dir uWSGI==2.0.31 --prefix=/install

# Cài Torch và TorchVision
RUN pip install --no-cache-dir torch==2.9.0 torchvision==0.24.0 \
--index-url https://download.pytorch.org/whl/cpu --prefix=/install

# Cài ultralytics nhưng không kéo thêm deps
RUN pip install --no-cache-dir ultralytics --no-deps --prefix=/install

# Cài toàn bộ requirements còn lại
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --no-deps \
--prefix=/install

FROM python:3.11.14-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 24816 app \
&& adduser --system --uid 24816 --ingroup app --home /app app

WORKDIR /app

# copy thư viện đã cài sẵn từ builder
COPY --from=builder /install /usr/local
COPY server/ ./server/

EXPOSE 8000

RUN mkdir -p /app/.config/Ultralytics \
    && mkdir -p /app/server/temporary \
    && chown -R app:app /app
    
USER app

RUN chmod +x ./server/entrypoint.sh
ENTRYPOINT ["./server/entrypoint.sh"]