"""
Test stubs for the 'badgeware' API used by apps so we can run smoke tests
on desktop Python without hardware or asset files.
"""
from types import SimpleNamespace


class _Screen:
    def __init__(self):
        self.width = 160
        self.height = 120
        self.brush = None
        self.font = None

    def draw(self, _shape):
        # no-op for tests
        return None

    def clear(self):
        return None

    def text(self, _text: str, _x: int, _y: int):
        return None

    def measure_text(self, text: str):
        # simple fixed-size metrics
        return (max(0, len(text)) * 6, 10)

    def blit(self, _img, _x: int, _y: int):
        return None

    def scale_blit(self, _img, _x: int, _y: int, _w: int, _h: int):
        return None


def _color(r, g=None, b=None, a=255):
    # Accept either (r,g,b[,a]) or grayscale style when only 'r' provided
    if g is None and b is None:
        g = b = r
    return (int(r), int(g), int(b), int(a))


class _Shapes:
    class _Shape:
        def __init__(self, *args, **kwargs):
            self.transform = SimpleNamespace(scale=lambda x, y: self, translate=lambda x, y: self)

    def rectangle(self, *args, **kwargs):
        return self._Shape()

    def rounded_rectangle(self, *args, **kwargs):
        return self._Shape()

    def circle(self, *args, **kwargs):
        return self._Shape()

    def pie(self, *args, **kwargs):
        return self._Shape()

    def squircle(self, *args, **kwargs):
        return self._Shape()


class _Image:
    def __init__(self, width=24, height=24):
        self.width = width
        self.height = height
        self.alpha = 255

    @classmethod
    def load(cls, _path: str):
        # Heuristic sizes for a couple known assets; otherwise default 24x24
        name = _path.lower()
        if "background" in name:
            return cls(160, 120)
        if "grass" in name:
            return cls(160, 16)
        if "cloud" in name:
            return cls(64, 24)
        if name.endswith("icon.png"):
            return cls(24, 24)
        return cls()


class _SpriteSheet:
    def __init__(self, _path: str, _cols: int, _rows: int):
        self._path = _path
        self._cols = _cols
        self._rows = _rows

    def animation(self):
        # Return an object with a no-op draw
        class _Anim:
            def draw(self, *args, **kwargs):
                return None

        return _Anim()


class _PixelFont:
    @classmethod
    def load(cls, _path: str):
        return SimpleNamespace(path=_path)


class _Matrix:
    def __init__(self):
        pass

    def translate(self, *_):
        return self

    def scale(self, *_):
        return self


class _IO:
    # simple input/timer mock
    BUTTON_A = 1
    BUTTON_B = 2
    BUTTON_C = 3
    BUTTON_UP = 4
    BUTTON_DOWN = 5
    pressed = set()
    ticks = 0


def is_dir(_path: str) -> bool:
    # We can safely say false to avoid filesystem work during tests
    return False


def file_exists(_path: str) -> bool:
    # Similarly, pretend files don't exist; apps should handle fallbacks
    return False


def run(update_fn):
    # Just invoke a single update for smoke testing
    try:
        return update_fn()
    finally:
        # Increment ticks a little to let blink logic move forward
        _IO.ticks += 100


# Public API objects
screen = _Screen()
brushes = SimpleNamespace(color=_color)
shapes = _Shapes()
Image = _Image
SpriteSheet = _SpriteSheet
PixelFont = _PixelFont
Matrix = _Matrix
io = _IO
