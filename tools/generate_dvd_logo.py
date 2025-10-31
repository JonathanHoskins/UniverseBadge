from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "badge" / "apps" / "dvd" / "assets"
out.mkdir(parents=True, exist_ok=True)
img_path = out / "dvd_logo.png"
icon_out = Path(__file__).resolve().parents[1] / "badge" / "apps" / "dvd" / "icon.png"

# create a small transparent image with "DVD" text
W, H = 40, 18
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# simple background rounded rectangle
bg_color = (255, 50, 50, 255)
radius = 3
# draw rounded rect manually
for y in range(H):
    for x in range(W):
        # simple distance from corners to create rounded effect
        if ((x < radius and y < radius and (x - radius) ** 2 + (y - radius) ** 2 > radius ** 2) or
            (x < radius and y >= H - radius and (x - radius) ** 2 + (y - (H - radius)) ** 2 > radius ** 2) or
            (x >= W - radius and y < radius and (x - (W - radius)) ** 2 + (y - radius) ** 2 > radius ** 2) or
            (x >= W - radius and y >= H - radius and (x - (W - radius)) ** 2 + (y - (H - radius)) ** 2 > radius ** 2)):
            # skip corner pixels
            continue
        img.putpixel((x, y), bg_color)

# draw DVD text in center using default font
try:
    font = ImageFont.truetype("arial.ttf", 10)
except Exception:
    font = ImageFont.load_default()

text = "DVD"
# robust text size calculation across Pillow versions
try:
    # Pillow >= 8: font.getbbox
    bbox = font.getbbox(text)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
except Exception:
    try:
        # ImageDraw.textbbox
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        try:
            # fallback to mask size
            w, h = font.getmask(text).size
        except Exception:
            w, h = 10, 8

tx = (W - w) // 2
ty = (H - h) // 2
# draw shadow
d.text((tx+1, ty+1), text, font=font, fill=(0,0,0,255))
d.text((tx, ty), text, font=font, fill=(255,255,255,255))

img.save(img_path)
print(f"Wrote sample DVD logo to {img_path}")

# Also generate a 24px-tall monochrome icon for the menu (icon.png)
IW, IH = 36, 24  # width x height; menu expects 24px tall, width is flexible
icon = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
di = ImageDraw.Draw(icon)

# Draw a thin white oval (ellipse outline)
pad = 2
di.ellipse([pad, pad + 2, IW - pad - 1, IH - pad - 3], outline=(255, 255, 255, 255), width=2)

# Draw white 'DVD' text centered
try:
    ifont = ImageFont.truetype("arial.ttf", 12)
except Exception:
    ifont = ImageFont.load_default()

text = "DVD"
try:
    bbox = ifont.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
except Exception:
    try:
        bbox = di.textbbox((0, 0), text, font=ifont)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        try:
            tw, th = ifont.getmask(text).size
        except Exception:
            tw, th = 14, 10

tx = (IW - tw) // 2
ty = (IH - th) // 2
di.text((tx, ty), text, font=ifont, fill=(255, 255, 255, 255))

icon.save(icon_out)
print(f"Wrote menu icon to {icon_out}")

# Generate a 24px-tall monochrome globe icon for the hello app (icon.png)
hello_out = Path(__file__).resolve().parents[1] / "badge" / "apps" / "hello" / "icon.png"
GW, GH = 36, 24
globe = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
dg = ImageDraw.Draw(globe)

white = (255, 255, 255, 255)
pad = 2

# Outer circle
dg.ellipse([pad, pad, GW - pad - 1, GH - pad - 1], outline=white, width=2)

# Horizontal latitude lines (top, middle, bottom-ish)
mid_y = GH // 2
dg.line([(pad + 3, mid_y), (GW - pad - 3, mid_y)], fill=white, width=2)
dg.line([(pad + 5, mid_y - 5), (GW - pad - 5, mid_y - 5)], fill=white, width=2)
dg.line([(pad + 5, mid_y + 5), (GW - pad - 5, mid_y + 5)], fill=white, width=2)

# Vertical longitude lines (left and right of center)
mid_x = GW // 2
dg.line([(mid_x - 6, pad + 4), (mid_x - 6, GH - pad - 4)], fill=white, width=2)
dg.line([(mid_x + 6, pad + 4), (mid_x + 6, GH - pad - 4)], fill=white, width=2)

globe.save(hello_out)
print(f"Wrote hello menu icon to {hello_out}")

# Generate a matching 24px-tall monochrome icon for the hello app (icon.png)
hello_icon_out = Path(__file__).resolve().parents[1] / "badge" / "apps" / "hello" / "icon.png"

# Utility: try to load a truetype font at or below a target size so that text fits width
def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, start_size: int = 12, min_size: int = 6):
    size = start_size
    while size >= min_size:
        try:
            f = ImageFont.truetype("arial.ttf", size)
        except Exception:
            # Fallback to default bitmap font and break
            return ImageFont.load_default()
        try:
            bbox = f.getbbox(text)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            try:
                bbox = draw.textbbox((0, 0), text, font=f)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception:
                tw, th = max_width + 1, 10
        if tw <= max_width:
            return f
        size -= 1
    return ImageFont.load_default()

IW2, IH2 = 36, 24
hello_icon = Image.new("RGBA", (IW2, IH2), (0, 0, 0, 0))
dh = ImageDraw.Draw(hello_icon)

# White oval outline, consistent with the DVD icon style
pad = 2
dh.ellipse([pad, pad + 2, IW2 - pad - 1, IH2 - pad - 3], outline=(255, 255, 255, 255), width=2)

# Centered text ("HELLO"), scaled to fit if needed
hello_text = "HELLO"
font = fit_font(dh, hello_text, max_width=IW2 - 6, start_size=12, min_size=6)
try:
    bbox = font.getbbox(hello_text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
except Exception:
    try:
        bbox = dh.textbbox((0, 0), hello_text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = 20, 10

tx = (IW2 - tw) // 2
ty = (IH2 - th) // 2
dh.text((tx, ty), hello_text, font=font, fill=(255, 255, 255, 255))

hello_icon.save(hello_icon_out)
print(f"Wrote menu icon to {hello_icon_out}")
