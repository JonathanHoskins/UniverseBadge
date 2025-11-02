"""Common constants and tiny helpers shared across apps.
These values mirror the badge's screen dimensions, common colors,
and font asset paths used throughout the apps.
"""

# Screen
SCREEN_WIDTH: int = 160
SCREEN_HEIGHT: int = 120

# Colors (RGB tuples)
WHITE: tuple[int, int, int] = (255, 255, 255)
PHOSPHOR: tuple[int, int, int] = (211, 250, 55)
GITHUB_DARK_BG: tuple[int, int, int] = (13, 17, 23)

# Font paths
FONT_NOPE: str = "/system/assets/fonts/nope.ppf"
FONT_ARK: str = "/system/assets/fonts/ark.ppf"
FONT_ZIPLOCK: str = "/system/assets/fonts/ziplock.ppf"
FONT_ABSOLUTE: str = "/system/assets/fonts/absolute.ppf"
FONT_VEST: str = "/system/assets/fonts/vest.ppf"
FONT_IGNORE: str = "/system/assets/fonts/ignore.ppf"
