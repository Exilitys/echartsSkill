"""Repository and compatibility tests; not required to use the skill."""

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent / "skills" / "echarts-json"
# Agent skill directories use hyphenated names; expose their standalone helpers to tests.
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
