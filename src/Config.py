from os.path import dirname, join, abspath

SOURCE_DIR = dirname(abspath(__file__))
DESIGN_DIR = join(SOURCE_DIR, "..", "design")
DATA_DIR = join(SOURCE_DIR, "..", "data")
DB_PATH = join(DATA_DIR, "data.db")

# Window sizes
DEFAULT_WIDTH = 720
DEFAULT_HEIGHT = 540

# Description submenu width
DESCRIPTION_WIDTH = 200

DEFAULT_BG = "#EDEDED"
SHADE = "#DCDCDC"

DEFAULT_PANE_WIDTH = 300

MARGIN = 6
