# IR Transmission Not Working? Here's Why

## The Real Problem: It's the Hardware Pin

**Bluetooth won't help** because:
1. Your badge has an **IR transmitter** (not Bluetooth remote capability)
2. Roku's Bluetooth is for mobile apps, not badge-to-Roku pairing
3. The issue is finding the **correct GPIO pin** for the IR LED

## Quick Diagnosis

### Step 1: Use Your Phone Camera
1. Open your phone's camera app
2. Point the badge's IR transmitter at the camera
3. Press A button in the remote app
4. **Look for a purple/white flash** on your phone screen
   - ✅ **See a flash?** → IR LED is working, pin is correct, aim/distance issue
   - ❌ **No flash?** → Wrong pin or hardware issue

### Step 2: Run the Pin Finder Tool

I've created `pin_finder.py` to help you find the correct pin:

```bash
# On your badge, run:
python badge/apps/tv-remote/pin_finder.py
```

**How to use it:**
1. Use UP/DOWN buttons to cycle through possible pins (20, 22, 19, 23, etc.)
2. Point badge at Roku
3. Press A to send HOME signal
4. **If Roku goes to home screen → YOU FOUND THE RIGHT PIN!**
5. Note the pin number and update `IR_TX_PIN` in `__init__.py`

### Step 3: Update the Pin

Once you find the working pin, edit `__init__.py`:

```python
IR_TX_PIN = 22  # Or whatever pin worked in the finder
```

## Why Pin 20 Might Be Wrong

- **Badge IR RX**: Pin 21 (confirmed)
- **Badge IR TX**: Unknown - not documented
- **Beacon hardware IR TX**: Pin 0 (different device)
- **Badge RGB LED**: Pins 18, 19, 20 (might conflict)

**Pin 20 collision?** If pin 20 is used for the RGB LED, it won't work for IR transmission.

## Other Possible Issues

### 1. IR LED Not Connected
- Badge might not have IR TX LED installed
- Check if there's a small dark component (IR LED) on the badge

### 2. PIO/State Machine Conflict
- Another app might be using PIO 0, state machine 0
- Try restarting the badge before running the remote app

### 3. Library Missing
- Check if `aye_arr.nec` library is installed
- Error message will say "Import 'aye_arr.nec' could not be resolved"

### 4. Power/Range Issues
- Badge battery might be low (IR LED needs power)
- Try from very close distance (< 30cm) first
- Make sure Roku is awake and ready

## Alternative: WiFi Control

If IR truly doesn't work, consider:
- **Roku has a network API** (External Control Protocol - ECP)
- Could create WiFi-based remote using badge's WiFi
- Requires Roku and badge on same network
- Uses HTTP requests instead of IR

Would you like me to create a WiFi-based version?

## Bottom Line

**Don't switch to Bluetooth** - that won't solve the problem. The issue is:
1. Finding the correct IR TX GPIO pin
2. Or determining if your badge model has IR TX hardware

Run `pin_finder.py` and report back what happens!
