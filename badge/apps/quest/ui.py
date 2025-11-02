"""UI helpers for the Quest app.

Renders the status header and a 3x3 grid of quest tiles with animated borders.
Functions are pure drawing helpers using the global screen.
"""

from __future__ import annotations

import math
from typing import List
from badgeware import *
from badge.common import FONT_IGNORE, FONT_ARK

screen.antialias = Image.X2

mona = Image.load("assets/mona.png")
large_font = PixelFont.load(FONT_IGNORE)
small_font = PixelFont.load(FONT_ARK)

tile_colors = [
  None,
  brushes.color(3, 58, 22),
  brushes.color(25, 108, 46),
  brushes.color(46, 160, 67),
  brushes.color(46, 160, 67),
  brushes.color(86, 211, 100),
  brushes.color(3, 58, 22),
  brushes.color(25, 108, 46),
  brushes.color(46, 160, 67),
  brushes.color(25, 108, 46),
]

def draw_status(complete: List[int]) -> None:
  """Draw the status header showing completed count."""
  screen.blit(mona, 0, 72)
  screen.font = small_font
  screen.brush = brushes.color(255, 255, 255)
  screen.text("mona's quest", 65, 0)

  screen.font = large_font
  screen.text(f"{len(complete)}/9", 5, 8)
  screen.font = small_font
  screen.brush = brushes.color(140, 160, 180)
  screen.text("found", 7, 30)


def draw_tiles(complete: List[int]) -> None:
  """Draw the 3x3 tile grid and fill completed tiles."""
  # define tile shape and set position of tile grid
  tile = shapes.squircle(0, 0, 1, 6)
  pos = (70, 31)
  screen.font = large_font

  for y in range(0, 3):
    for x in range(0, 3):
      # animate the inactive tile borders
      pulse = (math.sin(io.ticks / 250 + (x + y)) / 2) + 0.5
      pulse = 0.8 + (pulse / 2)

      # tile label
      index = x + (y * 3) + 1
      label = str(index)

      # determine centre point of tile
      xo, yo = x * 34, y * 34

      # calculate label position in tile
      label_pos = (xo + pos[0] - 6, yo + pos[1] - 15)

      if index in complete:
        screen.brush = tile_colors[index]
        tile.transform = Matrix().translate(*pos).translate(xo, yo).scale(16)
        screen.draw(tile)
        screen.brush = brushes.color(255, 255, 255, 150 * pulse)
        screen.text(label, *label_pos)
      else:
        border_brush = brushes.color(50 * pulse, 60 * pulse, 70 * pulse)
        tile.transform = Matrix().translate(*pos).translate(xo, yo).scale(16)
        screen.brush = border_brush
        screen.draw(tile)
        screen.brush = brushes.color(21, 27, 35)
        tile.transform = Matrix().translate(*pos).translate(xo, yo).scale(14)
        screen.draw(tile)
        screen.brush = border_brush
        screen.text(label, *label_pos)
