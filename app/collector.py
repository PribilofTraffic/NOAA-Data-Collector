#!/usr/bin/env python3
"""
NOAA Data Collector

Collects data from NDBC buoy stations and CO-OPS tide stations.
Stores data in CSV format with timestamps in America/Anchorage timezone.
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import pandas as pd
from zoneinfo import ZoneInfo

from monitor import StationMonitor


# Configuration
TIMEZONE = ZoneInfo("America/Anchorage")
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
COLLECTION_INTERVAL = int(os.getenv("COLLECTION_INTERVAL", "3600"))  # seconds

# NDBC Buoy Stations
BUOY_STATIONS = ["46073", "46035"]

# CO-OPS Tide Station
TIDE_STATION = "9464212"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(DATA_DIR, 'collector.log'))
    ]
)
logger = logging.getLogger(__name__)


class NDCBCollector:
    """Collector for NDBC buoy data."""
    
    BASE_URL = "https://www.ndbc.noaa.gov/data/realtime2"
    
    def __init__(self, station_id: str):
        """
        Initialize NDBC collector.
        
        Args:
            station_id: NDBC station identifier (e.g., '46073')
        """
        self.station_id = station_id
        self.data_file = os.path.join(DATA_DIR, f"buoy_{station_id}.csv")
        
    def fetch_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch real-time data from NDBC station.
        
        Returns:
            DataFrame with buoy data or None if fetch fails
        """
        url = f"{self.BASE_URL}/{self.station_id}.txt"
        
        try:
            logger.info(f"Fetching data from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the text data
            lines = response.text.strip().split('\n')
            
            if len(lines) < 3:
                logger.error(f"Insufficient data from station {self.station_id}")
                return None
            
            # First line is header, second is units, data starts at third line
            headers = lines[0].split()
            units = lines[1].split()
            
            # Parse data lines
            data_rows = []
            for line in lines[2:]:
                if line.strip():
                    data_rows.append(line.split())
            
            if not data_rows:
                logger.warning(f"No data rows found for station {self.station_id}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Convert timestamp columns to datetime
            if all(col in df.columns for col in ['#YY', 'MM', 'DD', 'hh', 'mm']):
                df['timestamp'] = pd.to_datetime(
                    df['#YY'] + '-' + df['MM'] + '-' + df['DD'] + ' ' + 
                    df['hh'] + ':' + df['mm'],
                    format='%Y-%m-%d %H:%M',
                    utc=True
                )
                # Convert to Alaska timezone
                df['timestamp'] = df['timestamp'].dt.tz_convert(TIMEZONE)
                df['timestamp_local'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            
            # Add collection timestamp
            df['collected_at'] = datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')
            df['station_id'] = self.station_id
            
            logger.info(f"Successfully fetched {len(df)} records from station {self.station_id}")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data from station {self.station_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing data from station {self.station_id}: {e}")
            return None
    
    def save_data(self, df: pd.DataFrame) -> None:
        """
        Save data to CSV file.
        
        Args:
            df: DataFrame to save
        """
        try:
            # Check if file exists
            file_exists = os.path.isfile(self.data_file)
            
            # Append to existing file or create new one
            df.to_csv(
                self.data_file,
                mode='a' if file_exists else 'w',
                header=not file_exists,
                index=False
            )
            logger.info(f"Saved {len(df)} records to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Error saving data to {self.data_file}: {e}")
    
    def save_failed_attempt(self) -> None:
        """
        Record a failed collection attempt with timestamp to maintain timeline.
        Writes a row with collection timestamp and NULL/FAILED markers.
        """
        try:
            now = datetime.now(TIMEZONE)
            
            # Create a single row with timestamp and failure markers
            failed_row = {
                '#YY': [now.year],
                'MM': [now.month],
                'DD': [now.day],
                'hh': [now.hour],
                'mm': [now.minute],
                'WDIR': ['FAILED'],
                'WSPD': ['FAILED'],
                'GST': ['FAILED'],
                'WVHT': ['FAILED'],
                'DPD': ['FAILED'],
                'APD': ['FAILED'],
                'MWD': ['FAILED'],
                'PRES': ['FAILED'],
                'ATMP': ['FAILED'],
                'WTMP': ['FAILED'],
                'DEWP': ['FAILED'],
                'VIS': ['FAILED'],
                'PTDY': ['FAILED'],
                'TIDE': ['FAILED'],
                'timestamp': [now.isoformat()],
                'timestamp_local': [now.strftime('%Y-%m-%d %H:%M:%S %Z')],
                'collected_at': [now.strftime('%Y-%m-%d %H:%M:%S %Z')],
                'station_id': [self.station_id]
            }
            
            df = pd.DataFrame(failed_row)
            
            # Check if file exists
            file_exists = os.path.isfile(self.data_file)
            
            # Append to existing file or create new one
            df.to_csv(
                self.data_file,
                mode='a' if file_exists else 'w',
                header=not file_exists,
                index=False
            )
            logger.info(f"Recorded failed attempt for station {self.station_id}")
            
        except Exception as e:
            logger.error(f"Error recording failed attempt to {self.data_file}: {e}")


class TideCollector:
    """Collector for CO-OPS tide station data."""
    
    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    def __init__(self, station_id: str):
        """
        Initialize tide collector.
        
        Args:
            station_id: CO-OPS station identifier (e.g., '9464212')
        """
        self.station_id = station_id
        self.data_file = os.path.join(DATA_DIR, f"tide_{station_id}.csv")
    
    def fetch_data(self, hours_back: int = 1) -> Optional[pd.DataFrame]:
        """
        Fetch tide data from CO-OPS API.
        
        Args:
            hours_back: Number of hours of historical data to fetch
            
        Returns:
            DataFrame with tide data or None if fetch fails
        """
        end_date = datetime.now(TIMEZONE)
        begin_date = end_date - timedelta(hours=hours_back)
        
        params = {
            'begin_date': begin_date.strftime('%Y%m%d %H:%M'),
            'end_date': end_date.strftime('%Y%m%d %H:%M'),
            'station': self.station_id,
            'product': 'water_level',
            'datum': 'MLLW',
            'time_zone': 'lst_ldt',  # Local standard/daylight time
            'units': 'english',
            'format': 'json',
            'application': 'NOAA_Data_Collector'
        }
        
        try:
            logger.info(f"Fetching tide data from station {self.station_id}")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"API error for station {self.station_id}: {data['error']}")
                return None
            
            if 'data' not in data or not data['data']:
                logger.warning(f"No data returned for station {self.station_id}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(data['data'])
            
            # Parse timestamp
            if 't' in df.columns:
                df['timestamp'] = pd.to_datetime(df['t'])
                df['timestamp_local'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add collection timestamp
            df['collected_at'] = datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')
            df['station_id'] = self.station_id
            
            logger.info(f"Successfully fetched {len(df)} records from tide station {self.station_id}")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching tide data from station {self.station_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing tide data from station {self.station_id}: {e}")
            return None
    
    def save_data(self, df: pd.DataFrame) -> None:
        """
        Save data to CSV file.
        
        Args:
            df: DataFrame to save
        """
        try:
            # Check if file exists
            file_exists = os.path.isfile(self.data_file)
            
            # Append to existing file or create new one
            df.to_csv(
                self.data_file,
                mode='a' if file_exists else 'w',
                header=not file_exists,
                index=False
            )
            logger.info(f"Saved {len(df)} records to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Error saving tide data to {self.data_file}: {e}")
    
    def save_failed_attempt(self) -> None:
        """
        Record a failed collection attempt with timestamp to maintain timeline.
        Writes a row with collection timestamp and FAILED markers.
        """
        try:
            now = datetime.now(TIMEZONE)
            
            # Create a single row with timestamp and failure markers
            failed_row = {
                't': [now.strftime('%Y-%m-%d %H:%M')],
                'v': ['FAILED'],
                's': ['FAILED'],
                'f': ['FAILED'],
                'q': ['FAILED'],
                'timestamp': [now.isoformat()],
                'timestamp_local': [now.strftime('%Y-%m-%d %H:%M:%S')],
                'collected_at': [now.strftime('%Y-%m-%d %H:%M:%S %Z')],
                'station_id': [self.station_id]
            }
            
            df = pd.DataFrame(failed_row)
            
            # Check if file exists
            file_exists = os.path.isfile(self.data_file)
            
            # Append to existing file or create new one
            df.to_csv(
                self.data_file,
                mode='a' if file_exists else 'w',
                header=not file_exists,
                index=False
            )
            logger.info(f"Recorded failed attempt for tide station {self.station_id}")
            
        except Exception as e:
            logger.error(f"Error recording failed tide attempt to {self.data_file}: {e}")


def collect_all_data(monitor: StationMonitor) -> None:
    """
    Collect data from all configured stations.
    
    Args:
        monitor: StationMonitor instance for tracking health
    """
    logger.info("=" * 60)
    logger.info("Starting data collection cycle")
    logger.info(f"Time: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("=" * 60)
    
    # Collect buoy data
    for station_id in BUOY_STATIONS:
        collector = NDCBCollector(station_id)
        df = collector.fetch_data()
        if df is not None:
            collector.save_data(df)
            monitor.record_attempt(station_id, "buoy", True, len(df))
        else:
            # Record failed attempt with timestamp to maintain timeline
            collector.save_failed_attempt()
            monitor.record_attempt(
                station_id, 
                "buoy", 
                False, 
                error_message="Failed to fetch or parse data"
            )
    
    # Collect tide data
    tide_collector = TideCollector(TIDE_STATION)
    df = tide_collector.fetch_data()
    if df is not None:
        tide_collector.save_data(df)
        monitor.record_attempt(TIDE_STATION, "tide", True, len(df))
    else:
        # Record failed attempt with timestamp to maintain timeline
        tide_collector.save_failed_attempt()
        monitor.record_attempt(
            TIDE_STATION, 
            "tide", 
            False, 
            error_message="Failed to fetch tide data"
        )
    
    logger.info("Data collection cycle completed")
    
    # Show alerts if any
    alerts = monitor.get_alert_summary()
    if alerts:
        logger.warning("STATION ALERTS:")
        for alert in alerts:
            logger.warning(f"  {alert}")
    
    # Generate status report
    monitor.save_report()
    
    logger.info("=" * 60)


def main() -> None:
    """Main execution loop."""
    logger.info("NOAA Data Collector starting...")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info(f"Collection interval: {COLLECTION_INTERVAL} seconds")
    logger.info(f"Timezone: {TIMEZONE}")
    logger.info(f"Buoy stations: {', '.join(BUOY_STATIONS)}")
    logger.info(f"Tide station: {TIDE_STATION}")
    
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize station monitor
    monitor = StationMonitor()
    logger.info("Station health monitoring enabled")
    
    # Run collection loop
    while True:
        try:
            collect_all_data(monitor)
            logger.info(f"Sleeping for {COLLECTION_INTERVAL} seconds...")
            time.sleep(COLLECTION_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, exiting...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)


if __name__ == "__main__":
    main()
