from types import SimpleNamespace
from pathlib import Path
import sys, json

# base path resolving
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# global configuration

config = json.load(
    open(str(BASE_DIR / "src/client/config.json"), 'r'),
    object_hook=lambda d: SimpleNamespace(**d)
)
