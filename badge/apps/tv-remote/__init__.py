import sys

# Add the app directory to the path to allow local imports
sys.path.insert(0, "/system/apps/tv-remote")

from badgeware import screen, PixelFont, shapes, brushes, io, run
from aye_arr.nec import NECSender
from remote import TVRemote

# Pin configuration for IR transmitter
# Note: Badge has IR receiver on pin 21. Transmitter pin needs verification.
# Try pin 20 first (common adjacent pin), but may need adjustment for your badge model.
# If not working, try: 22, 19, or check your badge's hardware documentation.
IR_TX_PIN = 20  # IR transmitter pin on the badge (VERIFY THIS FOR YOUR MODEL)

# Load font
font = PixelFont.load("/system/assets/fonts/nope.ppf")

# GitHub color scheme
BG_COLOR = (13, 17, 23)      # Dark background
TEXT_COLOR = (201, 209, 217) # Light text
BUTTON_COLOR = (48, 54, 61)  # Button background
HIGHLIGHT_COLOR = (88, 166, 255)  # Selected button
ACTIVE_COLOR = (46, 160, 67) # Active/pressed state
ERROR_COLOR = (248, 81, 73)  # Error state

# Button layout - Now includes INPUT and MENU
BUTTONS = [
    {"label": "PWR", "code": "POWER", "x": 10, "y": 25},
    {"label": "MENU", "code": "MENU", "x": 60, "y": 25},
    {"label": "INPUT", "code": "INPUT", "x": 110, "y": 25},
    {"label": "CH+", "code": "CHANNEL_UP", "x": 10, "y": 45},
    {"label": "CH-", "code": "CHANNEL_DOWN", "x": 10, "y": 65},
    {"label": "VOL+", "code": "VOLUME_UP", "x": 110, "y": 45},
    {"label": "VOL-", "code": "VOLUME_DOWN", "x": 110, "y": 65},
    {"label": "MUTE", "code": "MUTE", "x": 60, "y": 85},
]

# State
selected_button = 0
last_send_time = 0
send_cooldown = 300  # milliseconds between sends
init_error = None

# Initialize IR sender
sender = None
tv_remote = None

def init():
    global sender, tv_remote, init_error
    try:
        sender = NECSender(IR_TX_PIN, 0, 0)  # pin, PIO, state machine
        sender.start()
        tv_remote = TVRemote()
        print(f"IR Sender initialized on pin {IR_TX_PIN}")
        print(f"Using Sony TV codes - Address: 0x{tv_remote.ADDRESS:02X}")
    except Exception as e:
        init_error = str(e)
        print(f"Error initializing IR sender: {e}")
        print(f"Check that pin {IR_TX_PIN} is correct for your badge model")

def draw_button(x, y, width, height, label, is_selected, is_active):
    # Choose color based on state
    if is_active:
        color = ACTIVE_COLOR
    elif is_selected:
        color = HIGHLIGHT_COLOR
    else:
        color = BUTTON_COLOR
    
    # Draw button background
    screen.brush = brushes.color(*color)
    screen.draw(shapes.rectangle(x, y, width, height))
    
    # Draw button label
    screen.brush = brushes.color(*TEXT_COLOR)
    screen.font = font
    text_width, text_height = screen.measure_text(label)
    screen.text(label, x + (width - text_width) // 2, y + (height - text_height) // 2)

def send_ir_code(code_name):
    global last_send_time
    if sender and tv_remote:
        try:
            sender.send_remote(tv_remote, code_name)
            last_send_time = io.ticks
        except Exception as e:
            print(f"Error sending IR code: {e}")

def update():
    global selected_button, last_send_time
    
    # Clear the screen
    screen.brush = brushes.color(*BG_COLOR)
    screen.clear()
    
    # Draw title
    screen.brush = brushes.color(*TEXT_COLOR)
    screen.font = font
    title = "SONY TV REMOTE"
    title_width, _ = screen.measure_text(title)
    screen.text(title, (160 - title_width) // 2, 2)
    
    # Show initialization error if present
    if init_error:
        screen.brush = brushes.color(*ERROR_COLOR)
        error_msg = "INIT ERROR"
        error_width, _ = screen.measure_text(error_msg)
        screen.text(error_msg, (160 - error_width) // 2, 50)
        
        # Show abbreviated error message
        screen.brush = brushes.color(*TEXT_COLOR)
        err_short = init_error[:20] if len(init_error) > 20 else init_error
        err_w, _ = screen.measure_text(err_short)
        screen.text(err_short, (160 - err_w) // 2, 65)
        
        # Show instructions
        instructions = "Check IR TX pin"
        inst_width, _ = screen.measure_text(instructions)
        screen.text(instructions, (160 - inst_width) // 2, 105)
        return None
    
    # Handle button navigation
    if io.BUTTON_UP in io.pressed and selected_button > 0:
        selected_button -= 1
    elif io.BUTTON_DOWN in io.pressed and selected_button < len(BUTTONS) - 1:
        selected_button += 1
    
    # Check if we're in cooldown period
    time_since_send = io.ticks - last_send_time
    is_active = time_since_send < send_cooldown
    
    # Send IR signal when A button is pressed (and not in cooldown)
    if io.BUTTON_A in io.pressed and not is_active:
        button_info = BUTTONS[selected_button]
        send_ir_code(button_info["code"])
    
    # Draw all buttons
    for i, button in enumerate(BUTTONS):
        is_selected = (i == selected_button)
        is_button_active = is_active and is_selected
        draw_button(button["x"], button["y"], 40, 15, button["label"], is_selected, is_button_active)
    
    # Draw status info
    screen.brush = brushes.color(*TEXT_COLOR)
    screen.font = font
    status = f"Addr:0x{tv_remote.ADDRESS:02X}" if tv_remote else "No remote"
    status_width, _ = screen.measure_text(status)
    screen.text(status, (160 - status_width) // 2, 100)
    
    # Draw instructions
    instructions = "UP/DN:Select A:Send"
    inst_width, _ = screen.measure_text(instructions)
    screen.text(instructions, (160 - inst_width) // 2, 110)
    
    return None

def on_exit():
    # Clean up IR sender if needed
    pass

if __name__ == "__main__":
    init()
    run(update)
