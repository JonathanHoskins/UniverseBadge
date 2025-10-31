import sys
import os

sys.path.insert(0, "/system/apps/camera")
os.chdir("/system/apps/camera")

from badgeware import screen, PixelFont, brushes, shapes, run, io
import math

small_font = PixelFont.load("/system/assets/fonts/nope.ppf")
large_font = PixelFont.load("/system/assets/fonts/ark.ppf")


class Camera:
    def __init__(self):
        # Camera body dimensions (centered on screen)
        self.body_x = 40
        self.body_y = 30
        self.body_w = 80
        self.body_h = 60
        
        # Lens position
        self.lens_x = self.body_x + 25
        self.lens_y = self.body_y + 20
        self.lens_radius = 15
        
        # Animation state
        self.is_shooting = False
        self.shoot_start = 0
        self.aperture_size = 1.0  # 1.0 = fully open, 0.0 = fully closed
        
        # Flash state
        self.flash_alpha = 0
        
        # Animation timings (in milliseconds)
        self.close_duration = 100   # aperture closes in 100ms
        self.closed_duration = 50   # stays closed for 50ms
        self.open_duration = 150    # aperture opens in 150ms
        self.total_duration = self.close_duration + self.closed_duration + self.open_duration
        
    def trigger_shoot(self):
        """Start the camera shooting animation"""
        if not self.is_shooting:
            self.is_shooting = True
            self.shoot_start = io.ticks
    
    def update(self):
        """Update animation state"""
        if self.is_shooting:
            elapsed = io.ticks - self.shoot_start
            
            if elapsed < self.close_duration:
                # Closing phase
                progress = elapsed / self.close_duration
                self.aperture_size = 1.0 - progress
                self.flash_alpha = int(progress * 255)
            elif elapsed < self.close_duration + self.closed_duration:
                # Fully closed phase
                self.aperture_size = 0.0
                self.flash_alpha = 255
            elif elapsed < self.total_duration:
                # Opening phase
                progress = (elapsed - self.close_duration - self.closed_duration) / self.open_duration
                self.aperture_size = progress
                self.flash_alpha = int((1.0 - progress) * 255)
            else:
                # Animation complete
                self.is_shooting = False
                self.aperture_size = 1.0
                self.flash_alpha = 0
    
    def draw(self):
        """Draw the vintage 35mm camera"""
        # Camera body (main rectangle)
        screen.brush = brushes.color(60, 60, 70)
        screen.draw(shapes.rounded_rectangle(
            self.body_x, self.body_y, self.body_w, self.body_h, 4
        ))
        
        # Camera body highlight
        screen.brush = brushes.color(80, 80, 90)
        screen.draw(shapes.rounded_rectangle(
            self.body_x + 2, self.body_y + 2, self.body_w - 4, 8, 2
        ))
        
        # Viewfinder window
        screen.brush = brushes.color(40, 40, 50)
        screen.draw(shapes.rounded_rectangle(
            self.body_x + 55, self.body_y + 8, 18, 12, 2
        ))
        
        # Film advance lever
        screen.brush = brushes.color(80, 80, 90)
        screen.draw(shapes.rounded_rectangle(
            self.body_x + self.body_w - 12, self.body_y + 5, 8, 15, 2
        ))
        
        # Lens outer ring
        screen.brush = brushes.color(40, 40, 45)
        screen.draw(shapes.circle(self.lens_x, self.lens_y, self.lens_radius + 3))
        
        # Lens middle ring
        screen.brush = brushes.color(30, 30, 35)
        screen.draw(shapes.circle(self.lens_x, self.lens_y, self.lens_radius))
        
        # Lens glass with aperture effect
        if self.aperture_size > 0:
            # Draw aperture blades (hexagonal iris effect)
            aperture_radius = int(self.lens_radius * self.aperture_size * 0.7)
            if aperture_radius > 2:
                # Lens glass (dark blue tint)
                screen.brush = brushes.color(20, 30, 50)
                screen.draw(shapes.circle(self.lens_x, self.lens_y, aperture_radius))
                
                # Lens reflection
                screen.brush = brushes.color(60, 80, 120, 150)
                screen.draw(shapes.circle(self.lens_x - 3, self.lens_y - 3, aperture_radius // 2))
        
        # Flash bulb
        flash_x = self.body_x + 8
        flash_y = self.body_y + 8
        screen.brush = brushes.color(100, 100, 110)
        screen.draw(shapes.rounded_rectangle(flash_x, flash_y, 12, 8, 2))
        
        # Flash reflection when firing
        if self.flash_alpha > 0:
            screen.brush = brushes.color(255, 255, 200, self.flash_alpha)
            screen.draw(shapes.rounded_rectangle(flash_x + 1, flash_y + 1, 10, 6, 2))
        
        # Shutter button
        screen.brush = brushes.color(180, 40, 40) if not self.is_shooting else brushes.color(120, 20, 20)
        screen.draw(shapes.circle(self.body_x + self.body_w - 15, self.body_y - 3, 5))
        
        # Brand text on body
        screen.font = small_font
        screen.brush = brushes.color(200, 200, 200)
        screen.text("MONA", self.body_x + 28, self.body_y + 50)
        screen.text("35mm", self.body_x + 30, self.body_y + 57)
        
    def draw_flash_overlay(self):
        """Draw full-screen flash effect"""
        if self.flash_alpha > 30:
            screen.brush = brushes.color(255, 255, 255, self.flash_alpha)
            screen.draw(shapes.rectangle(0, 0, 160, 120))


camera = Camera()
photo_count = 0


def update():
    global photo_count
    
    # Clear screen
    screen.brush = brushes.color(20, 25, 30)
    screen.draw(shapes.rectangle(0, 0, 160, 120))
    
    # Handle input
    if io.BUTTON_DOWN in io.pressed:
        camera.trigger_shoot()
        photo_count += 1
    
    # Update camera animation
    camera.update()
    
    # Draw camera
    camera.draw()
    
    # Draw flash overlay on top
    camera.draw_flash_overlay()
    
    # Draw instructions
    screen.font = small_font
    if int(io.ticks / 500) % 2:
        screen.brush = brushes.color(180, 180, 180)
        text = "Press DOWN to shoot"
        w, _ = screen.measure_text(text)
        screen.text(text, 80 - (w // 2), 105)
    
    # Draw photo counter
    screen.font = large_font
    screen.brush = brushes.color(211, 250, 55)
    counter_text = f"Photos: {photo_count}"
    w, _ = screen.measure_text(counter_text)
    screen.text(counter_text, 80 - (w // 2), 5)
    
    return None


if __name__ == "__main__":
    run(update)
