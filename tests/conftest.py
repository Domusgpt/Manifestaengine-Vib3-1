import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.stderr.write(f"Adding {ROOT} to sys.path\n")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
