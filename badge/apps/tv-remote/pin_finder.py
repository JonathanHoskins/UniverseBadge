"""
IR Pin Finder - Diagnostic Tool

This script helps you find the correct IR transmitter pin on your badge.
It will try different GPIO pins and you can test which one works.

Usage:
1. Run this script
2. Use UP/DOWN to select a pin number
3. Press A to test that pin
4. Point badge at your Roku and watch for a response
5. When you find the working pin, note it down!
"""

import sys
sys.path.insert(0, "/system/apps/tv-remote")

from badgeware import screen, PixelFont, shapes, brushes, io, run
from aye_arr.nec import NECSender
from remote import TVRemote

# Possible IR TX pins to test
# Common adjacent pins to RX pin 21
POSSIBLE_PINS = [20, 22, 19, 23, 18, 17, 16, 24, 25, 26, 27, 28]

current_pin_index = 0
sender = None
tv_remote = None
last_test_time = 0
test_result = ""

font = PixelFont.load("/system/assets/fonts/nope.ppf")

def try_init_pin(pin_num):
    global sender, tv_remote, test_result
    # Clean up previous sender
    if sender:
        try:
            sender.stop()
        except:
            pass
    
    sender = None
    tv_remote = None
    test_result = ""
    
    try:
        print(f"Testing pin {pin_num}...")
        sender = NECSender(pin_num, 0, 0)
        sender.start()
        tv_remote = TVRemote()
        test_result = f"Pin {pin_num} initialized OK"
        print(test_result)
        return True
    except Exception as e:
        test_result = f"Pin {pin_num} FAILED: {str(e)[:20]}"
        print(test_result)
        return False

def send_test_signal():
    global last_test_time, test_result
    if sender and tv_remote:
        try:
            # Send HOME button code - most obvious test
            sender.send_remote(tv_remote, "HOME")
            last_test_time = io.ticks
            test_result = f"Pin {POSSIBLE_PINS[current_pin_index]}: Sent HOME"
            print(test_result)
        except Exception as e:
            test_result = f"Send failed: {str(e)[:20]}"
            print(test_result)

def update():
    global current_pin_index, last_test_time
    
    # Clear screen
    screen.brush = brushes.color(13, 17, 23)
    screen.clear()
    
    # Title
    screen.brush = brushes.color(201, 209, 217)
    screen.font = font
    title = "IR PIN FINDER"
    title_w, _ = screen.measure_text(title)
    screen.text(title, (160 - title_w) // 2, 5)
    
    # Current pin display
    pin_num = POSSIBLE_PINS[current_pin_index]
    screen.brush = brushes.color(88, 166, 255)
    pin_text = f"PIN: {pin_num}"
    pin_w, _ = screen.measure_text(pin_text)
    screen.text(pin_text, (160 - pin_w) // 2, 25)
    
    # Pin selection
    if io.BUTTON_UP in io.pressed:
        current_pin_index = (current_pin_index - 1) % len(POSSIBLE_PINS)
        try_init_pin(POSSIBLE_PINS[current_pin_index])
    
    if io.BUTTON_DOWN in io.pressed:
        current_pin_index = (current_pin_index + 1) % len(POSSIBLE_PINS)
        try_init_pin(POSSIBLE_PINS[current_pin_index])
    
    # Test button
    if io.BUTTON_A in io.pressed:
        send_test_signal()
    
    # Instructions
    screen.brush = brushes.color(201, 209, 217)
    inst1 = "UP/DN: Change pin"
    inst_w1, _ = screen.measure_text(inst1)
    screen.text(inst1, (160 - inst_w1) // 2, 45)
    
    inst2 = "A: Send HOME signal"
    inst_w2, _ = screen.measure_text(inst2)
    screen.text(inst2, (160 - inst_w2) // 2, 60)
    
    inst3 = "Watch your Roku!"
    inst_w3, _ = screen.measure_text(inst3)
    screen.text(inst3, (160 - inst_w3) // 2, 75)
    
    # Test result
    if test_result:
        screen.brush = brushes.color(46, 160, 67) if "OK" in test_result or "Sent" in test_result else brushes.color(248, 81, 73)
        result_w, _ = screen.measure_text(test_result[:25])
        screen.text(test_result[:25], (160 - result_w) // 2, 95)
    
    # Active indicator
    if io.ticks - last_test_time < 500:
        screen.brush = brushes.color(46, 160, 67)
        screen.draw(shapes.circle(80, 110, 5))
    
    return None

# Initialize with first pin
try_init_pin(POSSIBLE_PINS[0])

if __name__ == "__main__":
    run(update)
