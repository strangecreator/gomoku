import os, sys, platform
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from game_logic.main import State


class ConsoleOnlineInterface:
    pass