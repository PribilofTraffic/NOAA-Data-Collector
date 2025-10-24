#!/bin/bash
# View logs from the NOAA Data Collector

echo "Viewing NOAA Data Collector logs (Ctrl+C to exit)..."
echo ""
cd /opt/dockers
sudo docker compose logs -f noaa-collector
