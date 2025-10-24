# NOAA Data Dictionary

Complete reference for all data fields collected from NDBC buoy stations.

## Data Format

All data is stored in **raw format** exactly as provided by NOAA. No conversions, interpolations, or modifications are made to sensor values.

## NDBC Buoy Data Fields

### Time Fields

| Field | Description | Format | Example |
|-------|-------------|--------|---------|
| `#YY` | Year | 4-digit | 2025 |
| `MM` | Month | 2-digit | 10 |
| `DD` | Day | 2-digit | 24 |
| `hh` | Hour (UTC) | 2-digit | 05 |
| `mm` | Minute | 2-digit | 50 |

### Wind Measurements

| Field | Description | Units | Range | Notes |
|-------|-------------|-------|-------|-------|
| `WDIR` | Wind Direction | degrees | 0-360 | Direction wind is coming FROM (meteorological convention) |
| `WSPD` | Wind Speed | m/s | 0-50+ | Sustained wind speed |
| `GST` | Wind Gust | m/s | 0-70+ | Peak gust speed |

**Wind Direction Reference:**
- 0° / 360° = North
- 90° = East
- 180° = South
- 270° = West

### Wave Measurements

| Field | Description | Units | Range | Notes |
|-------|-------------|-------|-------|-------|
| `WVHT` | Significant Wave Height | meters | 0-20+ | Average height of highest 1/3 of waves |
| `DPD` | Dominant Wave Period | seconds | 1-25 | Period of most energetic waves |
| `APD` | Average Wave Period | seconds | 1-25 | Mean of all wave periods |
| `MWD` | Wave Direction | degrees | 0-360 | Direction waves are coming FROM |

**Wave Height Scale:**
- 0-1m: Calm to slight
- 1-2.5m: Moderate
- 2.5-4m: Rough
- 4-6m: Very rough
- 6-9m: High
- 9-14m: Very high
- 14m+: Phenomenal

### Atmospheric Measurements

| Field | Description | Units | Range | Notes |
|-------|-------------|-------|-------|-------|
| `PRES` | Air Pressure | hPa | 950-1050 | Atmospheric pressure at sea level |
| `ATMP` | Air Temperature | °C | -40 to 40 | Air temperature at sensor height (~3.8m) |
| `DEWP` | Dewpoint Temperature | °C | -50 to 30 | Temperature at which air becomes saturated |

**Pressure Reference:**
- < 980 hPa: Very low (storm)
- 980-1000 hPa: Low
- 1000-1020 hPa: Normal
- 1020-1040 hPa: High
- > 1040 hPa: Very high

### Oceanographic Measurements

| Field | Description | Units | Range | Notes |
|-------|-------------|-------|-------|-------|
| `WTMP` | Water Temperature | °C | -2 to 35 | Sea surface temperature (~1-2m depth) |

**Bering Sea Water Temps:**
- Winter: -1 to 3°C
- Summer: 5 to 12°C
- Freezing point: ~-1.8°C (saltwater)

### Other Measurements

| Field | Description | Units | Range | Notes |
|-------|-------------|-------|-------|-------|
| `VIS` | Visibility | nautical miles | 0-30+ | Horizontal visibility |
| `PTDY` | Pressure Tendency | hPa | -10 to +10 | 3-hour pressure change |
| `TIDE` | Tide | feet | -5 to +5 | Water level relative to datum |

### Metadata Fields (Added by Collector)

| Field | Description | Format | Example |
|-------|-------------|--------|---------|
| `timestamp` | Parsed UTC timestamp | ISO 8601 | 2025-10-23 21:50:00-08:00 |
| `timestamp_local` | Alaska local time | String | 2025-10-23 21:50:00 AKDT |
| `collected_at` | Collection timestamp | String | 2025-10-23 22:18:49 AKDT |
| `station_id` | Station identifier | String | 46073 |

## Missing Data

### `MM` Code
Indicates **Missing Measurement** - sensor did not report data for that specific field.

**Common Reasons:**
- Sensor malfunction or calibration
- Value outside sensor range
- Temporary sensor offline
- Data quality check failed

**Important:** `MM` is NOT zero! It means no valid measurement was available.

### `FAILED` Code
Indicates **Collection Failure** - the entire data collection attempt failed for that timestamp.

**Common Reasons:**
- Station completely offline
- Network connectivity issues
- API unavailable
- Data parsing errors

**Purpose:** Maintains complete timeline even during outages. You'll see a row with:
- Timestamp of collection attempt
- All data fields marked as `FAILED`
- This ensures you can track when collections occurred and identify gaps

**Important:** `FAILED` means the collector tried but couldn't get ANY data from the station at that time. This is different from `MM` which means a specific sensor didn't report within an otherwise successful collection.

## CO-OPS Tide Station Data

### Tide Data Fields

| Field | Description | Units | Notes |
|-------|-------------|-------|-------|
| `t` | Timestamp | ISO 8601 | UTC or local time |
| `v` | Water Level | feet | Relative to MLLW datum |
| `s` | Sigma | feet | Standard deviation of 1-second samples |
| `f` | Flags | string | Quality control flags |
| `q` | Quality | string | Quality assurance level |

**MLLW Datum:** Mean Lower Low Water - average of lower low water heights

**Typical Tide Range (Unalaska):**
- Low: 0-2 feet (MLLW)
- High: 8-12 feet (MLLW)
- Range: ~10 feet

## Unit Conversions

### Wind Speed
- m/s to knots: multiply by 1.944
- m/s to mph: multiply by 2.237
- m/s to km/h: multiply by 3.6

### Wave Height
- meters to feet: multiply by 3.281

### Temperature
- °C to °F: (°C × 9/5) + 32
- °C to K: °C + 273.15

### Pressure
- hPa to inHg: multiply by 0.02953
- hPa to mb: same (1 hPa = 1 mb)

### Distance
- nautical miles to km: multiply by 1.852
- nautical miles to miles: multiply by 1.151

## Data Quality

### NDBC Quality Control
NOAA performs automated quality control:
- Range checks (values within sensor limits)
- Rate-of-change checks (realistic variations)
- Climatology checks (values typical for location/season)
- Spike detection

**Result:** Data in our files has passed NOAA's QC, but may still contain `MM` for missing values.

### Using the Data

**Best Practices:**
1. Filter out `MM` values before analysis
2. Check for data gaps (missing timestamps)
3. Consider sensor height/depth for measurements
4. Account for timezone (UTC in raw data)
5. Validate against expected ranges

**Example Python:**
```python
import pandas as pd

# Read data
df = pd.read_csv('buoy_46073.csv')

# Replace MM with NaN
df = df.replace('MM', pd.NA)

# Convert to numeric
df['WSPD'] = pd.to_numeric(df['WSPD'], errors='coerce')

# Filter valid wind speeds
valid_wind = df[df['WSPD'].notna()]
```

## Station-Specific Information

### Station 46073 (Southeast Bering Sea)
- **Location:** 55.008°N, 172.012°W
- **Water Depth:** 3,471 meters
- **Buoy Type:** 3-meter discus
- **Sensor Heights:**
  - Anemometer: 3.8m above sea level
  - Air temp: 3.4m above sea level
  - Barometer: 2.4m above mean sea level
  - Water temp: 2m below waterline

### Station 46035 (Central Bering Sea)
- **Location:** 57.034°N, 177.468°W
- **Water Depth:** 3,696 meters
- **Buoy Type:** 3-meter foam buoy
- **Sensor Heights:**
  - Anemometer: 4.1m above sea level
  - Air temp: 3.7m above sea level
  - Barometer: 2.7m above mean sea level
  - Water temp: 1.5m below waterline

### Station 9464212 (Unalaska)
- **Location:** Unalaska, AK
- **Type:** Tide gauge
- **Datum:** MLLW (Mean Lower Low Water)
- **Update Frequency:** 6-minute intervals

## References

- [NDBC Measurement Descriptions](https://www.ndbc.noaa.gov/faq/measdes.shtml)
- [NDBC Web Data Guide](https://www.ndbc.noaa.gov/docs/ndbc_web_data_guide.pdf)
- [CO-OPS API Documentation](https://api.tidesandcurrents.noaa.gov/api/prod/)
- [Meteorological Conventions](https://www.ndbc.noaa.gov/faq/measdes.shtml)

## Summary

✅ **All data is RAW** - No conversions or modifications  
✅ **MM = Missing** - Not zero, not estimated  
✅ **NOAA QC Applied** - Data has passed quality checks  
✅ **Standard Units** - Metric (m/s, °C, hPa, meters)  
✅ **Documented** - Full field definitions and ranges  

This data is suitable for scientific analysis, research, and operational use.
