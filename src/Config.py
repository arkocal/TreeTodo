from os.path import dirname, join, abspath
from logging import warning

import configparser

SOURCE_DIR = dirname(abspath(__file__))
DESIGN_DIR = join(SOURCE_DIR, "..", "design")
DATA_DIR = join(SOURCE_DIR, "..", "data")
DB_PATH = join(DATA_DIR, "data.db")
CONFIG_PATH = join(DATA_DIR, "treetodo.conf")

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

def get_config_with_warning(section, option, fallback):
    """Get config and warn if fallback value is used."""
    try:
        return config.get(section, option)
    except configparser.NoSectionError as err:
        warning(("Corrupted config file, missing section {}. " +
              "Using default values").format(section))
        return fallback
    except configparser.NoOptionError as err:
        warning((("Corrupted config file, missing option {}. " +
              "Using default value {}").format(option, fallback)))
        return fallback

# Window sizes
DEFAULT_WIDTH = int(get_config_with_warning("window", "Width", 720))
DEFAULT_HEIGHT = int(get_config_with_warning("window", "Height", 540))

# Description submenu width
DESCRIPTION_WIDTH = int(get_config_with_warning("ui", "DescriptionWidth", 200))
DEFAULT_PANE_WIDTH = int(get_config_with_warning("ui", "PaneWidth", 300)) 
MARGIN = int(get_config_with_warning("ui", "Margin", 6))

DEFAULT_BG = get_config_with_warning("color", "DefaultBg", "#EDEDED")
SHADE = get_config_with_warning("color", "Shade", "#DCDCDC")


