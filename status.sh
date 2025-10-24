#!/bin/bash
# Check status of NOAA Data Collector

cd /opt/dockers

echo "=== Container Status ==="
sudo docker compose ps noaa-collector

echo ""
echo "=== Recent Logs (last 20 lines) ==="
sudo docker compose logs --tail=20 noaa-collector

echo ""
echo "=== Data Files ==="
if [ -d "noaa-data-collector/data" ]; then
    ls -lh noaa-data-collector/data/
else
    echo "Data directory not found"
fi

echo ""
echo "=== Disk Usage ==="
if [ -d "noaa-data-collector/data" ]; then
    du -sh noaa-data-collector/data/
else
    echo "Data directory not found"
fi
