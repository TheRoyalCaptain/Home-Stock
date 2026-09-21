FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME_STOCK_DATA_DIR=/data

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates templates
COPY static static

RUN mkdir -p /data && chown -R 1000:1000 /app /data
USER 1000:1000

EXPOSE 8080
VOLUME ["/data"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app:app"]
