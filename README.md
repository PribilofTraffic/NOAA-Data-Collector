# NOAA Data Collector

Automated Docker application for collecting real-time data from Alaska NOAA buoy and tide stations.

## Quick Start

```bash
cd /opt/dockers
sudo docker compose up -d noaa-collector
```

Or use the helper script:
```bash
cd /opt/dockers/noaa-data-collector
./start.sh
```

## Stations Monitored

- **Buoy 46073**: Southeast Bering Sea (205 NM WNW of Dutch Harbor)
- **Buoy 46035**: Central Bering Sea (310 NM North of Adak)
- **Tide 9464212**: Unalaska, AK

## Data Location

Data is stored in `./data/`:
- `buoy_46073.csv` - Buoy 46073 meteorological data
- `buoy_46035.csv` - Buoy 46035 meteorological data
- `tide_9464212.csv` - Tide station water level data
- `collector.log` - Application logs

## Common Commands

```bash
# Start collector
cd /opt/dockers
sudo docker compose up -d noaa-collector

# Stop collector
sudo docker compose stop noaa-collector

# View logs
sudo docker compose logs -f noaa-collector

# Check status
sudo docker compose ps noaa-collector

# Restart collector
sudo docker compose restart noaa-collector
```

Or use the helper scripts from `/opt/dockers/noaa-data-collector/`:
```bash
./start.sh   # Start
./stop.sh    # Stop
./logs.sh    # View logs
./status.sh  # Check status
```

## Configuration

Edit the `.env` file or set environment variables in `docker-compose.yml`:

```env
# Collection interval in seconds (default: 1 hour)
COLLECTION_INTERVAL=3600

# Timezone for timestamps
TZ=America/Anchorage

# NDBC Buoy Stations (comma-separated)
BUOY_STATIONS=46073,46035

# CO-OPS Tide Station
TIDE_STATION=9464212
```

### Monitor Different Stations

**For Atlantic buoys:**
```env
BUOY_STATIONS=41001,41002
TIDE_STATION=8454000
TZ=America/New_York
```

**For Pacific buoys:**
```env
BUOY_STATIONS=51000,51001
TIDE_STATION=9414290
TZ=America/Los_Angeles
```

**For Gulf of Mexico:**
```env
BUOY_STATIONS=42001,42002
TIDE_STATION=8729108
TZ=America/Chicago
```

Find station IDs:
- **Buoys**: https://www.ndbc.noaa.gov/
- **Tides**: https://tidesandcurrents.noaa.gov/

### Change Collection Interval

To collect data more frequently, modify `docker-compose.yml`:

```yaml
environment:
  - COLLECTION_INTERVAL=1800  # 30 minutes in seconds
```

```bash
cd /opt/dockers
sudo docker compose restart noaa-collector
```

## Features

### Complete Timeline Tracking
- **Every collection attempt recorded** - Even when stations are offline
- **Failed attempts marked** - `FAILED` markers maintain timeline continuity
- **No gaps in timeline** - Always know when collections occurred
- **Easy analysis** - Filter out failures or analyze outage patterns

See [TIMELINE.md](TIMELINE.md) for details.

### Station Health Monitoring
- **Station availability and uptime tracking**
- **Outage detection and recovery**
- **Historical performance data**
- **Never generates fake data**
- **Never gives up on stations**

### View Station Status

```bash
cd /opt/dockers/noaa-data-collector
./view_status.sh
```

See [MONITORING.md](MONITORING.md) for complete monitoring documentation.

## Full Documentation

- **[TIMELINE.md](TIMELINE.md)** - Timeline continuity and failed attempt tracking
- **[DATA_DICTIONARY.md](DATA_DICTIONARY.md)** - Complete field definitions and units
- **[MONITORING.md](MONITORING.md)** - Station health monitoring system
- **[docs/README.md](docs/README.md)** - Complete technical documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[INTEGRATION.md](INTEGRATION.md)** - Docker integration details

## Timezone

All timestamps are in **America/Anchorage** timezone.

## Where this came from

The idea is older than the AI help. It began years ago as a hand-written script that collected buoy and tide
readings for the waters around the islands.
It was written and run that way, without AI, long before any was involved.

AI came later, as an assistant. Claude helped tidy the code, add tests, find
bugs and package it as a container other people can run. The ideas, and the
judgement about what matters on these islands, are the maintainer's own.

Most of the Pribilof Traffic collectors started on Raspberry Pis, and
Raspberry Pis on the islands still run the webcam and the aircraft (tar1090)
and ACARS receivers today.

## License

MIT. See [LICENSE](LICENSE).
