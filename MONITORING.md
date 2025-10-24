# Station Health Monitoring

The NOAA Data Collector includes a comprehensive monitoring system that tracks station availability, outages, and data quality **without generating fake data**.

## Features

### ✅ What It Does

- **Tracks Every Collection Attempt**: Success or failure
- **Records Outages**: When stations go offline and when they recover
- **Calculates Uptime**: Percentage of successful collections
- **Generates Reports**: Human-readable status summaries
- **Alerts on Issues**: Warns about offline or stale stations
- **Historical Data**: Keeps outage history for analysis

### ❌ What It Doesn't Do

- **No Fake Data**: Never generates or interpolates missing data
- **No Giving Up**: Continues trying even after long outages
- **No False Positives**: Distinguishes between station issues and network issues

## Station States

### 🟢 ONLINE
Station is responding normally and providing data.

### 🔴 OFFLINE
Station is currently not responding. The system:
- Tracks how long the outage has lasted
- Records the error message
- Continues attempting collection
- Will automatically detect when station recovers

### 🟡 STALE DATA
Station hasn't provided new data in over 2 hours, but was working recently.

### ⚪ UNKNOWN
Insufficient data to determine status (usually on first startup).

## Viewing Station Status

### Quick Status Check

```bash
cd /opt/dockers/noaa-data-collector
./view_status.sh
```

### View Raw Health Data

```bash
# JSON format with detailed statistics
cat /opt/dockers/noaa-data-collector/data/station_health.json
```

### View in Logs

Station alerts are automatically logged during each collection cycle:

```bash
cd /opt/dockers
sudo docker compose logs noaa-collector | grep "ALERT"
```

## Status Report Format

The status report includes for each station:

```
Station: 46073 (BUOY)
----------------------------------------------------------------------
Status: ✓ ONLINE
Message: Station operating normally

Uptime: 98.5%
Total Attempts: 200
Successful: 197
Failed: 3
Last Success: 2025-10-24 14:30:00 AKDT
Last Record Count: 6,452
Historical Outages: 2 (45 total minutes)
Recent Outages:
  - 2025-10-23 08:15 (15 min)
  - 2025-10-22 14:30 (30 min)
```

## Understanding Outages

### Short Outages (< 1 hour)
Common causes:
- Temporary network issues
- Station maintenance
- Brief sensor resets

**Action**: Monitor, usually resolves automatically.

### Medium Outages (1-24 hours)
Possible causes:
- Weather-related power issues
- Equipment malfunction
- Data transmission problems

**Action**: Check NOAA's station status page, continue monitoring.

### Long Outages (> 24 hours)
Likely causes:
- Major equipment failure
- Severe weather damage
- Scheduled maintenance

**Action**: Check NOAA announcements. Station will auto-recover when back online.

## Monitoring Files

All monitoring data is stored in `/opt/dockers/noaa-data-collector/data/`:

### station_health.json
Complete health tracking data in JSON format:
```json
{
  "stations": {
    "46073": {
      "type": "buoy",
      "total_attempts": 100,
      "successful_attempts": 98,
      "failed_attempts": 2,
      "last_success": "2025-10-24T14:30:00-08:00",
      "current_outage_start": null,
      "outage_history": [...]
    }
  }
}
```

### station_report.txt
Human-readable status report, regenerated after each collection cycle.

### collector.log
Detailed logs including all collection attempts and errors.

## Automated Alerts

The system automatically logs warnings when:

1. **Station Goes Offline**
   ```
   WARNING - STATION ALERTS:
   WARNING -   ⚠ 46073: OFFLINE for 45 minutes
   ```

2. **Data Becomes Stale**
   ```
   WARNING -   ⚠ 9464212: No recent data
   ```

## Integration with Dozzle

View real-time monitoring in your Dozzle interface (http://localhost:8888):

1. Select the `noaa-data-collector` container
2. Filter for "ALERT" to see only warnings
3. Filter for "OFFLINE" to track outages

## Uptime Calculation

Uptime percentage is calculated as:

```
Uptime = (Successful Attempts / Total Attempts) × 100
```

Example:
- 197 successful out of 200 attempts = 98.5% uptime

## Historical Outage Tracking

The system maintains a complete history of outages:

- **Start Time**: When station first failed
- **End Time**: When station recovered
- **Duration**: Length of outage in minutes
- **Recent Outages**: Last 3 outages displayed in report

This helps identify:
- Patterns in station reliability
- Typical outage durations
- Best/worst performing stations

## Troubleshooting

### "No station report available yet"

**Cause**: First collection cycle hasn't completed.

**Solution**: Wait for first cycle (up to 1 hour), then check again.

### All stations showing OFFLINE

**Cause**: Likely network connectivity issue.

**Solution**: 
1. Check internet connection
2. Verify NOAA services are accessible
3. Check collector logs for specific errors

### Station stuck in OFFLINE state

**Cause**: Station may be genuinely offline.

**Solution**:
1. Check NOAA's official station status
2. Review outage duration in report
3. System will auto-recover when station returns

## Best Practices

### Regular Monitoring

Check status report daily or weekly:
```bash
./view_status.sh
```

### Watch for Patterns

- Multiple short outages may indicate intermittent issues
- Long outages may require checking NOAA announcements
- Low uptime (<90%) may indicate station problems

### Don't Panic on Failures

- Stations do go offline temporarily
- System continues trying automatically
- Data collection resumes when station recovers
- No manual intervention needed

### Review Logs for Details

If concerned about a station:
```bash
cd /opt/dockers
sudo docker compose logs noaa-collector | grep "46073"
```

## API Considerations

### NDBC Buoys
- Real-time data updated hourly
- Stations can be offline for maintenance
- Weather events can cause temporary outages

### CO-OPS Tide Stations
- Data updated every 6 minutes
- May have gaps during maintenance
- "No data found" errors are normal during some periods

## Future Enhancements

Potential additions to monitoring:
- Email/SMS alerts for extended outages
- Web dashboard for status visualization
- Trend analysis and predictions
- Integration with NOAA status APIs

## Summary

The monitoring system provides:
- ✅ Real-time station health tracking
- ✅ Automatic outage detection and recovery
- ✅ Historical performance data
- ✅ No fake data generation
- ✅ Continuous retry on failures
- ✅ Detailed logging and reporting

The collector will **never give up** on a station and will automatically resume data collection when stations come back online.
