import os
import sys
import argparse
from pathlib import Path

# base path resolving
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--interface",
    nargs='?',
    choices=["console", "GUI"],
    help="Specify the type of interface. Available options: [console, GUI]",
    type=str,
    required=True,
    dest="interface"
)

args = parser.parse_args()

# launch the defined interface
if args.interface == "console":
    path_to_file = BASE_DIR / "client/interfaces/console/console.py"
    os.system(f'{sys.executable} {path_to_file}')
elif args.interface == "GUI":
    os.system(f'{sys.executable} {BASE_DIR / "client/interfaces/GUI/gui.py"}')
