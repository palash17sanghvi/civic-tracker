FROM python:3.12-slim

# Install cron alongside Python so scheduled ingestion can run inside this container
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make scripts executable and install the crontab
RUN chmod +x /app/scripts/refresh_data.sh
RUN crontab /app/scripts/crontab

# Create the log directory cron writes to
RUN mkdir -p /var/log/civic-tracker

EXPOSE 8000

# Start cron in the background, then run gunicorn in the foreground
CMD service cron start && gunicorn civic.wsgi:application --bind 0.0.0.0:8000
