"""
WiFi Connection Test App.

Displays current WiFi connection state and a scrollable set of network stats.
Button mapping:
- A: Toggle WiFi on/off
- C: Switch between status log and stats view (when connected)
- UP/DOWN: Scroll in stats view
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from badgeware import screen, PixelFont, shapes, brushes, io

# UI state
font = None
status_lines = []
wifi_enabled = False
wlan = None
connect_attempted = False
last_update = 0
view_mode = "status"  # "status" or "stats"
stats_scroll = 0
max_stats_scroll = 0
connection_start_time = 0

# Colors
BG = (13, 17, 23)
TEXT = (201, 209, 217)
SUCCESS = (46, 160, 67)
ERROR = (248, 81, 73)
WARNING = (255, 191, 0)
DIM = (88, 96, 105)
ITEMS_PER_PAGE = 4  # number of stats entries visible per screen


def get_network_stats() -> List[Tuple[str, str, Optional[Tuple[int, int, int]]]]:
    """Collect network statistics for the current connection.

    Returns a list of tuples: (label, value, color_override).
    color_override is optional; if present, it overrides the default text color.
    """
    if not wlan or not wlan.isconnected():
        return []
    
    stats = []
    try:
        config = wlan.ifconfig()
        stats.append(("IP Address", config[0], None))
        stats.append(("Subnet Mask", config[1], None))
        stats.append(("Gateway", config[2], None))
        stats.append(("DNS Server", config[3], None))
    except Exception:
        pass
    
    try:
        mac = wlan.config("mac")
        mac_str = ":".join([f"{b:02x}" for b in mac])
        stats.append(("MAC Address", mac_str, None))
    except Exception:
        pass
    
    try:
        rssi = wlan.status("rssi")
        # Color code: red if signal is weak (below -70 dBm)
        signal_color = ERROR if rssi < -70 else None
        stats.append(("Signal (RSSI)", f"{rssi} dBm", signal_color))
    except Exception:
        pass
    
    try:
        ssid = wlan.config("ssid")
        stats.append(("SSID", ssid[:20], None))
    except Exception:
        pass
    
    try:
        channel = wlan.config("channel")
        stats.append(("Channel", str(channel), None))
    except Exception:
        pass
    
    if connection_start_time > 0:
        uptime = (io.ticks - connection_start_time) // 1000
        mins = uptime // 60
        secs = uptime % 60
        stats.append(("Uptime", f"{mins}m {secs}s", None))
    
    return stats


def add_status(text: str) -> None:
    """Append a status line to the log (keeps the last 8 lines)."""
    global status_lines
    status_lines.append(text)
    if len(status_lines) > 8:
        status_lines = status_lines[-8:]


def _ensure_font() -> None:
    global font
    if font is None:
        try:
            font = PixelFont.load("/system/assets/fonts/ark.ppf")
            add_status("App started")
        except Exception as e:
            add_status(f"Font error: {str(e)[:20]}")

def _handle_input() -> None:
    global view_mode, stats_scroll, wifi_enabled, connect_attempted, wlan, connection_start_time
    # Toggle view mode
    if io.BUTTON_C in io.pressed:
        if wlan and wlan.isconnected():
            view_mode = "stats" if view_mode == "status" else "status"
            stats_scroll = 0
        else:
            add_status("Connect WiFi first!")
    # Scroll in stats view
    if view_mode == "stats":
        if io.BUTTON_UP in io.pressed:
            stats_scroll = max(0, stats_scroll - 1)
        if io.BUTTON_DOWN in io.pressed:
            stats_scroll = min(max_stats_scroll, stats_scroll + 1)
    # Toggle WiFi
    if io.BUTTON_A in io.pressed:
        wifi_enabled = not wifi_enabled
        if wifi_enabled:
            add_status("WiFi enabled - connecting...")
            connect_attempted = False
        else:
            add_status("WiFi disabled")
            if wlan:
                try:
                    wlan.active(False)
                except Exception:
                    pass
            wlan = None
            connect_attempted = False
            connection_start_time = 0
            view_mode = "status"

def _handle_wifi_connect() -> None:
    global wifi_enabled, connect_attempted, wlan
    if wifi_enabled and not connect_attempted:
        try:
            import network
            add_status("Network module loaded")
            try:
                import sys
                sys.path.insert(0, "/")
                from secrets import WIFI_SSID, WIFI_PASSWORD  # type: ignore[attr-defined]
                sys.path.pop(0)
                add_status(f"SSID: {WIFI_SSID[:15]}")
            except Exception as e:
                add_status(f"Secrets error: {str(e)[:20]}")
                add_status("Create /secrets.py")
                wifi_enabled = False
                connect_attempted = True
            if wifi_enabled:
                wlan = network.WLAN(network.STA_IF)
                wlan.active(True)
                add_status("WLAN activated")
                wlan.connect(WIFI_SSID, WIFI_PASSWORD)
                add_status("Connecting...")
                connect_attempted = True
        except Exception as e:
            add_status(f"Error: {str(e)[:30]}")
            wifi_enabled = False
            connect_attempted = True

def _check_connection_status() -> None:
    global last_update, connection_start_time
    if wifi_enabled and connect_attempted and wlan:
        if io.ticks - last_update > 1000:
            last_update = io.ticks
            try:
                if wlan.isconnected():
                    if connection_start_time == 0:
                        connection_start_time = io.ticks
                        add_status("Connected!")
                    config = wlan.ifconfig()
                    if view_mode == "status":
                        add_status(f"IP: {config[0]}")
                else:
                    connection_start_time = 0
                    status = wlan.status()
                    add_status(f"Status: {status}")
            except Exception as e:
                add_status(f"Check error: {str(e)[:20]}")

def draw_status_view() -> None:
    """Draw the status log view with title, ON/OFF, and recent messages."""
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text("WiFi Test", 5, 3)
        status_text = "ON" if wifi_enabled else "OFF"
        color = SUCCESS if wifi_enabled else ERROR
        screen.brush = brushes.color(*color)
        screen.text(status_text, 135, 3)
    if font:
        screen.brush = brushes.color(*TEXT)
        y = 20
        for line in status_lines:
            if y < 105:
                screen.text(line[:26], 5, y)
                y += 10
    if font:
        screen.brush = brushes.color(*WARNING)
        if wlan and wlan.isconnected():
            screen.text("A:WiFi C:Stats", 5, 108)
        else:
            screen.text("A:Toggle WiFi", 5, 108)
    try:
        color = SUCCESS if (io.ticks // 250) % 2 == 0 else BG
        screen.brush = brushes.color(*color)
        screen.draw(shapes.circle(4, 4, 2))
    except Exception:
        pass

def draw_stats_view() -> None:
    """Draw the network statistics view with paging/scroll support."""
    global max_stats_scroll
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text("Network Stats", 5, 3)
        color = SUCCESS if wifi_enabled else ERROR
        screen.brush = brushes.color(*color)
        screen.text("ON", 135, 3)
    stats = get_network_stats()
    max_stats_scroll = max(0, len(stats) - ITEMS_PER_PAGE)
    if font and stats:
        y = 20
        visible_stats = stats[stats_scroll:stats_scroll + ITEMS_PER_PAGE]
        for item in visible_stats:
            if len(item) == 3:
                label, value, color_override = item
            else:
                label, value = item
                color_override = None
            screen.brush = brushes.color(*DIM)
            screen.text(f"{label}:", 5, y)
            if color_override:
                screen.brush = brushes.color(*color_override)
            else:
                screen.brush = brushes.color(*TEXT)
            screen.text(str(value)[:20], 5, y + 10)
            y += 20
            if y >= 100:
                break
    if font and len(stats) > ITEMS_PER_PAGE:
        current_page = (stats_scroll // ITEMS_PER_PAGE) + 1
        total_pages = (len(stats) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        screen.brush = brushes.color(*DIM)
        screen.text(f"Page {current_page}/{total_pages}", 95, 98)
    if font:
        screen.brush = brushes.color(*WARNING)
        screen.text("C:Back UP/DOWN:Scroll", 5, 108)
    try:
        color = SUCCESS if (io.ticks // 250) % 2 == 0 else BG
        screen.brush = brushes.color(*color)
        screen.draw(shapes.circle(4, 4, 2))
    except Exception:
        pass

def update() -> None:
    global font
    screen.brush = brushes.color(*BG)
    screen.clear()
    _ensure_font()
    if font:
        screen.font = font
    _handle_input()
    _handle_wifi_connect()
    _check_connection_status()
    if view_mode == "stats":
        draw_stats_view()
    else:
        draw_status_view()
    return None
