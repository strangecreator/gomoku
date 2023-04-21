import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# global configuration
import json
from types import SimpleNamespace

config = json.load(
    open(str(Path(BASE_DIR, "config.json")), 'r'),
    object_hook=lambda d: SimpleNamespace(**d)
)