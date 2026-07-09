#!/bin/bash
# refresh_data.sh
# Runs all three ingestion pipelines in sequence and logs output.
# Triggered every 6 hours by cron inside the backend container.

LOG_FILE="/var/log/civic-tracker/refresh.log"
mkdir -p /var/log/civic-tracker

echo "===== Refresh started: $(date) =====" >> "$LOG_FILE"

cd /app || exit 1

echo "--- Fetching Congress members ---" >> "$LOG_FILE"
python manage.py fetch_congress_data >> "$LOG_FILE" 2>&1

echo "--- Fetching bills ---" >> "$LOG_FILE"
python manage.py fetch_bills_data >> "$LOG_FILE" 2>&1

echo "--- Fetching FEC fundraising data ---" >> "$LOG_FILE"
python manage.py fetch_fec_data >> "$LOG_FILE" 2>&1

echo "===== Refresh finished: $(date) =====" >> "$LOG_FILE"
