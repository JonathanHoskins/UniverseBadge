# Hamilton County 911 Incidents App

Displays real-time active incident data from Hamilton County, Tennessee's 911 Emergency Communications District.

## Features

- **Active Incident Count** - Shows current number of active 911 incidents
- **Daily Total** - Total incidents handled today
- **Yearly Total** - Total incidents this year
- **Auto-refresh** - Press A to fetch latest data
- **Last Update Timer** - Shows time since last successful fetch
- **Non-blocking** - Network operations don't freeze the UI
- **Error Handling** - Graceful handling of network errors

## Data Source

Data is fetched from: https://www.hamiltontn911.gov/active-incidents.php

## Requirements

- WiFi connection required
- Create `/secrets.py` with WiFi credentials:
  ```python
  WIFI_SSID = "your-network-name"
  WIFI_PASSWORD = "your-password"
  ```

## Controls

- **A Button** - Fetch/refresh incident data
- Activity indicator blinks while fetching

## Display

```
HC 911 Incidents
─────────────────
Active Now:
42

Today: 888
Year: 361264

Updated 15s ago

Status: Updated

A:Refresh
```

## Technical Details

- Uses HTTP GET request to fetch webpage
- Parses HTML to extract incident counts
- Implements timeout handling (10 second max)
- Limits response size to 50KB to prevent memory issues
- Simple string parsing for robustness

## Error States

- **WiFi not connected** - Enable WiFi in network settings
- **Parse error** - Website format may have changed
- **Timeout** - Network connection issue
- **Connection refused** - Service may be temporarily down
