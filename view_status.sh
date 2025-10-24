#!/bin/bash
# View station health status report

cd /opt/dockers

echo "Fetching station health report..."
echo ""

# Check if report file exists
if sudo docker compose exec noaa-collector test -f /app/data/station_report.txt; then
    sudo docker compose exec noaa-collector cat /app/data/station_report.txt
else
    echo "No station report available yet. Collector may still be initializing."
    echo "Check back after the first collection cycle completes."
fi
