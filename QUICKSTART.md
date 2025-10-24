# NOAA Data Collector - Quick Start Guide

## What This Does

Automatically collects oceanographic data every hour from:
- **Buoy 46073** (Southeast Bering Sea)
- **Buoy 46035** (Central Bering Sea)  
- **Tide Station 9464212** (Unalaska, AK)

Data is saved to CSV files in the `data/` directory.

## Installation & Usage

### 1. Start the Collector

```bash
cd /opt/dockers/noaa-data-collector
./start.sh
```

Or manually from the main docker directory:
```bash
cd /opt/dockers
sudo docker compose up -d noaa-collector
```

### 2. Check Status

```bash
./status.sh
```

### 3. View Live Logs

```bash
./logs.sh
```

Press `Ctrl+C` to exit logs.

### 4. Stop the Collector

```bash
./stop.sh
```

Or manually from the main docker directory:
```bash
cd /opt/dockers
sudo docker compose stop noaa-collector
```

## Data Files

All data is stored in `./data/`:

- `buoy_46073.csv` - Southeast Bering Sea buoy data
- `buoy_46035.csv` - Central Bering Sea buoy data
- `tide_9464212.csv` - Unalaska tide station data
- `collector.log` - Application logs

## Configuration

Edit `/opt/dockers/docker-compose.yml` to change collection frequency in the `noaa-collector` service:

```yaml
environment:
  - COLLECTION_INTERVAL=3600  # seconds (3600 = 1 hour)
```

Common intervals:
- 30 minutes: `1800`
- 1 hour: `3600` (default)
- 2 hours: `7200`
- 6 hours: `21600`

After changing, restart:
```bash
cd /opt/dockers
sudo docker compose restart noaa-collector
```

## Viewing Data

```bash
# View latest buoy data
tail data/buoy_46073.csv

# Count total records
wc -l data/*.csv

# View in spreadsheet
libreoffice data/buoy_46073.csv
```

## Troubleshooting

### Container won't start
```bash
sudo docker compose logs
```

### No data being collected
1. Check logs: `./logs.sh`
2. Verify internet connection
3. Check NOAA services are online

### Permission errors
```bash
sudo chown -R $USER:$USER data/
```

## Full Documentation

See `docs/README.md` for complete documentation.

## Data Sources

- **NDBC**: https://www.ndbc.noaa.gov/
- **CO-OPS**: https://tidesandcurrents.noaa.gov/

All timestamps are in **America/Anchorage** timezone.
