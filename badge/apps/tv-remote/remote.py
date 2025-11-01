from aye_arr.nec.remotes.descriptor import RemoteDescriptor

# Generic TV Remote using NEC protocol
# Using a common TV remote address and standard button codes
class TVRemote(RemoteDescriptor):
    NAME = "TVRemote"
    
    # Common TV remote address (many TVs use 0x00 or similar)
    ADDRESS = 0x00
    
    # Standard NEC remote button codes for common TV functions
    BUTTON_CODES = {
        "POWER": 0x02,
        "CHANNEL_UP": 0x00,
        "CHANNEL_DOWN": 0x01,
        "VOLUME_UP": 0x10,
        "VOLUME_DOWN": 0x11,
        "MUTE": 0x0D,
        "1": 0x04,
        "2": 0x05,
        "3": 0x06,
        "4": 0x08,
        "5": 0x09,
        "6": 0x0A,
        "7": 0x0C,
        "8": 0x0F,
        "9": 0x0E,
        "0": 0x03,
    }
    
    def __init__(self):
        super().__init__()
