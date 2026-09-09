from pathlib import Path

# Load code/README.md
_readme_path = Path(__file__).parents[3] / "README.md"

if _readme_path.exists():
    __doc__ = _readme_path.read_text(encoding="utf-8")
else:
    __doc__ = "# README\n\nFile not found."
