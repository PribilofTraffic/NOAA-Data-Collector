#!/usr/bin/env python3
"""
NOAA Station Health Monitor

Monitors station availability, data quality, and generates status reports.
Tracks outages and recovery without generating fake data.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd


TIMEZONE = ZoneInfo("America/Anchorage")
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
MONITOR_FILE = os.path.join(DATA_DIR, "station_health.json")
REPORT_FILE = os.path.join(DATA_DIR, "station_report.txt")


class StationMonitor:
    """Monitor station health and availability."""
    
    def __init__(self):
        """Initialize the monitor."""
        self.health_data = self._load_health_data()
        
    def _load_health_data(self) -> Dict:
        """Load existing health data or create new."""
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "stations": {},
            "last_updated": None
        }
    
    def _save_health_data(self) -> None:
        """Save health data to file."""
        try:
            with open(MONITOR_FILE, 'w') as f:
                json.dump(self.health_data, f, indent=2)
        except Exception as e:
            print(f"Error saving health data: {e}")
    
    def record_attempt(
        self,
        station_id: str,
        station_type: str,
        success: bool,
        record_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Record a data collection attempt.
        
        Args:
            station_id: Station identifier
            station_type: Type of station (buoy, tide)
            success: Whether collection succeeded
            record_count: Number of records collected
            error_message: Error message if failed
        """
        now = datetime.now(TIMEZONE).isoformat()
        
        if station_id not in self.health_data["stations"]:
            self.health_data["stations"][station_id] = {
                "type": station_type,
                "first_seen": now,
                "total_attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "last_success": None,
                "last_failure": None,
                "current_outage_start": None,
                "outage_history": [],
                "last_record_count": None,
                "total_records_collected": 0
            }
        
        station = self.health_data["stations"][station_id]
        station["total_attempts"] += 1
        station["last_attempt"] = now
        
        if success:
            station["successful_attempts"] += 1
            station["last_success"] = now
            station["last_record_count"] = record_count
            if record_count:
                station["total_records_collected"] += record_count
            
            # If recovering from outage, record it
            if station["current_outage_start"]:
                outage_duration = self._calculate_duration(
                    station["current_outage_start"],
                    now
                )
                station["outage_history"].append({
                    "start": station["current_outage_start"],
                    "end": now,
                    "duration_minutes": outage_duration
                })
                station["current_outage_start"] = None
        else:
            station["failed_attempts"] += 1
            station["last_failure"] = now
            station["last_error"] = error_message
            
            # Mark start of outage if this is first failure
            if not station["current_outage_start"]:
                station["current_outage_start"] = now
        
        self.health_data["last_updated"] = now
        self._save_health_data()
    
    def _calculate_duration(self, start_iso: str, end_iso: str) -> int:
        """Calculate duration in minutes between two ISO timestamps."""
        try:
            start = datetime.fromisoformat(start_iso)
            end = datetime.fromisoformat(end_iso)
            return int((end - start).total_seconds() / 60)
        except Exception:
            return 0
    
    def get_station_status(self, station_id: str) -> Dict:
        """
        Get current status of a station.
        
        Args:
            station_id: Station identifier
            
        Returns:
            Dictionary with status information
        """
        if station_id not in self.health_data["stations"]:
            return {
                "status": "unknown",
                "message": "No data collection attempts recorded"
            }
        
        station = self.health_data["stations"][station_id]
        
        # Check if currently in outage
        if station["current_outage_start"]:
            outage_duration = self._calculate_duration(
                station["current_outage_start"],
                datetime.now(TIMEZONE).isoformat()
            )
            return {
                "status": "offline",
                "message": f"Station offline for {outage_duration} minutes",
                "outage_start": station["current_outage_start"],
                "last_error": station.get("last_error", "Unknown error")
            }
        
        # Check last success time
        if station["last_success"]:
            last_success = datetime.fromisoformat(station["last_success"])
            time_since = datetime.now(TIMEZONE) - last_success
            
            if time_since < timedelta(hours=2):
                return {
                    "status": "online",
                    "message": "Station operating normally",
                    "last_success": station["last_success"],
                    "last_record_count": station.get("last_record_count")
                }
            else:
                return {
                    "status": "stale",
                    "message": f"No data for {int(time_since.total_seconds() / 3600)} hours",
                    "last_success": station["last_success"]
                }
        
        return {
            "status": "unknown",
            "message": "No successful collections yet"
        }
    
    def get_uptime_percentage(self, station_id: str) -> float:
        """Calculate uptime percentage for a station."""
        if station_id not in self.health_data["stations"]:
            return 0.0
        
        station = self.health_data["stations"][station_id]
        total = station["total_attempts"]
        
        if total == 0:
            return 0.0
        
        return (station["successful_attempts"] / total) * 100
    
    def generate_report(self) -> str:
        """
        Generate a human-readable status report.
        
        Returns:
            Formatted status report string
        """
        now = datetime.now(TIMEZONE)
        lines = []
        
        lines.append("=" * 70)
        lines.append("NOAA STATION HEALTH REPORT")
        lines.append(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        lines.append("=" * 70)
        lines.append("")
        
        if not self.health_data["stations"]:
            lines.append("No station data available yet.")
            return "\n".join(lines)
        
        for station_id, station in sorted(self.health_data["stations"].items()):
            status = self.get_station_status(station_id)
            uptime = self.get_uptime_percentage(station_id)
            
            lines.append(f"Station: {station_id} ({station['type'].upper()})")
            lines.append("-" * 70)
            
            # Status indicator
            status_icon = {
                "online": "✓ ONLINE",
                "offline": "✗ OFFLINE",
                "stale": "⚠ STALE DATA",
                "unknown": "? UNKNOWN"
            }.get(status["status"], "? UNKNOWN")
            
            lines.append(f"Status: {status_icon}")
            lines.append(f"Message: {status['message']}")
            lines.append("")
            
            # Statistics
            lines.append(f"Uptime: {uptime:.1f}%")
            lines.append(f"Total Attempts: {station['total_attempts']}")
            lines.append(f"Successful: {station['successful_attempts']}")
            lines.append(f"Failed: {station['failed_attempts']}")
            
            if station.get('last_success'):
                last_success = datetime.fromisoformat(station['last_success'])
                lines.append(f"Last Success: {last_success.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                if station.get('last_record_count'):
                    lines.append(f"Last Record Count: {station['last_record_count']:,}")
            
            if station.get('last_failure'):
                last_failure = datetime.fromisoformat(station['last_failure'])
                lines.append(f"Last Failure: {last_failure.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                if station.get('last_error'):
                    lines.append(f"Last Error: {station['last_error']}")
            
            # Outage information
            if station['current_outage_start']:
                outage_start = datetime.fromisoformat(station['current_outage_start'])
                duration = (now - outage_start).total_seconds() / 60
                lines.append(f"⚠ Current Outage: {duration:.0f} minutes")
            
            if station['outage_history']:
                total_outages = len(station['outage_history'])
                total_outage_time = sum(o['duration_minutes'] for o in station['outage_history'])
                lines.append(f"Historical Outages: {total_outages} ({total_outage_time:.0f} total minutes)")
                
                # Show recent outages
                recent = station['outage_history'][-3:]
                if recent:
                    lines.append("Recent Outages:")
                    for outage in recent:
                        start = datetime.fromisoformat(outage['start'])
                        lines.append(f"  - {start.strftime('%Y-%m-%d %H:%M')} ({outage['duration_minutes']:.0f} min)")
            
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("LEGEND:")
        lines.append("✓ ONLINE    - Station responding normally")
        lines.append("✗ OFFLINE   - Station currently not responding")
        lines.append("⚠ STALE     - No recent data (>2 hours)")
        lines.append("? UNKNOWN   - Insufficient data to determine status")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_report(self) -> None:
        """Generate and save report to file."""
        report = self.generate_report()
        try:
            with open(REPORT_FILE, 'w') as f:
                f.write(report)
        except Exception as e:
            print(f"Error saving report: {e}")
    
    def get_alert_summary(self) -> List[str]:
        """
        Get list of current alerts/issues.
        
        Returns:
            List of alert messages
        """
        alerts = []
        
        for station_id, station in self.health_data["stations"].items():
            status = self.get_station_status(station_id)
            
            if status["status"] == "offline":
                outage_duration = self._calculate_duration(
                    station["current_outage_start"],
                    datetime.now(TIMEZONE).isoformat()
                )
                alerts.append(
                    f"⚠ {station_id}: OFFLINE for {outage_duration} minutes"
                )
            elif status["status"] == "stale":
                alerts.append(f"⚠ {station_id}: No recent data")
        
        return alerts


def main():
    """Generate and display current status report."""
    monitor = StationMonitor()
    report = monitor.generate_report()
    print(report)
    monitor.save_report()


if __name__ == "__main__":
    main()
