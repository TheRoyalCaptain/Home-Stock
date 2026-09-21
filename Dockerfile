FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/TheRoyalCaptain/Home-Stock" \
      org.opencontainers.image.description="Self-hosted household stock and expiry tracker for umbrelOS" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME_STOCK_DATA_DIR=/data

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
      cups cups-client cups-filters printer-driver-dymo \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py auth.py printer_service.py print-service-entrypoint.sh ./
COPY templates templates
COPY static static

RUN chmod 0755 /app/print-service-entrypoint.sh \
    && mkdir -p /data && chown -R 1000:1000 /app /data
USER 1000:1000

EXPOSE 8080
VOLUME ["/data"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app:app"]
