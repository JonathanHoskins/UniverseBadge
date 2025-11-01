# Sony TV Remote App

A universal remote control app for controlling Sony TVs using the badge's IR transmitter.

## Features

- Power, Volume, Channel, Mute controls
- Input/Source selection
- Menu navigation
- NEC protocol transmission
- Visual feedback for button presses
- GitHub-themed UI

## Sony TV Compatibility

This app uses **NEC protocol** codes that are compatible with many Sony TV models in universal remote mode:

- **Address**: `0x52` (Samsung-compatible codes that many Sony TVs accept)
- **Alternative**: If `0x52` doesn't work, try changing to `0x04` in `remote.py`

### Supported Commands

| Button | Function | Code |
|--------|----------|------|
| PWR | Power Toggle | 0x15 |
| VOL+ | Volume Up | 0x07 |
| VOL- | Volume Down | 0x0B |
| CH+ | Channel Up | 0x1B |
| CH- | Channel Down | 0x1F |
| MUTE | Mute Toggle | 0x0F |
| INPUT | Input/Source | 0x47 |
| MENU | Menu | 0x1A |

## Hardware Setup

### IR Transmitter Pin

The app is configured to use **GPIO pin 20** for IR transmission. This may need adjustment based on your badge model:

- Badge IR **Receiver**: Pin 21 (confirmed)
- Badge IR **Transmitter**: Pin 20 (default, may need verification)

### If Remote Doesn't Work

1. **Check IR TX Pin**: 
   - If pin 20 doesn't work, try pins: 22, 19, or 23
   - Edit `IR_TX_PIN` in `__init__.py`
   - Check your badge's hardware documentation

2. **Check Initialization**:
   - The app will show "INIT ERROR" if IR sender fails to initialize
   - Check the console output for detailed error messages

3. **Check Sony TV Model**:
   - Some Sony TVs only respond to Sony's proprietary SIRC protocol
   - Try changing `ADDRESS` in `remote.py` from `0x52` to `0x04`
   - Newer Sony TVs may require learning mode or app pairing

4. **Distance & Aiming**:
   - Point the badge's IR transmitter directly at the TV's receiver
   - Try from 1-3 meters distance
   - Ensure no obstacles between badge and TV

## Usage

1. **Navigate**: Use UP/DOWN buttons to select a remote button
2. **Send**: Press A button to transmit the IR code
3. **Cooldown**: Wait 300ms between sends (prevents duplicate commands)
4. **Status**: Bottom of screen shows current address being used

## Troubleshooting

### "INIT ERROR" Displayed

- IR transmitter hardware not found on specified pin
- Try different `IR_TX_PIN` values
- Check that `aye_arr.nec` library is available

### TV Not Responding

1. **Test with multiple TVs** - Confirm badge is transmitting
2. **Change address** - Edit `remote.py` and try `ADDRESS = 0x04`
3. **Check TV's universal remote support** - Some Sony TVs need setup mode
4. **Verify distance** - Move closer to TV (< 2 meters)

### Code Changes Not Taking Effect

- Save files and reboot badge
- Check for Python syntax errors in console
- Ensure `remote.py` is in `/system/apps/tv-remote/`

## Customization

### Add More Buttons

Edit `BUTTONS` array in `__init__.py`:

```python
BUTTONS = [
    {"label": "NEW", "code": "NEW_COMMAND", "x": 60, "y": 105},
    # ... existing buttons
]
```

Then add the command code to `remote.py`:

```python
BUTTON_CODES = {
    "NEW_COMMAND": 0x1D,  # Your hex code
    # ... existing codes
}
```

### Change TV Brand

For other TV brands, edit `remote.py`:

```python
# Samsung TVs often use:
ADDRESS = 0xE0E0  # Extended address

# LG TVs often use:
ADDRESS = 0x20  # Simple address
```

Then update `BUTTON_CODES` with brand-specific codes (search online for NEC codes for your TV model).

## Technical Details

- **Protocol**: NEC Infrared
- **Carrier Frequency**: 38kHz (standard)
- **PIO**: Uses PIO instance 0, state machine 0
- **Transmission**: Single burst per button press
- **Cooldown**: 300ms between transmissions

## Files

- `__init__.py` - Main app logic, UI, and IR control
- `remote.py` - Sony TV NEC code definitions
- `icon.png` - Remote control icon (24x24)
- `README.md` - This documentation

## References

- [NEC Protocol Specification](https://www.sbprojects.net/knowledge/ir/nec.php)
- [Sony TV IR Codes](https://www.remotecentral.com/cgi-bin/mboard/rc-pronto/thread.cgi?26250)
- Badge Hardware: See `/badge/AGENTS.md` for IR pin details

## License

Part of the UniverseBadge project.
