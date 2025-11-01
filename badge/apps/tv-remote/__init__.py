import sys

# Add the app directory to the path to allow local imports
sys.path.insert(0, "/system/apps/tv-remote")

from badgeware import screen, PixelFont, shapes, brushes, io, run
from aye_arr.nec import NECSender
from remote import TVRemote

# Pin configuration for IR transmitter
IR_TX_PIN = 20  # IR transmitter pin on the badge

# Load font
font = PixelFont.load("/system/assets/fonts/nope.ppf")

# GitHub color scheme
BG_COLOR = (13, 17, 23)      # Dark background
TEXT_COLOR = (201, 209, 217) # Light text
BUTTON_COLOR = (48, 54, 61)  # Button background
HIGHLIGHT_COLOR = (88, 166, 255)  # Selected button
ACTIVE_COLOR = (46, 160, 67) # Active/pressed state

# Button layout
BUTTONS = [
    {"label": "PWR", "code": "POWER", "x": 60, "y": 10},
    {"label": "CH+", "code": "CHANNEL_UP", "x": 10, "y": 30},
    {"label": "CH-", "code": "CHANNEL_DOWN", "x": 10, "y": 50},
    {"label": "VOL+", "code": "VOLUME_UP", "x": 110, "y": 30},
    {"label": "VOL-", "code": "VOLUME_DOWN", "x": 110, "y": 50},
    {"label": "MUTE", "code": "MUTE", "x": 60, "y": 70},
]

# State
selected_button = 0
last_send_time = 0
send_cooldown = 300  # milliseconds between sends

# Initialize IR sender
sender = None
tv_remote = None

def init():
    global sender, tv_remote
    try:
        sender = NECSender(IR_TX_PIN, 0, 0)  # pin, PIO, state machine
        sender.start()
        tv_remote = TVRemote()
    except Exception as e:
        print(f"Error initializing IR sender: {e}")

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
    title = "TV REMOTE"
    title_width, _ = screen.measure_text(title)
    screen.text(title, (160 - title_width) // 2, 2)
    
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
    
    # Draw instructions
    screen.brush = brushes.color(*TEXT_COLOR)
    screen.font = font
    instructions = "UP/DN: Select  A: Send"
    inst_width, _ = screen.measure_text(instructions)
    screen.text(instructions, (160 - inst_width) // 2, 105)
    
    return None

def on_exit():
    # Clean up IR sender if needed
    pass

if __name__ == "__main__":
    init()
    run(update)
