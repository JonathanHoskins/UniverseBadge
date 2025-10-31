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
cx, cy = GW // 2, GH // 2
r = min(GW, GH) // 2 - 3

# Outer circle
dg.ellipse([cx - r, cy - r, cx + r, cy + r], outline=white, width=2)

# Equator (straight line)
dg.line([(cx - (r - 2), cy), (cx + (r - 2), cy)], fill=white, width=1)

# Latitudes (curved): draw two horizontal ellipses with reduced height
for frac in (0.55, 0.25):
    h = max(1, int(r * frac))
    dg.ellipse([cx - r, cy - h, cx + r, cy + h], outline=white, width=1)

# Longitudes (curved): draw two vertical ellipses with reduced width
for frac in (0.55, 0.25):
    w = max(1, int(r * frac))
    dg.ellipse([cx - w, cy - r, cx + w, cy + r], outline=white, width=1)

globe.save(hello_out)
print(f"Wrote hello menu icon to {hello_out}")

# (Removed text-based hello icon generation; globe icon above is the final output.)
