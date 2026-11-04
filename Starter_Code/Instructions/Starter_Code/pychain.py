"""Keep the original classroom launch command working."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app import main

if __name__ == "__main__":
    main()
