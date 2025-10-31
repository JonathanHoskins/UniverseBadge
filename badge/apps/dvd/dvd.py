from badgeware import screen, brushes, shapes, SpriteSheet
import random
import os


class DVDLogo:
    def __init__(self):
        self.w = 48  # width
        self.h = 24  # height (taller in middle)
        # use floats for smoother, slower motion
        self.x = float((screen.width - self.w) // 2)
        self.y = float((screen.height - self.h) // 2)
        # initial velocity (slower)
        self.dx = 0.6 * (1 if random.choice([True, False]) else -1)
        self.dy = 0.6 * (1 if random.choice([True, False]) else -1)
        self.color = (255, 0, 0)
        # try to load a sprite-based logo (assets/dvd_logo.png) as a 1x1 spritesheet
        self.sprite = None
        try:
            asset_path = os.path.join(os.getcwd(), "assets", "dvd_logo.png")
            # prefer a local app asset first
            if os.path.exists(asset_path):
                self.sprite = SpriteSheet("assets/dvd_logo.png", 1, 1)
            else:
                # fallback to system asset if present
                if os.path.exists("/system/assets/mona-sprites/mona-default.png"):
                    self.sprite = SpriteSheet("/system/assets/mona-sprites/mona-default.png", 1, 1)
        except Exception:
            # if sprite loading fails, we'll just draw the rectangle/text fallback
            self.sprite = None

    def update(self):
        # move
        self.x += self.dx
        self.y += self.dy

        bounced = False
        # bounce on horizontal edges
        if self.x <= 0:
            self.x = 0
            self.dx = abs(self.dx)
            bounced = True
        if self.x + self.w >= screen.width:
            self.x = screen.width - self.w
            self.dx = -abs(self.dx)
            bounced = True

        # bounce on vertical edges
        if self.y <= 0:
            self.y = 0
            self.dy = abs(self.dy)
            bounced = True
        if self.y + self.h >= screen.height:
            self.y = screen.height - self.h
            self.dy = -abs(self.dy)
            bounced = True

        if bounced:
            self._on_bounce()

    def _on_bounce(self):
        # change color randomly on bounce
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        # slightly randomize speed to keep motion interesting but stay slow
        def clamp(v, lo=0.3, hi=2.0):
            sign = 1 if v >= 0 else -1
            return sign * max(lo, min(abs(v) + random.choice([-0.2, 0, 0.2]), hi))

        self.dx = clamp(self.dx)
        self.dy = clamp(self.dy)

    def draw(self):
        if self.sprite:
            try:
                img = self.sprite.sprite(0, 0)
                # center the sprite inside the logo bounds
                sx = int(round(self.x + (self.w - img.width) / 2))
                sy = int(round(self.y + (self.h - img.height) / 2))
                screen.blit(img, sx, sy)
                return
            except Exception:
                # fall through to rectangle fallback
                pass
        # draw rounded rectangle fallback with a subtle border
        rx = int(round(self.x))
        ry = int(round(self.y))
        rw = int(self.w)
        rh = int(self.h)
        
        # Draw perfect oval shape
        screen.brush = brushes.color(*self.color)
        
        # Main oval using maximum corner radius
        radius = rh // 2  # half height for perfect oval ends
        screen.draw(shapes.rounded_rectangle(rx, ry, rw, rh, radius))
        
        # Draw a thin border for depth
        border_width = 2
        screen.brush = brushes.color(0, 0, 0)
        screen.draw(shapes.rounded_rectangle(
            rx,
            ry,
            rw,
            border_width,
            radius
        ))
        screen.draw(shapes.rounded_rectangle(
            rx,
            ry + rh - border_width,
            rw,
            border_width,
            radius
        ))

        # draw the text "DVD" centered inside
        # do not override font; calling module should set the font
        w, _ = screen.measure_text("DVD")
        tx = rx + (rw - w) // 2
        ty = ry + (rh - 8) // 2 - 2  # moved up slightly to fit in bat shape
        screen.brush = brushes.color(0, 0, 0)
        screen.text("DVD", tx, ty)
