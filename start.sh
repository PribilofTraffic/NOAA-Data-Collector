#!/bin/bash
# Start the NOAA Data Collector

echo "Starting NOAA Data Collector..."
cd /opt/dockers
sudo docker compose up -d noaa-collector

echo ""
echo "Waiting for container to start..."
sleep 3

echo ""
echo "Container status:"
sudo docker compose ps noaa-collector

echo ""
echo "To view logs, run: cd /opt/dockers && sudo docker compose logs -f noaa-collector"
echo "To stop, run: cd /opt/dockers && sudo docker compose stop noaa-collector"
