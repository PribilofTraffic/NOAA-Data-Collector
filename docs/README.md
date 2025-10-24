# NOAA Data Collector

A Docker-based application that collects real-time oceanographic data from NOAA buoy stations and tide gauges in Alaska waters.

## Overview

This application automatically collects and stores data from:

### NDBC Buoy Stations
- **Station 46073** - Southeast Bering Sea (205 NM WNW of Dutch Harbor, AK)
  - Location: 55.008°N, 172.012°W
  - Measurements: Wind speed/direction, wave height, air/water temperature, pressure
  
- **Station 46035** - Central Bering Sea (310 NM North of Adak, AK)
  - Location: 57.034°N, 177.468°W
  - Measurements: Wind speed/direction, wave height, air/water temperature, pressure

### CO-OPS Tide Station
- **Station 9464212** - Unalaska, AK
  - Measurements: Water level, tide predictions

## Features

- **Automated Collection**: Runs continuously with configurable collection intervals
- **Timezone Support**: All timestamps are in America/Anchorage timezone
- **Data Persistence**: Stores data in CSV format with append mode
- **Error Handling**: Robust error handling with logging
- **Docker-based**: Easy deployment and management
- **Type Hints**: Full Python type annotations following PEP8

## Project Structure

```
noaa-data-collector/
├── app/
│   └── collector.py          # Main data collection script
├── data/                      # Data storage directory (created on run)
│   ├── buoy_46073.csv        # Buoy 46073 data
│   ├── buoy_46035.csv        # Buoy 46035 data
│   ├── tide_9464212.csv      # Tide station data
│   └── collector.log         # Application logs
├── docs/
│   └── README.md             # This file
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker image definition
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment configuration
└── .gitignore               # Git ignore rules
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Internet connection for accessing NOAA APIs

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /opt/dockers/noaa-data-collector
   ```

2. **Create environment configuration (optional):**
   ```bash
   cp .env.example .env
   # Edit .env to customize settings if needed
   ```

3. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

4. **Verify the container is running:**
   ```bash
   docker-compose ps
   ```

## Usage

### Starting the Collector

```bash
docker-compose up -d
```

### Stopping the Collector

```bash
docker-compose down
```

### Viewing Logs

```bash
# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Accessing Data

Data files are stored in the `./data` directory:

```bash
# View buoy data
cat data/buoy_46073.csv
cat data/buoy_46035.csv

# View tide data
cat data/tide_9464212.csv

# View application logs
cat data/collector.log
```

### Configuration

Edit `docker-compose.yml` or create a `.env` file to customize:

- **COLLECTION_INTERVAL**: Time between data collections in seconds (default: 3600 = 1 hour)
- **TZ**: Timezone for timestamps (default: America/Anchorage)

Example `.env` file:
```bash
COLLECTION_INTERVAL=1800  # Collect every 30 minutes
TZ=America/Anchorage
```

## Data Format

### Buoy Data (NDBC)

CSV files contain real-time meteorological and oceanographic data:

- **Timestamp columns**: Year, Month, Day, Hour, Minute
- **Wind data**: Direction (WDIR), Speed (WSPD), Gust (GST)
- **Wave data**: Height (WVHT), Period (DPD), Direction (MWD)
- **Atmospheric**: Pressure (PRES), Air Temperature (ATMP)
- **Oceanographic**: Water Temperature (WTMP)
- **Metadata**: Station ID, collection timestamp

### Tide Data (CO-OPS)

CSV files contain water level measurements:

- **t**: Timestamp of observation
- **v**: Water level value (feet, MLLW datum)
- **s**: Sigma (standard deviation)
- **f**: Quality flags
- **q**: Quality assurance flags
- **Metadata**: Station ID, collection timestamp

## Data Sources

### NDBC (National Data Buoy Center)
- **API**: https://www.ndbc.noaa.gov/data/realtime2/
- **Documentation**: https://www.ndbc.noaa.gov/faq/measdes.shtml
- **Update Frequency**: Hourly (or more frequent)

### CO-OPS (Center for Operational Oceanographic Products and Services)
- **API**: https://api.tidesandcurrents.noaa.gov/api/prod/
- **Documentation**: https://api.tidesandcurrents.noaa.gov/api/prod/
- **Update Frequency**: 6-minute intervals

## Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker-compose logs

# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### No data being collected

1. Check internet connectivity
2. Verify NOAA services are operational
3. Check application logs: `docker-compose logs -f`
4. Verify data directory permissions

### Data directory permissions

```bash
# Fix permissions if needed
sudo chown -R $USER:$USER data/
```

## Monitoring

### Health Check

```bash
# Check if container is running
docker-compose ps

# Check recent logs
docker-compose logs --tail=50

# Check data files
ls -lh data/
```

### Data Validation

```bash
# Count records in buoy data
wc -l data/buoy_46073.csv

# View latest entries
tail -n 5 data/buoy_46073.csv

# Check for errors in logs
grep -i error data/collector.log
```

## Maintenance

### Updating the Application

```bash
# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Data Backup

```bash
# Create backup of data directory
tar -czf noaa-data-backup-$(date +%Y%m%d).tar.gz data/

# Or use rsync for incremental backups
rsync -av data/ /path/to/backup/location/
```

### Log Rotation

Logs are automatically rotated by Docker (max 10MB, 3 files). Application logs in `data/collector.log` should be manually rotated if they grow too large.

## Technical Details

### Python Dependencies

- **requests**: HTTP library for API calls
- **pandas**: Data manipulation and CSV handling
- **tzdata**: Timezone database for America/Anchorage

### Docker Configuration

- **Base Image**: python:3.11-slim
- **Network**: Bridge network for isolation
- **Volumes**: `./data` mounted to `/app/data`
- **Restart Policy**: unless-stopped

### API Rate Limits

- **NDBC**: No explicit rate limits, but recommended to access no more than once per hour
- **CO-OPS**: No explicit rate limits for reasonable use

## References

- [NOAA NDBC Website](https://www.ndbc.noaa.gov/)
- [NOAA CO-OPS Website](https://tidesandcurrents.noaa.gov/)
- [NDBC Web Data Guide](https://www.ndbc.noaa.gov/docs/ndbc_web_data_guide.pdf)
- [CO-OPS API Documentation](https://api.tidesandcurrents.noaa.gov/api/prod/)
- [NOAA-EDAB/buoydata GitHub](https://github.com/NOAA-EDAB/buoydata)

## License

This project collects publicly available data from NOAA. Please refer to NOAA's data usage policies:
- [NOAA Data Access Policy](https://www.noaa.gov/information-technology/open-data-dissemination)

## Contact

For issues or questions about this application, please check the logs and documentation first. For NOAA data issues, contact:
- NDBC: https://www.ndbc.noaa.gov/
- CO-OPS: co-ops.userservices@noaa.gov

## Legal Disclaimer

This is an independent data collection tool and is not an official NOAA product. All data is sourced from publicly available NOAA APIs. Users assume responsibility for the use of this software and collected data.
