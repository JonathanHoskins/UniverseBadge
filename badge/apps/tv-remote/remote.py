from aye_arr.nec.remotes.descriptor import RemoteDescriptor

# Roku Remote Control using NEC protocol
# Roku devices use NEC protocol with specific address and command codes
# Based on Roku's published IR codes specification
class TVRemote(RemoteDescriptor):
    NAME = "Roku"
    
    # Roku NEC address - Standard for Roku devices
    ADDRESS = 0xEE87
    
    # Roku NEC button codes
    # Source: https://developer.roku.com/docs/developer-program/debugging/external-control-api.md
    BUTTON_CODES = {
        # Navigation
        "HOME": 0x03,         # Home button
        "UP": 0x05,           # Up
        "DOWN": 0x06,         # Down
        "LEFT": 0x07,         # Left
        "RIGHT": 0x04,        # Right
        "OK": 0x02,           # OK/Select
        "BACK": 0x0D,         # Back
        
        # Playback
        "PLAY": 0x0B,         # Play/Pause
        "REV": 0x08,          # Reverse/Rewind
        "FWD": 0x09,          # Forward/Fast-forward
        
        # Channel/Search
        "SEARCH": 0x0A,       # Search
        "POWER": 0x17,        # Power (if TV supports CEC)
        
        # Volume (requires Roku TV or soundbar, not streaming stick)
        "VOLUME_UP": 0x14,    # Volume up
        "VOLUME_DOWN": 0x15,  # Volume down
        "MUTE": 0x16,         # Mute
        
        # Special
        "INFO": 0x0C,         # Info/Star (*)
        "REPLAY": 0x13,       # Replay (instant replay)
    }
    
    def __init__(self):
        super().__init__()
