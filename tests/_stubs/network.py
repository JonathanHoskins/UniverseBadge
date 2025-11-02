"""
Network stubs for desktop emulation.

Provides working network.WLAN and socket implementations that use
real network connections on the desktop, allowing WiFi and network
apps to function in the emulator.
"""
import socket as _real_socket
import time

# Mock WLAN status codes (from MicroPython)
STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = -3
STAT_NO_AP_FOUND = -2
STAT_CONNECT_FAIL = -1
STAT_GOT_IP = 3

# Mode constants
STA_IF = 0
AP_IF = 1


class WLAN:
    """Mock WLAN interface that simulates WiFi connection using desktop network."""
    
    def __init__(self, interface_id):
        self._interface_id = interface_id
        self._active = False
        self._connected = False
        self._ssid = None
        self._password = None
        self._connect_time = 0
        self._status = STAT_IDLE
        
    def active(self, is_active=None):
        """Get or set active state."""
        if is_active is None:
            return self._active
        self._active = bool(is_active)
        if not self._active:
            self._connected = False
            self._status = STAT_IDLE
        return None
    
    def connect(self, ssid, password=None):
        """Simulate WiFi connection. On desktop, just mark as connected after brief delay."""
        self._ssid = ssid
        self._password = password
        self._connect_time = time.time()
        self._status = STAT_CONNECTING
        # Simulate instant connection on desktop (we have real network)
        self._connected = True
        self._status = STAT_GOT_IP
    
    def isconnected(self):
        """Check if connected."""
        # On desktop, if we activated and connected, assume we're online
        if not self._active:
            return False
        if self._status == STAT_CONNECTING:
            # After 1 second, mark as connected
            if time.time() - self._connect_time > 1.0:
                self._connected = True
                self._status = STAT_GOT_IP
        return self._connected
    
    def status(self, param=None):
        """Get connection status or specific parameter."""
        if param == "rssi":
            return -45  # Mock signal strength in dBm
        if param is None:
            return self._status
        return self._status
    
    def ifconfig(self):
        """Return IP configuration."""
        # Return mock but realistic-looking config
        return ("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
    
    def config(self, param):
        """Get configuration parameter."""
        if param == "mac":
            return bytes([0x00, 0x11, 0x22, 0x33, 0x44, 0x55])
        if param == "ssid":
            return self._ssid or "Desktop-Network"
        if param == "channel":
            return 6
        return None


# Export real socket module functions for desktop use
socket = _real_socket.socket
AF_INET = _real_socket.AF_INET
SOCK_STREAM = _real_socket.SOCK_STREAM
SOCK_DGRAM = _real_socket.SOCK_DGRAM


def getaddrinfo(host, port, family=0, socktype=0, proto=0, flags=0):
    """Wrapper for socket.getaddrinfo that returns MicroPython-compatible format."""
    results = _real_socket.getaddrinfo(host, port, family, socktype, proto, flags)
    # Return in format compatible with MicroPython: [(family, type, proto, canonname, sockaddr)]
    return results
