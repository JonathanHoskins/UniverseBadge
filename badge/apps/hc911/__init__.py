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
wifi_connect_start = 0

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
    
    print("[hc911] ========== FETCH STARTED ==========")
    fetching = True
    status_text = "Fetching..."
    error_msg = None
    
    try:
        print("[hc911] Importing network modules")
        # Import network modules
        import socket
        
        # Try to import ssl for HTTPS support
        try:
            import ssl
            has_ssl = True
            print("[hc911] SSL available")
        except ImportError:
            has_ssl = False
            print("[hc911] SSL NOT available")
        
        # Check WiFi connection
        global wlan
        print(f"[hc911] Checking WiFi: wlan={wlan}")
        if not (wlan and wlan.isconnected()):
            print("[hc911] WiFi not connected!")
            status_text = "WiFi not connected"
            error_msg = "Press B to enable WiFi"
            cached_error_msg = error_msg
            try:
                last_error_time = io.ticks
            except Exception:
                pass
            fetching = False
            return
        
        print("[hc911] WiFi OK, defining _https_get")
        
        # Helper: minimal HTTPS GET with optional headers and chunked decoding
        def _https_get(host, path, extra_headers=None):
            addr = socket.getaddrinfo(host, 443)[0][-1]
            s = socket.socket()
            # Keep timeouts short so UI remains responsive if run on main thread
            s.settimeout(5)
            s.connect(addr)
            if has_ssl:
                # Try SNI first; fall back to no-SNI (common on MicroPython)
                try:
                    s = ssl.wrap_socket(s, server_hostname=host)
                except TypeError:
                    try:
                        s = ssl.wrap_socket(s)
                    except Exception:
                        pass
                except AttributeError:
                    try:
                        s = ssl.wrap_socket(s)
                    except Exception:
                        pass
                except Exception:
                    try:
                        context = ssl.create_default_context()
                        s = context.wrap_socket(s, server_hostname=host)
                    except Exception:
                        pass
            # build request
            headers = [
                f"GET {path} HTTP/1.1",
                f"Host: {host}",
                "Connection: close",
            ]
            if extra_headers:
                for k, v in extra_headers.items():
                    headers.append(f"{k}: {v}")
            req = "\r\n".join(headers) + "\r\n\r\n"
            s.send(req.encode())
            # receive
            resp = b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                resp += chunk
                if len(resp) > 200000:
                    break
            s.close()
            # split headers/body
            sep = resp.find(b"\r\n\r\n")
            if sep == -1:
                return resp
            # MicroPython bytes.decode may not accept keyword args; use positional only
            try:
                raw_headers = resp[:sep].decode("utf-8")
            except Exception:
                try:
                    raw_headers = resp[:sep].decode("latin-1")
                except Exception:
                    raw_headers = str(resp[:sep])
            body = resp[sep+4:]
            if "Transfer-Encoding: chunked" in raw_headers:
                # dechunk
                i = 0
                out = b""
                while True:
                    j = body.find(b"\r\n", i)
                    if j == -1:
                        break
                    size_str = body[i:j].split(b";")[0]
                    try:
                        size = int(size_str, 16)
                    except Exception:
                        break
                    i = j + 2
                    if size == 0:
                        break
                    out += body[i:i+size]
                    i += size + 2  # skip CRLF
                body = out
            return body

        # Fetch totals (yearly, daily)
        import json as _json
        global yearly_total, daily_total, active_incidents
        
        fetch_error = None
        try:
            print("[hc911] Fetching /api/count")
            b = _https_get("hc911server.com", "/api/count")
            print(f"[hc911] Count response length: {len(b)}")
            print(f"[hc911] Count response (first 200 bytes): {b[:200]}")
            # Decode body without keyword args for compatibility
            try:
                body_text = b.decode("utf-8")
            except Exception:
                try:
                    body_text = b.decode("latin-1")
                except Exception:
                    body_text = str(b)
            data = _json.loads(body_text)
            print(f"[hc911] Count parsed: {data}")
            # Expect [[{"": YEARLY}], [{"": DAILY}]]
            try:
                yearly_total = int(list(data[0][0].values())[0])
                daily_total = int(list(data[1][0].values())[0])
                print(f"[hc911] Success: yearly={yearly_total}, daily={daily_total}")
            except Exception as e:
                print(f"[hc911] Count parse failed: {e}")
                fetch_error = f"Parse: {str(e)[:40]}"
                pass
        except Exception as e:
            print(f"[hc911] Count fetch failed: {e}")
            fetch_error = f"Fetch: {str(e)[:40]}"
            # leave totals as-is
            pass

        # Try to fetch current active incidents count (uses public header by default)
        try:
            print("[hc911] Fetching /api/calls")
            # Load optional token from secrets if available
            try:
                import sys as _sys
                _sys.path.insert(0, "/")
                from secrets import HC911_TOKEN  # type: ignore
                _sys.path.pop(0)
                print("[hc911] Using secrets token")
            except Exception:
                HC911_TOKEN = None  # type: ignore
                print("[hc911] Using default token")
            # Default to the public header observed on the site
            token = HC911_TOKEN or "my-secure-token"  # type: ignore
            headers = {
                "X-Frontend-Auth": token,
                "Origin": "https://www.hamiltontn911.gov",
            }
            b = _https_get("hc911server.com", "/api/calls", headers)
            print(f"[hc911] Calls response length: {len(b)}")
            print(f"[hc911] Calls response (first 200 bytes): {b[:200]}")
            try:
                body_text = b.decode("utf-8")
            except Exception:
                try:
                    body_text = b.decode("latin-1")
                except Exception:
                    body_text = str(b)
            data = _json.loads(body_text)
            print(f"[hc911] Calls type: {type(data)}, is_list: {isinstance(data, list)}")
            if isinstance(data, list):
                active_incidents = len(data)
                print(f"[hc911] Active incidents: {active_incidents}")
        except Exception as e:
            print(f"[hc911] Calls fetch failed: {e}")
            # Ignore if unauthorized or failed
            pass
        
        print(f"[hc911] Final state: daily={daily_total}, yearly={yearly_total}, active={active_incidents}")
        if (daily_total is not None and yearly_total is not None) or (active_incidents is not None):
            # Data available; clear transient WiFi message
            status_text = ""
            print("[hc911] SUCCESS")
            # Clear any previous error indicator on success
            last_error_time = 0
            cached_error_msg = None
        else:
            print("[hc911] FAILED - no data")
            status_text = "Parse error"
            # Show which values are None for debugging
            error_msg = fetch_error if fetch_error else "All APIs failed"
            cached_error_msg = error_msg
            try:
                last_error_time = io.ticks
            except Exception:
                pass
        
    except Exception as e:
        print(f"[hc911] EXCEPTION in fetch: {e}")
        import sys
        sys.print_exception(e)
        status_text = "Error"
        error_msg = str(e)[:30]
        cached_error_msg = error_msg
        try:
            last_error_time = io.ticks
        except Exception:
            pass
    finally:
        print("[hc911] ========== FETCH ENDED ==========")
        fetching = False


def _start_fetch_async(allow_sync_fallback=True):
    """Kick off a fetch in a background thread when available to avoid UI freezes.
    If threading isn't supported and allow_sync_fallback is True, runs synchronously; otherwise, skips."""
    global fetching, status_text, error_msg
    if fetching:
        return
    try:
        import _thread  # type: ignore
        # Start threaded fetch
        status_text = "Fetching..."
        error_msg = None
        fetching = True
        _thread.start_new_thread(fetch_incidents, ())
    except Exception:
        # No threading support
        if allow_sync_fallback:
            fetch_incidents()
        else:
            # Avoid blocking the UI on auto-fetch when threads are unavailable
            status_text = "Press A to fetch"
            error_msg = None
            fetching = False


def update():
    global font, last_fetch, status_text, error_msg, cached_error_msg
    global wifi_enabled, wlan, connect_attempted, last_wifi_check, wifi_was_connected, wifi_connect_start
    
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
        print(f"[hc911] Button B pressed, wifi_enabled={wifi_enabled}")
        wifi_enabled = not wifi_enabled
        if wifi_enabled:
            print("[hc911] Enabling WiFi...")
            status_text = "WiFi: enabling..."
            try:
                import network  # type: ignore
                print("[hc911] Network module imported")
                # Load WiFi credentials
                try:
                    import sys
                    sys.path.insert(0, "/")
                    from secrets import WIFI_SSID, WIFI_PASSWORD  # type: ignore
                    sys.path.pop(0)
                    print(f"[hc911] Loaded credentials: SSID={WIFI_SSID}")
                except Exception as e:
                    print(f"[hc911] Secrets load error: {e}")
                    status_text = "Secrets error"
                    error_msg = "Create /secrets.py"
                    wifi_enabled = False
                    connect_attempted = False
                
                if wifi_enabled:
                    wlan = network.WLAN(network.STA_IF)
                    wlan.active(True)
                    print(f"[hc911] WLAN active, connecting to {WIFI_SSID}")
                    status_text = "Connecting WiFi..."
                    try:
                        wlan.connect(WIFI_SSID, WIFI_PASSWORD)  # type: ignore
                        connect_attempted = True
                        print("[hc911] Connect command sent")
                        try:
                            wifi_connect_start = io.ticks
                        except Exception:
                            wifi_connect_start = 0
                    except Exception as e:
                        print(f"[hc911] Connect error: {e}")
                        status_text = "WiFi error"
                        error_msg = str(e)[:30]
                        wifi_enabled = False
                        connect_attempted = False
            except Exception as e:
                print(f"[hc911] Network error: {e}")
                status_text = "Network error"
                error_msg = str(e)[:30]
                wifi_enabled = False
                connect_attempted = False
        else:
            print("[hc911] Disabling WiFi")
            status_text = "WiFi disabled"
            try:
                if wlan:
                    wlan.active(False)
            except Exception:
                pass
            wlan = None
            connect_attempted = False
            wifi_was_connected = False
            wifi_connect_start = 0

    # Periodic WiFi status check
    if wifi_enabled and connect_attempted and wlan:
        if io.ticks - last_wifi_check > 1000:  # every second
            last_wifi_check = io.ticks
            try:
                is_connected = wlan.isconnected()
                status = wlan.status()
                print(f"[hc911] WiFi check: connected={is_connected}, status={status}")
                
                if is_connected:
                    if not wifi_was_connected and not fetching:
                        # First time connection established: auto-fetch once
                        print("[hc911] AUTO-FETCH triggered")
                        wifi_was_connected = True
                        status_text = "Fetching..."  # Clear "WiFi connected" immediately
                        last_fetch = io.ticks
                        try:
                            _start_fetch_async(allow_sync_fallback=False)
                        except Exception as e:
                            print(f"[hc911] Auto-fetch exception: {e}")
                            status_text = "Error"
                            error_msg = str(e)[:30]
                    elif (active_incidents is None and daily_total is None and yearly_total is None) and not fetching and wifi_was_connected:
                        # Connected but no data and not currently fetching - show hint
                        status_text = "Press A to fetch"
                else:
                    wifi_was_connected = False
                    # Show status code, and timeout after 15s
                    try:
                        st = wlan.status()
                        status_text = f"WiFi status: {st}"
                    except Exception:
                        pass
                    try:
                        if wifi_connect_start and (io.ticks - wifi_connect_start > 15000):
                            status_text = "WiFi failed"
                            error_msg = "Timeout or credentials"
                            try:
                                wlan.active(False)
                            except Exception:
                                pass
                            wifi_enabled = False
                            connect_attempted = False
                            wifi_connect_start = 0
                    except Exception:
                        pass
            except Exception:
                pass

    # Handle fetch button
    if io.BUTTON_A in io.pressed and not fetching:
        print("[hc911] BUTTON A pressed - manual fetch")
        # If there's a cached error (even if expired), show it briefly as tooltip
        if cached_error_msg and not error_msg:
            error_msg = f"Last: {cached_error_msg}"
        last_fetch = io.ticks
        try:
            _start_fetch_async()
        except Exception as e:
            print(f"[hc911] Manual fetch exception: {e}")
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
                # Note: MicroPython shapes.circle likely doesn't accept keyword args
                screen.draw(shapes.circle(152, 6, 2))
        except Exception:
            pass
        # Show a red error dot for ~10s after a fetch error (when not currently connecting)
        try:
            if (not (wifi_enabled and wlan and not wlan.isconnected())) and last_error_time > 0:
                if io.ticks - last_error_time < 10000:
                    screen.brush = brushes.color(*ERROR)
                    screen.draw(shapes.circle(152, 6, 2))
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
            # No data yet - show debug info
            screen.brush = brushes.color(*DIM)
            
            # Show WiFi status if available
            if wlan and connect_attempted:
                try:
                    is_conn = wlan.isconnected()
                    stat = wlan.status()
                    screen.text(f"WiFi: conn={is_conn}", 5, 20)
                    screen.text(f"Status: {stat}", 5, 32)
                except Exception:
                    pass
            
            screen.text("No data loaded", 5, 47)
            screen.text("Press A to fetch", 5, 59)
    
    # Draw status
    if font:
        screen.brush = brushes.color(*TEXT)
        screen.text(status_text, 5, 80)
        
        if error_msg:
            screen.brush = brushes.color(*ERROR)
            screen.text(error_msg[:36], 5, 92)
    
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
            screen.draw(shapes.circle(4, 4, 2))
        except Exception:
            pass

    return None

    return None
