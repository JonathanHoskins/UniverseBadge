# Roku Remote Control App

A universal remote control app for controlling Roku streaming devices using the badge's IR transmitter.

## Features

- Navigation controls (Up/Down/Left/Right/OK)
- Home, Back buttons
- Play/Pause control
- Volume controls (for Roku TV/soundbar)
- Visual feedback for button presses
- GitHub-themed UI

## Roku Compatibility

This app uses **NEC protocol** with Roku's official IR codes:

- **Address**: `0xEE87` (Standard Roku NEC address)
- **Protocol**: NEC Infrared Remote Control
- **Compatible Devices**:
  - Roku Streaming Stick/Stick+
  - Roku Ultra
  - Roku Express/Express+
  - Roku Premiere/Premiere+
  - Roku TV (all models)
  - Roku Streambar/Streambar Pro

### Supported Commands

| Button | Function | Code |
|--------|----------|------|
| HOME | Home Screen | 0x03 |
| UP | Navigate Up | 0x05 |
| DOWN | Navigate Down | 0x06 |
| LEFT | Navigate Left | 0x07 |
| RIGHT | Navigate Right | 0x04 |
| OK | Select/OK | 0x02 |
| BACK | Back/Exit | 0x0D |
| PLAY | Play/Pause | 0x0B |
| VOL+ | Volume Up* | 0x14 |
| VOL- | Volume Down* | 0x15 |

*Volume controls work on Roku TV and Streambar models. On streaming sticks, they control TV volume via HDMI-CEC if your TV supports it.

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

3. **Check Roku Device**:
   - Ensure Roku is powered on and not in sleep mode
   - Some Roku devices have IR receiver on front, others on top
   - Roku Streaming Stick models have IR receiver in the Roku logo

4. **Distance & Aiming**:
   - Point the badge's IR transmitter directly at the Roku's IR receiver
   - Try from 1-5 meters distance (Roku IR is generally more sensitive than TV remotes)
   - For Roku Stick: aim at the side with the Roku logo
   - For Roku boxes: aim at the front panel

5. **Test Basic Functions**:
   - Start with HOME button - should take you to Roku home screen
   - Try OK button on home screen - should select highlighted app
   - Navigation (UP/DOWN/LEFT/RIGHT) should move through menu

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

1. **Verify Roku is on** - Check that device has power and is awake
2. **Find IR receiver** - Look for small dark window on Roku device
3. **Test distance** - Start close (< 1 meter) and gradually move back
4. **Try other buttons** - If HOME works, others should too
5. **Check badge IR output** - Use phone camera to see if IR LED blinks (appears purple/white on camera)

### Additional Roku Buttons

Want more functions? Edit `remote.py` to add these Roku codes:

```python
"SEARCH": 0x0A,    # Voice search
"REV": 0x08,       # Rewind
"FWD": 0x09,       # Fast-forward  
"INFO": 0x0C,      # Info (*)
"REPLAY": 0x13,    # Instant replay
"MUTE": 0x16,      # Mute
"POWER": 0x17,     # Power (CEC-enabled TVs)
```

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

For other streaming devices or TV brands, edit `remote.py`:

```python
# Amazon Fire TV
ADDRESS = 0xFB04  # Fire TV address
BUTTON_CODES = {
    "HOME": 0x03,
    # ... Fire TV specific codes
}

# Apple TV (uses different protocol - may not work with NEC)
# Samsung TV
ADDRESS = 0xE0E0  # Samsung extended address

# LG TV  
ADDRESS = 0x20DF  # LG address
```

Then update button codes with brand-specific values (search online for NEC codes).

## Why Roku?

Roku devices are well-documented and consistently use the NEC IR protocol with the same address (0xEE87) across all models. This makes them ideal for IR remote projects. The codes are published in Roku's official documentation, ensuring compatibility.

### Roku vs Other Devices

- ✅ **Roku**: Excellent - Standard NEC, well-documented, works on all models
- ⚠️ **Sony TV**: Variable - Some use NEC, others use proprietary SIRC protocol
- ⚠️ **Samsung**: Mixed - Newer models prefer Bluetooth/WiFi over IR
- ⚠️ **LG**: Similar to Samsung - IR support varies by model
- ❌ **Apple TV**: Bluetooth only (4th gen+), no IR support
- ✅ **Fire TV**: Good - Uses NEC protocol with address 0xFB04


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

- [Roku External Control API](https://developer.roku.com/docs/developer-program/debugging/external-control-api.md)
- [Roku IR Code Specification](https://sdkdocs.roku.com/display/sdkdoc/External+Control+Guide)
- [NEC Protocol Specification](https://www.sbprojects.net/knowledge/ir/nec.php)
- Badge Hardware: See `/badge/AGENTS.md` for IR pin details

## License

Part of the UniverseBadge project.
