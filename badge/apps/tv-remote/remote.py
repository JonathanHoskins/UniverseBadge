from aye_arr.nec.remotes.descriptor import RemoteDescriptor

# Sony TV Remote using NEC protocol
# Sony TVs often respond to NEC address 0x04 (some models) or 0x52 (Samsung-compatible)
# These are common codes that work with many Sony TVs in universal remote mode
class TVRemote(RemoteDescriptor):
    NAME = "SonyTV"
    
    # Sony TV NEC address - 0x52 is commonly used for Sony TVs in universal remote mode
    # Alternative: Try 0x04 if 0x52 doesn't work with your specific TV model
    ADDRESS = 0x52
    
    # NEC button codes for Sony TV compatible commands
    BUTTON_CODES = {
        "POWER": 0x15,        # Power toggle
        "CHANNEL_UP": 0x1B,   # Channel up
        "CHANNEL_DOWN": 0x1F, # Channel down
        "VOLUME_UP": 0x07,    # Volume up
        "VOLUME_DOWN": 0x0B,  # Volume down
        "MUTE": 0x0F,         # Mute toggle
        "INPUT": 0x47,        # Input/Source
        "MENU": 0x1A,         # Menu
        "1": 0x16,
        "2": 0x19,
        "3": 0x0D,
        "4": 0x18,
        "5": 0x1C,
        "6": 0x5E,
        "7": 0x08,
        "8": 0x42,
        "9": 0x52,
        "0": 0x4C,
    }
    
    def __init__(self):
        super().__init__()
