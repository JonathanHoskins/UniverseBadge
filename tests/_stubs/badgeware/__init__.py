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

    def window(self, _x, _y, _w, _h):
        # Return a lightweight view with same API
        view = _Screen()
        view.width = _w
        view.height = _h
        return view

    def load_into(self, _filename: str):
        # No-op for tests
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

    def line(self, *args, **kwargs):
        return self._Shape()


class _Image:
    def __init__(self, width=24, height=24):
        self.width = width
        self.height = height
        self.alpha = 255
    # Provide antialias constant used by some apps
    X2 = 2

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

    def animation(self, start_x: int = 0, start_y: int = 0, count: int | None = None):
        """Return a lightweight animation object.

        Some apps call animation() with (start_x, start_y, count). We only need to
        support .frame(i) and .count() for smoke tests.
        """

        class _Anim:
            def __init__(self, _count: int | None):
                # default to 1 if unknown; tests only check type/availability
                self._count = _count if _count is not None else 1

            def frame(self, _i: int):
                # Return a simple sprite image; size is arbitrary for tests
                return _Image(16, 16)

            def count(self) -> int:
                return int(self._count)

            def draw(self, *args, **kwargs):
                # Some apps might try to call draw on the animation
                return None

        return _Anim(count)

    def sprite(self, _x: int, _y: int):
        # Return a simple image-like object
        img = _Image(16, 16)
        return img


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
    held = set()
    ticks = 0
    ticks_delta = 100

    @staticmethod
    def poll():
        # no-op in tests
        return None


def is_dir(_path: str) -> bool:
    # We can safely say false to avoid filesystem work during tests
    return False


def file_exists(_path: str) -> bool:
    # Similarly, pretend files don't exist; apps should handle fallbacks
    return False


def get_battery_level() -> float:
    # Return a mock battery level (0.0 to 1.0)
    return 0.85


def run(update_fn):
    # Just invoke a single update for smoke testing
    try:
        return update_fn()
    finally:
        # Increment ticks a little to let blink logic move forward
        _IO.ticks_delta = 100
        _IO.ticks += _IO.ticks_delta


class _Display:
    @staticmethod
    def update():
        return None


class _State:
    _store = {}

    @classmethod
    def load(cls, key: str, obj):
        data = cls._store.get(key)
        if isinstance(obj, dict):
            if data and isinstance(data, dict):
                obj.update(data)
        return True

    @classmethod
    def save(cls, key: str, obj):
        cls._store[key] = obj
        return True


# Public API objects
screen = _Screen()
brushes = SimpleNamespace(color=_color)
shapes = _Shapes()
Image = _Image
SpriteSheet = _SpriteSheet
PixelFont = _PixelFont
Matrix = _Matrix
io = _IO
display = _Display
State = _State
