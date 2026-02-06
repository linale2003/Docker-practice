FROM python:3.9-slim

WORKDIR /app

EXPOSE 5000 

LABEL maintainer="practice" \
      version="??" \
      description="image for..."
      
COPY ./requirements.txt .

RUN apt-get update && \
    apt-get install -y \
    curl \
    python3 \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    postgresql \
    postgresql-contrib && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \ 
    rm -rf /var/lib/apt/lists/*

COPY  . .

RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 appuser && \ 
    chown -R appuser:appuser /app

USER appuser 

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]