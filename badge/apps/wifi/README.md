# WiFi Connection Test App

A simple diagnostic app to test WiFi connectivity on the badge.

## Features

- Toggle WiFi ON/OFF with the A button
- Shows connection status in real-time
- Displays IP address when connected
- **Find Roku devices on network with B button**
- Scrolling log of connection events
- Heartbeat indicator to show the app is responsive

## Setup

1. Create `/secrets.py` on your badge with WiFi credentials:
   ```python
   WIFI_SSID = "your-network-name"
   WIFI_PASSWORD = "your-password"
   ```

2. Launch the `wifi` app from the menu

## Usage

- **A button**: Toggle WiFi ON/OFF
- **B button**: Scan for Roku devices (only works when connected to WiFi)
- The status indicator (top-right) shows:
  - **GREEN "ON"**: WiFi is enabled and attempting to connect
  - **RED "OFF"**: WiFi is disabled
- The log shows connection progress:
  - Network module loading
  - SSID being used
  - Connection status
  - IP address once connected
  - Roku discovery results

## Troubleshooting

If you see:
- **"Secrets error"** → Create `/secrets.py` with your WiFi credentials
- **"Network module loaded"** but no connection → Check your SSID/password
- **Status numbers** (e.g., "Status: 1") → Check MicroPython docs for WLAN status codes
- **Heartbeat dot not blinking** → App may be frozen; press HOME to exit

## Status Codes

Common WLAN status codes:
- `0` = IDLE
- `1` = CONNECTING
- `3` = CONNECTED
- `-1`, `-2`, `-3` = Various error states (wrong password, no AP, etc.)
