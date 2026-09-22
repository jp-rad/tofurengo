"""
Unit tests for the GlyphInverseRenderer module.

These tests verify correct behavior for:
- brace escaping
- glyph conversion
- IVS (Ideographic Variation Sequence) handling
- mixed composite Unicode strings
"""

import pytest
from tofurengo.glyph_inverse_renderer import GlyphInverseRenderer
from tofurengo.ucs import ucs_to_glyph

# Dummy glyph table
GLYPH_TABLE = {
    "MJ022335": {"b": "U+845B", "v": "U+845B U+E0102", "active": True},
}

def _get_char_base_ivs_MJ022335():
    base_char = ucs_to_glyph("U+845B")
    assert len(base_char) == 1
    ivs_char = ucs_to_glyph("U+845B U+E0102")
    assert len(ivs_char) == 2

    return base_char, ivs_char

# ---------------------------------------------------------------------------
# Basic behavior tests
# ---------------------------------------------------------------------------

def test_no_converter_preserves_characters_and_escapes_brace():
    renderer = GlyphInverseRenderer()

    assert renderer.inverse_text("ABC") == "ABC"
    assert renderer.inverse_text("{") == "{{"
    assert renderer.inverse_text("A{B") == "A{{B"


def test_converter_converts_characters_into_tags():
    mapping = {
        "\u6f22": "MJ000001",  # U+6F22
        "\u5b57": "MJ000002",  # U+5B57
    }

    def conv(ch: str) -> str | None:
        return mapping.get(ch)

    renderer = GlyphInverseRenderer(glyph_converter=conv)

    assert renderer.inverse_text("\u6f22") == "{MJ000001}"
    assert renderer.inverse_text("\u5b57") == "{MJ000002}"
    assert renderer.inverse_text("\u6f22\u5b57") == "{MJ000001}{MJ000002}"


def test_converter_none_falls_back_to_brace_escape():
    def conv(ch: str) -> None:
        return None

    renderer = GlyphInverseRenderer(glyph_converter=conv)

    assert renderer.inverse_text("A") == "A"
    assert renderer.inverse_text("{") == "{{"
    assert renderer.inverse_text("A{B") == "A{{B"


# ---------------------------------------------------------------------------
# IVS tests
# ---------------------------------------------------------------------------

def test_ivs_conversion():
    base_char, ivs_char = _get_char_base_ivs_MJ022335()
    
    def conv(ch: str) -> str | None:
        if ch == base_char:
            return "MJ022335-BASE"
        if ch == ivs_char:
            return "MJ022335-IVS"
        return None

    renderer = GlyphInverseRenderer(glyph_converter=conv)

    assert renderer.inverse_text(base_char) == "{MJ022335-BASE}"
    assert renderer.inverse_text(ivs_char) == "{MJ022335-IVS}"


def test_ivs_mixed_text():
    base_char, ivs_char = _get_char_base_ivs_MJ022335()

    def conv(ch: str) -> str | None:
        if ch == base_char:
            return "MJ022335-BASE"
        if ch == ivs_char:
            return "MJ022335-IVS"
        return None

    renderer = GlyphInverseRenderer(glyph_converter=conv)

    input_text = ivs_char + "{" + base_char
    expected = "{MJ022335-IVS}{{{MJ022335-BASE}"

    assert renderer.inverse_text(input_text) == expected


def test_ivs_no_converter_falls_back_to_escape():
    renderer = GlyphInverseRenderer()

    base_char, ivs_char = _get_char_base_ivs_MJ022335()

    input_text = ivs_char + "{" + base_char
    expected = ivs_char + "{{" + base_char

    assert renderer.inverse_text(input_text) == expected


# ---------------------------------------------------------------------------
# Composite string tests (long sequences, mixed IVS/base/braces)
# ---------------------------------------------------------------------------

def test_composite_unicode_string():
    """
    Complex sequence combining:
    - base characters
    - IVS characters
    - braces
    - ASCII text
    """

    base_char, ivs_char = _get_char_base_ivs_MJ022335()

    def conv(ch: str) -> str | None:
        if ch == base_char:
            return "MJ022335-BASE"
        if ch == ivs_char:
            return "MJ022335-IVS"
        return None

    renderer = GlyphInverseRenderer(glyph_converter=conv)

    input_text = (
        "X" +
        base_char +
        "{" +
        ivs_char +
        "Y" +
        "{" +
        base_char +
        "Z"
    )

    # Expected breakdown:
    # X → X
    # base → {MJ022335-BASE}
    # { → {{
    # ivs → {MJ022335-IVS}
    # Y → Y
    # { → {{
    # base → {MJ022335-BASE}
    # Z → Z

    expected = (
        "X"
        "{MJ022335-BASE}"
        "{{"
        "{MJ022335-IVS}"
        "Y"
        "{{"
        "{MJ022335-BASE}"
        "Z"
    )

    assert renderer.inverse_text(input_text) == expected


def test_empty_string_returns_empty():
    renderer = GlyphInverseRenderer()
    assert renderer.inverse_text("") == ""
