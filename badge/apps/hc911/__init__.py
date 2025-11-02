"""
Hamilton County 911 Active Incidents App
Displays current incident count from hamiltontn911.gov
"""

from badgeware import screen, PixelFont, shapes, brushes, io

# UI state
font = None
status_text = "Press A to fetch"
active_incidents = None
daily_total = None
yearly_total = None
last_fetch = 0
fetching = False
error_msg = None
wifi_enabled = False
wlan = None
connect_attempted = False
last_wifi_check = 0
wifi_was_connected = False
last_error_time = 0
cached_error_msg = None

# Colors
BG = (13, 17, 23)
TEXT = (201, 209, 217)
SUCCESS = (46, 160, 67)
ERROR = (248, 81, 73)
WARNING = (255, 191, 0)
DIM = (88, 96, 105)


def fetch_incidents():
    """Fetch incident data from Hamilton County 911 website."""
    global active_incidents, daily_total, yearly_total, status_text, error_msg, fetching, last_error_time, cached_error_msg
    
    fetching = True
    status_text = "Fetching..."
    error_msg = None
    
    try:
        # Import network modules
        import network  # type: ignore
        import socket
        
        # Check WiFi connection
        global wlan
        if not (wlan and wlan.isconnected()):
            status_text = "WiFi not connected"
            error_msg = "Press B to enable WiFi"
            cached_error_msg = error_msg
            try:
                last_error_time = io.ticks
            except Exception:
                pass
            fetching = False
            return
        
        # Parse URL
        url = "www.hamiltontn911.gov"
        path = "/active-incidents.php"
        
        status_text = "Connecting..."
        
        # Create socket and connect
        addr = socket.getaddrinfo(url, 80)[0][-1]
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        
        # Send HTTP GET request
        request = f"GET {path} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
        s.send(request.encode())
        
        status_text = "Receiving..."
        
        # Read response
        response = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            response += chunk
            if len(response) > 50000:  # Limit response size
                break
        
        s.close()
        
        # Parse response
        html = response.decode("utf-8", errors="ignore")
        
        # Extract incident counts using simple string search
        # Format: "CURRENT ACTIVE INCIDENTS:  32"
        active_idx = html.find("CURRENT ACTIVE INCIDENTS:")
        daily_idx = html.find("DAILY TOTAL INCIDENTS:")
        yearly_idx = html.find("YEARLY INCIDENTS:")
        
        if active_idx != -1:
            # Extract number after the label
            text = html[active_idx:active_idx+100]
            # Find the number between the colon and next newline/tag
            start = text.find(":") + 1
            end = text.find("\n", start)
            if end == -1:
                end = text.find("<", start)
            num_str = text[start:end].strip()
            active_incidents = int(num_str)
        
        if daily_idx != -1:
            text = html[daily_idx:daily_idx+100]
            start = text.find(":") + 1
            end = text.find("\n", start)
            if end == -1:
                end = text.find("<", start)
            num_str = text[start:end].strip()
            daily_total = int(num_str)
        
        if yearly_idx != -1:
            text = html[yearly_idx:yearly_idx+100]
            start = text.find(":") + 1
            end = text.find("\n", start)
            if end == -1:
                end = text.find("<", start)
            num_str = text[start:end].strip()
            yearly_total = int(num_str)
        
        if active_incidents is not None:
            status_text = "Updated"
            # Clear any previous error indicator on success
            last_error_time = 0
            cached_error_msg = None
        else:
            status_text = "Parse error"
            error_msg = "Could not find data"
            cached_error_msg = error_msg
            try:
                last_error_time = io.ticks
            except Exception:
                pass
        
    except Exception as e:
        status_text = "Error"
        error_msg = str(e)[:30]
        cached_error_msg = error_msg
        try:
            last_error_time = io.ticks
        except Exception:
            pass
    finally:
        fetching = False


def update():
    global font, last_fetch, status_text, error_msg, cached_error_msg
    global wifi_enabled, wlan, connect_attempted, last_wifi_check, wifi_was_connected
    
    screen.brush = brushes.color(*BG)
    screen.clear()
    
    # Load font on first run
    if font is None:
        try:
            font = PixelFont.load("/system/assets/fonts/ark.ppf")
        except Exception:
            pass
    
    if font:
        screen.font = font
    
    # Handle WiFi toggle on B
    if io.BUTTON_B in io.pressed:
        wifi_enabled = not wifi_enabled
        if wifi_enabled:
            status_text = "WiFi: enabling..."
            try:
                import network  # type: ignore
                # Load WiFi credentials
                try:
                    import sys
                    sys.path.insert(0, "/")
                    from secrets import WIFI_SSID, WIFI_PASSWORD  # type: ignore
                    sys.path.pop(0)
                except Exception as e:
                    status_text = "Secrets error"
                    error_msg = "Create /secrets.py"
                    wifi_enabled = False
                    connect_attempted = False
                
                if wifi_enabled:
                    wlan = network.WLAN(network.STA_IF)
                    wlan.active(True)
                    status_text = "Connecting WiFi..."
                    try:
                        wlan.connect(WIFI_SSID, WIFI_PASSWORD)  # type: ignore
                        connect_attempted = True
                    except Exception as e:
                        status_text = "WiFi error"
                        error_msg = str(e)[:30]
                        wifi_enabled = False
                        connect_attempted = False
            except Exception as e:
                status_text = "Network error"
                error_msg = str(e)[:30]
                wifi_enabled = False
                connect_attempted = False
        else:
            status_text = "WiFi disabled"
            try:
                if wlan:
                    wlan.active(False)
            except Exception:
                pass
            wlan = None
            connect_attempted = False
            wifi_was_connected = False

    # Periodic WiFi status check
    if wifi_enabled and connect_attempted and wlan:
        if io.ticks - last_wifi_check > 1000:  # every second
            last_wifi_check = io.ticks
            try:
                if wlan.isconnected():
                    status_text = "WiFi connected"
                    if not wifi_was_connected and not fetching:
                        # First time connection established: auto-fetch once
                        wifi_was_connected = True
                        last_fetch = io.ticks
                        try:
                            fetch_incidents()
                        except Exception as e:
                            status_text = "Error"
                            error_msg = str(e)[:30]
                else:
                    wifi_was_connected = False
            except Exception:
                pass

    # Handle fetch button
    if io.BUTTON_A in io.pressed and not fetching:
        # If there's a cached error (even if expired), show it briefly as tooltip
        if cached_error_msg and not error_msg:
            error_msg = f"Last: {cached_error_msg}"
        last_fetch = io.ticks
        try:
            fetch_incidents()
        except Exception as e:
            status_text = "Error"
            error_msg = str(e)[:30]
    
    # Draw header
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text("HC 911 Incidents", 5, 3)
        # WiFi indicator
        indicator = (SUCCESS, "ON") if (wifi_enabled and wlan) else (ERROR, "OFF")
        screen.brush = brushes.color(*indicator[0])
        screen.text(indicator[1], 135, 3)
        # Show a small spinner while WiFi is connecting
        try:
            if wifi_enabled and wlan and not wlan.isconnected():
                color = SUCCESS if (io.ticks // 150) % 2 == 0 else BG
                screen.brush = brushes.color(*color)
                screen.draw(shapes.circle(152, 6, radius=2))
        except Exception:
            pass
        # Show a red error dot for ~10s after a fetch error (when not currently connecting)
        try:
            if (not (wifi_enabled and wlan and not wlan.isconnected())) and last_error_time > 0:
                if io.ticks - last_error_time < 10000:
                    screen.brush = brushes.color(*ERROR)
                    screen.draw(shapes.circle(152, 6, radius=2))
        except Exception:
            pass
    
    # Draw incident data
    if font:
        y = 25
        
        if active_incidents is not None:
            # Active incidents (large)
            screen.brush = brushes.color(*WARNING)
            screen.text("Active Now:", 5, y)
            y += 12
            
            screen.brush = brushes.color(*SUCCESS)
            count_str = str(active_incidents)
            screen.text(count_str, 5, y)
            y += 20
            
            # Daily total
            if daily_total is not None:
                screen.brush = brushes.color(*DIM)
                screen.text(f"Today: {daily_total}", 5, y)
                y += 12
            
            # Yearly total
            if yearly_total is not None:
                screen.brush = brushes.color(*DIM)
                screen.text(f"Year: {yearly_total}", 5, y)
                y += 12
            
            # Last update time
            if last_fetch > 0:
                elapsed = (io.ticks - last_fetch) // 1000
                mins = elapsed // 60
                secs = elapsed % 60
                screen.brush = brushes.color(*DIM)
                if mins > 0:
                    screen.text(f"Updated {mins}m {secs}s ago", 5, y)
                else:
                    screen.text(f"Updated {secs}s ago", 5, y)
        else:
            # No data yet
            screen.brush = brushes.color(*DIM)
            screen.text("No data loaded", 5, 35)
            screen.text("Press A to fetch", 5, 47)
    
    # Draw status
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text(status_text, 5, 80)
        
        if error_msg:
            screen.brush = brushes.color(*ERROR)
            screen.text(error_msg[:26], 5, 92)
    
    # Draw instructions
    if font:
        screen.brush = brushes.color(*WARNING)
        if fetching:
            screen.text("Fetching...", 5, 108)
        else:
            screen.text("A:Refresh  B:WiFi", 5, 108)
    
    # Activity indicator
    if fetching:
        try:
            color = SUCCESS if (io.ticks // 150) % 2 == 0 else BG
            screen.brush = brushes.color(*color)
            screen.draw(shapes.circle(4, 4, radius=2))
        except Exception:
            pass
    
    return None
    
    return None
