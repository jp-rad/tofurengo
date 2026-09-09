from pathlib import Path

# Load code/GLYPH-TAG-SPECS.ja.md
_spec_path = Path(__file__).parents[3] / "GLYPH-TAG-SPECS.ja.md"

if _spec_path.exists():
    __doc__ = _spec_path.read_text(encoding="utf-8")
else:
    __doc__ = "# GLYPH-TAG-SPECS\n\nFile not found."
