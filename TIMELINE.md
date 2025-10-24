# Timeline Continuity

The NOAA Data Collector maintains a **complete timeline** of all collection attempts, even when stations are offline or data is unavailable.

## How It Works

### Every Collection Attempt is Recorded

**When data is available:**
- Normal data rows with all sensor values
- Timestamps show when data was collected
- Values are raw from NOAA

**When data is NOT available:**
- A row is still written with the collection timestamp
- All data fields are marked as `FAILED`
- This maintains the timeline continuity

## Why This Matters

### Complete Historical Record
You can always see:
- ✅ When collections were attempted
- ✅ When stations were offline
- ✅ Duration of outages
- ✅ No gaps in your timeline

### Easy Gap Analysis
```python
import pandas as pd

# Read data
df = pd.read_csv('buoy_46073.csv')

# Find all failed attempts
failures = df[df['WSPD'] == 'FAILED']

# Count outages
print(f"Total failed collections: {len(failures)}")

# Find gaps in timeline
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
df['time_diff'] = df['timestamp'].diff()

# Gaps > 2 hours (allowing for collection interval)
gaps = df[df['time_diff'] > pd.Timedelta(hours=2)]
print(f"Significant gaps: {len(gaps)}")
```

### Data Integrity
- No ambiguity about missing data
- Clear distinction between:
  - `MM` = Sensor didn't report (partial data)
  - `FAILED` = Entire collection failed (no data)

## Example Data

### Successful Collection
```csv
2025,10,24,14,00,20,6.0,8.0,2.6,9,7.0,358,1006.4,4.9,7.6,-2.2,MM,MM,MM,2025-10-24 14:00:00-08:00,2025-10-24 14:00:00 AKDT,2025-10-24 14:05:00 AKDT,46073
```
- Wind, waves, pressure, temps all present
- Some fields have `MM` (individual sensor issues)

### Failed Collection
```csv
2025,10,24,15,00,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,2025-10-24 15:00:00-08:00,2025-10-24 15:00:00 AKDT,2025-10-24 15:05:00 AKDT,46073
```
- All data fields marked `FAILED`
- Timestamp shows when collection was attempted
- Station was completely offline at this time

### Recovered Collection
```csv
2025,10,24,16,00,10,5.0,7.0,2.8,8,6.5,355,1005.2,5.1,7.8,-1.8,MM,MM,MM,2025-10-24 16:00:00-08:00,2025-10-24 16:00:00 AKDT,2025-10-24 16:05:00 AKDT,46073
```
- Station back online
- Normal data collection resumed

## Timeline Benefits

### 1. Outage Duration Tracking
You can calculate exactly how long stations were offline:
```python
# Find consecutive failures
failures = df[df['WSPD'] == 'FAILED']
if len(failures) > 0:
    outage_start = failures.iloc[0]['timestamp_local']
    outage_end = failures.iloc[-1]['timestamp_local']
    print(f"Outage: {outage_start} to {outage_end}")
```

### 2. Reliability Analysis
Calculate station uptime:
```python
total_attempts = len(df)
failed_attempts = len(df[df['WSPD'] == 'FAILED'])
uptime = ((total_attempts - failed_attempts) / total_attempts) * 100
print(f"Station uptime: {uptime:.1f}%")
```

### 3. Data Quality Assessment
Identify patterns:
- Time of day when failures occur
- Seasonal reliability
- Correlation with weather events

### 4. Scientific Integrity
- No interpolated or estimated values
- Clear markers for missing data
- Complete audit trail of collection attempts

## Filtering Data

### Include Only Valid Data
```python
# Remove failed collections
valid_data = df[df['WSPD'] != 'FAILED']

# Also remove rows with MM for specific field
valid_wind = valid_data[valid_data['WSPD'] != 'MM']
```

### Analyze Failures
```python
# Get only failed collections
failures = df[df['WSPD'] == 'FAILED']

# Group by date to see failure patterns
failures['date'] = pd.to_datetime(failures['timestamp_local']).dt.date
failure_counts = failures.groupby('date').size()
```

### Timeline Completeness Check
```python
# Expected collections per day (hourly = 24)
expected_per_day = 24

# Count actual collections per day
df['date'] = pd.to_datetime(df['timestamp_local']).dt.date
actual_per_day = df.groupby('date').size()

# Find days with missing collections
incomplete_days = actual_per_day[actual_per_day < expected_per_day]
print(f"Days with missing collections: {len(incomplete_days)}")
```

## Storage Impact

### Minimal Overhead
A `FAILED` row is very small:
- ~100 bytes per failed attempt
- 1 hour outage = 1 failed row = ~100 bytes
- 24 hour outage = 24 failed rows = ~2.4 KB
- 1 week outage = 168 failed rows = ~17 KB

**Negligible impact** compared to successful collections (~300 bytes each with full data).

## Data Codes Summary

| Code | Meaning | Scope | Example |
|------|---------|-------|---------|
| `FAILED` | Collection failed | Entire row | Station offline |
| `MM` | Missing measurement | Single field | One sensor malfunction |
| Valid number | Successful reading | Single field | 6.0 m/s wind |

## Best Practices

### 1. Always Check for FAILED
Before analysis, filter out failed collections:
```python
df = df[df['WSPD'] != 'FAILED']
```

### 2. Document Outages
When analyzing data, note significant outages:
```python
# Find outage periods
failures = df[df['WSPD'] == 'FAILED']
if len(failures) > 0:
    print(f"Note: {len(failures)} failed collections during analysis period")
```

### 3. Use Timeline for Context
Failed rows provide context for data gaps:
- Why is there no data for this period?
- Was it a station issue or collector issue?
- How long was the outage?

### 4. Preserve Failed Rows
Don't delete `FAILED` rows from your archive:
- They're part of the historical record
- Useful for reliability analysis
- Minimal storage cost

## Comparison with Other Approaches

### ❌ Without Timeline Tracking
```csv
2025,10,24,14,00,20,6.0,8.0,2.6,9,7.0,358,1006.4,4.9,7.6,-2.2,MM,MM,MM
[GAP - no record of what happened]
2025,10,24,16,00,10,5.0,7.0,2.8,8,6.5,355,1005.2,5.1,7.8,-1.8,MM,MM,MM
```
**Problems:**
- Can't tell if collector ran or not
- Can't measure outage duration
- Ambiguous gaps in data

### ✅ With Timeline Tracking
```csv
2025,10,24,14,00,20,6.0,8.0,2.6,9,7.0,358,1006.4,4.9,7.6,-2.2,MM,MM,MM
2025,10,24,15,00,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED,FAILED
2025,10,24,16,00,10,5.0,7.0,2.8,8,6.5,355,1005.2,5.1,7.8,-1.8,MM,MM,MM
```
**Benefits:**
- Clear record of collection attempt
- Known outage duration (1 hour)
- Complete timeline maintained

## Summary

✅ **Every collection attempt is recorded**  
✅ **Failed attempts marked with `FAILED`**  
✅ **Complete timeline maintained**  
✅ **Easy to filter for analysis**  
✅ **Minimal storage overhead**  
✅ **Scientific integrity preserved**  

Your data will always have a complete timeline, making it easy to:
- Track station reliability
- Identify outage patterns
- Maintain data integrity
- Perform accurate historical analysis

**No gaps, no guessing, complete transparency.**
