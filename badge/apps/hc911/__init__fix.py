        # Fetch totals (yearly, daily)
        import json as _json
        global yearly_total, daily_total, active_incidents
        
        fetch_error = None
        try:
            print("[hc911] Fetching /api/count")
            b = _https_get("hc911server.com", "/api/count")
            print(f"[hc911] Count response length: {len(b)}")
            print(f"[hc911] Count response (first 200 bytes): {b[:200]}")
            data = _json.loads(b.decode("utf-8", errors="ignore"))
            print(f"[hc911] Count parsed: {data}")
            # Expect [[{"": YEARLY}], [{"": DAILY}]]
            try:
                yearly_total = int(list(data[0][0].values())[0])
                daily_total = int(list(data[1][0].values())[0])
                print(f"[hc911] Success: yearly={yearly_total}, daily={daily_total}")
            except Exception as e:
                print(f"[hc911] Count parse failed: {e}")
                fetch_error = f"Parse: {str(e)[:15]}"
                pass
        except Exception as e:
            print(f"[hc911] Count fetch failed: {e}")
            fetch_error = f"Fetch: {str(e)[:15]}"
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
            data = _json.loads(b.decode("utf-8", errors="ignore"))
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
            # Show actual error
            error_msg = fetch_error if fetch_error else "All APIs failed"
            cached_error_msg = error_msg
            try:
                last_error_time = io.ticks
            except Exception:
                pass
