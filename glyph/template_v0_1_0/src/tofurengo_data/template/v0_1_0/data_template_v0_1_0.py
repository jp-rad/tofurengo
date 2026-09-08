"""
Dataset module template for tofurengo glyph mappings.

This module provides a dataset mapping table (`GLYPH_TABLE`) and versioning metadata
(`VERSION`). It serves as a standard template for dataset packages consumed by the
`tofurengo` library.

Attributes:
    VERSION (str): Dataset version identifier (e.g., '0.1.0').
    GLYPH_TABLE (dict[str, dict[str, str | bool]]): Dictionary mapping unique glyph
        identifiers (e.g., 'MJ000001') to their respective character properties:
        - `b` (str): Base UCS code point sequence (e.g., 'U+845B').
        - `v` (str): Variation code point sequence, including IVS/VS if present (e.g., 'U+845B U+E0102').
        - `active` (bool): Active status indicator (`True` if active, `False` if archived).
"""

VERSION: str = "0.1.0"

GLYPH_TABLE: dict[str, dict[str, str | bool]] = {
    "MJ000001": {"v": "U+3005", "b": "U+3005", "active": True},
    "MJ000012": {"v": "U+2CF1C", "b": "U+2CF1C", "active": False},
    "MJ000013": {"v": "U+3416", "b": "U+3416", "active": False},
    "MJ022336": {"v": "U+845B U+E0103", "b": "U+845B", "active": True},
    "MJ022335": {"v": "U+845B U+E0102", "b": "U+845B", "active": True},
}
