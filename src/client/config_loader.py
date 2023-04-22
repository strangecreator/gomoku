import sys
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# global configuration
import json
from types import SimpleNamespace

config = json.load(
    open(str(BASE_DIR / "src/client/config.json"), 'r'),
    object_hook=lambda d: SimpleNamespace(**d)
)