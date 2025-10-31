from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "badge" / "apps" / "dvd" / "assets"
out.mkdir(parents=True, exist_ok=True)
img_path = out / "dvd_logo.png"

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
