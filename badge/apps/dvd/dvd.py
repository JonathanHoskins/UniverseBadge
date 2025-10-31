from badgeware import screen, brushes, shapes, io
import random


class DVDLogo:
    def __init__(self):
        self.w = 42
        self.h = 20
        self.x = (screen.width - self.w) // 2
        self.y = (screen.height - self.h) // 2
        # initial velocity
        self.dx = 1
        self.dy = 1
        self.color = (255, 0, 0)

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
        # slightly randomize speed to keep motion interesting
        if abs(self.dx) < 4:
            self.dx += random.choice([-1, 0, 1])
        if abs(self.dy) < 4:
            self.dy += random.choice([-1, 0, 1])

    def draw(self):
        # draw rounded-ish rectangle
        screen.brush = brushes.color(*self.color)
        screen.draw(shapes.rectangle(self.x, self.y, self.w, self.h))

        # draw border
        screen.brush = brushes.color(0, 0, 0)
        screen.draw(shapes.rectangle(self.x, self.y, self.w, 1))
        screen.draw(shapes.rectangle(self.x, self.y + self.h - 1, self.w, 1))

        # draw the text "DVD" centered inside
        screen.font = None  # leave calling module to set font
        w, _ = screen.measure_text("DVD")
        tx = self.x + (self.w - w) // 2
        ty = self.y + (self.h - 8) // 2
        screen.brush = brushes.color(0, 0, 0)
        screen.text("DVD", tx, ty)
