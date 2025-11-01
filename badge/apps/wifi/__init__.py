"""
WiFi Connection Test App
Shows WiFi status and connection information
"""

from badgeware import screen, PixelFont, shapes, brushes, io

# UI state
font = None
status_lines = []
wifi_enabled = False
wlan = None
connect_attempted = False
last_update = 0
roku_scan_active = False

# Colors
BG = (13, 17, 23)
TEXT = (201, 209, 217)
SUCCESS = (46, 160, 67)
ERROR = (248, 81, 73)
WARNING = (255, 191, 0)


def add_status(text):
    """Add a status line (keeps last 8 lines)."""
    global status_lines
    status_lines.append(text)
    if len(status_lines) > 8:
        status_lines = status_lines[-8:]


def scan_for_roku():
    """Try to find Roku device using SSDP discovery."""
    add_status("Scanning for Roku...")
    try:
        import socket
        
        # SSDP multicast discovery
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900
        SSDP_MX = 2
        SSDP_ST = "roku:ecp"
        
        ssdp_request = (
            "M-SEARCH * HTTP/1.1\r\n"
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
            "MAN: \"ssdp:discover\"\r\n"
            f"MX: {SSDP_MX}\r\n"
            f"ST: {SSDP_ST}\r\n"
            "\r\n"
        )
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        
        # Send discovery request
        sock.sendto(ssdp_request.encode(), (SSDP_ADDR, SSDP_PORT))
        add_status("SSDP request sent")
        
        # Listen for responses
        found_roku = False
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                response = data.decode()
                if "roku" in response.lower():
                    add_status(f"Found Roku at {addr[0]}")
                    found_roku = True
                    break
        except Exception:
            pass  # Timeout or no more responses
        
        sock.close()
        
        if not found_roku:
            add_status("No Roku found")
            # Try common ECP port test
            add_status("Trying ECP test...")
            test_roku_ecp()
            
    except Exception as e:
        add_status(f"Scan error: {str(e)[:20]}")


def test_roku_ecp():
    """Test if a Roku is reachable on common local IPs."""
    try:
        import socket
        # Get our IP to determine subnet
        if wlan and wlan.isconnected():
            my_ip = wlan.ifconfig()[0]
            subnet = ".".join(my_ip.split(".")[:3])
            test_ips = [f"{subnet}.{i}" for i in [2, 10, 20, 30, 34, 50, 100]]
            for ip in test_ips:
                try:
                    sock = socket.socket()
                    sock.settimeout(0.7)
                    sock.connect((ip, 8060))
                    # Send GET request
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                    data = b""
                    try:
                        while True:
                            chunk = sock.recv(256)
                            if not chunk:
                                break
                            data += chunk
                            if len(data) > 2048:
                                break
                    except Exception:
                        pass
                    sock.close()
                    # Check for Roku-specific headers or XML
                    text = data.decode(errors="ignore")
                    if ("Server: Roku/" in text or "Application-URL:" in text or "<deviceType>roku:ecp</deviceType>" in text):
                        add_status(f"Roku confirmed at {ip}:8060!")
                        return
                except Exception:
                    pass
            add_status("No Roku on subnet")
    except Exception as e:
        add_status(f"ECP test err: {str(e)[:15]}")


def update():
    global font, wifi_enabled, wlan, connect_attempted, last_update, roku_scan_active
    
    screen.brush = brushes.color(*BG)
    screen.clear()
    
    # Load font on first run
    if font is None:
        try:
            font = PixelFont.load("/system/assets/fonts/ark.ppf")
            add_status("App started")
        except Exception as e:
            add_status(f"Font error: {str(e)[:20]}")
    
    if font:
        screen.font = font
    
    # Handle WiFi toggle with A button
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
    
    # Handle Roku scan with B button
    if io.BUTTON_B in io.pressed and not roku_scan_active:
        if wlan and wlan.isconnected():
            roku_scan_active = True
            scan_for_roku()
            roku_scan_active = False
        else:
            add_status("Connect WiFi first!")
    
    # Try to connect if enabled and not yet attempted
    if wifi_enabled and not connect_attempted:
        try:
            # Import network module
            import network
            add_status("Network module loaded")
            
            # Load WiFi credentials
            try:
                import sys
                sys.path.insert(0, "/")
                from secrets import WIFI_SSID, WIFI_PASSWORD
                sys.path.pop(0)
                add_status(f"SSID: {WIFI_SSID[:15]}")
            except Exception as e:
                add_status(f"Secrets error: {str(e)[:20]}")
                add_status("Create /secrets.py")
                wifi_enabled = False
                connect_attempted = True
            
            if wifi_enabled:
                # Initialize WLAN
                wlan = network.WLAN(network.STA_IF)
                wlan.active(True)
                add_status("WLAN activated")
                
                # Connect
                wlan.connect(WIFI_SSID, WIFI_PASSWORD)
                add_status("Connecting...")
                connect_attempted = True
                
        except Exception as e:
            add_status(f"Error: {str(e)[:30]}")
            wifi_enabled = False
            connect_attempted = True
    
    # Check connection status periodically
    if wifi_enabled and connect_attempted and wlan:
        if io.ticks - last_update > 1000:  # Check every second
            last_update = io.ticks
            try:
                if wlan.isconnected():
                    config = wlan.ifconfig()
                    add_status("Connected!")
                    add_status(f"IP: {config[0]}")
                else:
                    status = wlan.status()
                    add_status(f"Status: {status}")
            except Exception as e:
                add_status(f"Check error: {str(e)[:20]}")
    
    # Draw header
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text("WiFi Test", 5, 3)
        
        # Draw WiFi status indicator
        status_text = "ON" if wifi_enabled else "OFF"
        color = SUCCESS if wifi_enabled else ERROR
        screen.brush = brushes.color(*color)
        screen.text(status_text, 135, 3)
    
    # Draw status lines
    if font:
        screen.brush = brushes.color(*TEXT)
        y = 20
        for line in status_lines:
            if y < 105:
                screen.text(line[:26], 5, y)
                y += 10
    
    # Draw instructions
    if font:
        screen.brush = brushes.color(*WARNING)
        screen.text("A:WiFi  B:Find Roku", 5, 108)
    
    # Heartbeat indicator
    try:
        color = SUCCESS if (io.ticks // 250) % 2 == 0 else BG
        screen.brush = brushes.color(*color)
        screen.draw(shapes.circle(4, 4, 2))
    except Exception:
        pass
    
    return None
