import importlib
from conftest import prepare_app_import


def test_hc911_handle_fetch_button_triggers_fetch_when_a_pressed():
    prepare_app_import("hc911")
    hc911 = importlib.import_module("badge.apps.hc911")

    # Ensure not currently fetching
    hc911.fetching = False

    # Monkeypatch _start_fetch_async to record calls
    calls = {"count": 0}

    def _fake_start():
        calls["count"] += 1

    hc911._start_fetch_async = _fake_start  # type: ignore[attr-defined]

    # Simulate pressing A
    from badgeware import io
    io.pressed.add(io.BUTTON_A)

    # Call helper and clear pressed
    hc911._handle_fetch_button()
    io.pressed.clear()

    assert calls["count"] == 1


def test_hc911_wifi_toggle_without_secrets_sets_error_and_disables_wifi():
    prepare_app_import("hc911")
    hc911 = importlib.import_module("badge.apps.hc911")

    # Start from clean state
    hc911.wifi_enabled = False
    hc911.wlan = None
    hc911.connect_attempted = False
    hc911.status_text = ""
    hc911.error_msg = None

    # Press B to toggle WiFi on; since no secrets are available in tests,
    # the app should surface a Secrets error and keep wifi disabled.
    from badgeware import io
    io.pressed.add(io.BUTTON_B)

    hc911._handle_wifi_toggle()

    # Clear pressed for safety
    io.pressed.clear()

    assert hc911.wifi_enabled is False
    assert hc911.connect_attempted is False
    # Should show a friendly hint to create secrets
    assert hc911.status_text in ("Secrets error", "Network error", "WiFi error")


def test_hc911_periodic_check_triggers_auto_fetch_on_connect():
    # Prepare app and simulate WiFi becoming connected
    prepare_app_import("hc911")
    hc911 = importlib.import_module("badge.apps.hc911")

    # Ensure clean state
    hc911.fetching = False
    hc911.wifi_enabled = True
    hc911.connect_attempted = True
    hc911.wifi_was_connected = False

    # Install a fake _start_fetch_async to avoid threading/network
    calls = {"count": 0}

    def _fake_start_fetch_async(allow_sync_fallback=True):  # signature match
        calls["count"] += 1

    hc911._start_fetch_async = _fake_start_fetch_async  # type: ignore[attr-defined]

    # Provide a stub WLAN that reports connected
    class _StubWLAN:
        def isconnected(self):
            return True

        def status(self):
            return 3

    hc911.wlan = _StubWLAN()

    # Force periodic check window
    from badgeware import io
    io.ticks = 10_000
    hc911.last_wifi_check = 0

    # Call the periodic checker
    hc911._periodic_wifi_status_check()

    # It should have triggered exactly one auto-fetch and marked connected state
    assert calls["count"] == 1
    assert hc911.wifi_was_connected is True
    # Status text is set to "Fetching..." just before the async call
    assert hc911.status_text == "Fetching..."
