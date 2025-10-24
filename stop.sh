#!/bin/bash
# Stop the NOAA Data Collector

echo "Stopping NOAA Data Collector..."
cd /opt/dockers
sudo docker compose stop noaa-collector

echo ""
echo "Container stopped."
