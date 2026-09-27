import pytest
from tofurengo.ucs import (
    glyph_to_ucs,
    ucs_to_glyph,
    _validate_glyph,
    _parse_ucs_tokens,
)

# Reference:
# MJ022335 (KATSU)
# Basic code point: U+845B
# IVS code point:   U+E0102
# Official info URL:
# https://moji.or.jp/mojikibansearch/info?MJ%E6%96%87%E5%AD%97%E5%9B%B3%E5%BD%A2%E5%90%8D=MJ022335

# ------------------------------------------------------------
# glyph_to_ucs
# ------------------------------------------------------------

def test_glyph_to_ucs_single_mj022335():
    # MJ022335 basic glyph: \u845B (KATSU)
    assert glyph_to_ucs("\u845B") == "U+845B"

def test_glyph_to_ucs_ivs_mj022335():
    # MJ022335 IVS glyph: \u845B + U+E0102 (KATSU with IVS)
    text = "\u845B\U000E0102"
    assert glyph_to_ucs(text) == "U+845B U+E0102"

def test_glyph_to_ucs_multiple_chars_error():
    # Multiple independent chars must raise: \u845B + "A"
    with pytest.raises(ValueError):
        glyph_to_ucs("\u845B" + "A")

def test_glyph_to_ucs_empty_error():
    # Empty glyph must raise
    with pytest.raises(ValueError):
        glyph_to_ucs("")


# ------------------------------------------------------------
# ucs_to_glyph
# ------------------------------------------------------------

def test_ucs_to_glyph_basic_mj022335():
    # Basic BMP code point: U+845B (KATSU)
    assert ucs_to_glyph("U+845B") == "\u845B"

def test_ucs_to_glyph_ivs_mj022335():
    # IVS sequence: U+845B U+E0102 (KATSU with IVS)
    assert ucs_to_glyph("U+845B U+E0102") == "\u845B\U000E0102"

def test_ucs_to_glyph_lowercase_and_no_uplus():
    # Lowercase hex and no U+ prefix
    assert ucs_to_glyph("845b e0102") == "\u845B\U000E0102"

def test_ucs_to_glyph_tab_and_newline():
    # Mixed whitespace (tab, newline)
    seq = "U+845B\tU+E0102\nU+E0103"
    assert ucs_to_glyph(seq) == "\u845B\U000E0102\U000E0103"

def test_ucs_to_glyph_invalid_token():
    # Invalid hex must raise
    with pytest.raises(ValueError):
        ucs_to_glyph("U+ZZZZ")

def test_ucs_to_glyph_out_of_range():
    # Out-of-range code point must raise
    with pytest.raises(ValueError):
        ucs_to_glyph("U+110000")

def test_ucs_to_glyph_empty_error():
    # Empty input must raise
    with pytest.raises(ValueError):
        ucs_to_glyph("")


# ------------------------------------------------------------
# _validate_glyph (internal)
# ------------------------------------------------------------

def test_validate_glyph_single_mj022335():
    # Single BMP char: \u845B (KATSU)
    cps = _validate_glyph("\u845B")
    assert cps == [0x845B]

def test_validate_glyph_ivs_mj022335():
    # Base char + IVS: \u845B + U+E0102 (KATSU with IVS)
    cps = _validate_glyph("\u845B\U000E0102")
    assert cps == [0x845B, 0xE0102]

def test_validate_glyph_multiple_chars_error():
    # Multiple independent chars must raise: \u845B + "A"
    with pytest.raises(ValueError):
        _validate_glyph("\u845B" + "A")

def test_validate_glyph_empty_error():
    # Empty glyph must raise
    with pytest.raises(ValueError):
        _validate_glyph("")


# ------------------------------------------------------------
# _parse_ucs_tokens (internal)
# ------------------------------------------------------------

def test_parse_ucs_tokens_basic_mj022335():
    # Basic BMP code point: U+845B (KATSU)
    cps = _parse_ucs_tokens("U+845B")
    assert cps == [0x845B]

def test_parse_ucs_tokens_ivs_mj022335():
    # IVS sequence: U+845B U+E0102 (KATSU with IVS)
    cps = _parse_ucs_tokens("U+845B U+E0102")
    assert cps == [0x845B, 0xE0102]

def test_parse_ucs_tokens_lowercase_and_no_uplus():
    # Lowercase hex and no U+ prefix
    cps = _parse_ucs_tokens("845b e0102")
    assert cps == [0x845B, 0xE0102]

def test_parse_ucs_tokens_tab_and_newline():
    # Mixed whitespace
    cps = _parse_ucs_tokens("U+845B\tU+E0102\nU+E0103")
    assert cps == [0x845B, 0xE0102, 0xE0103]

def test_parse_ucs_tokens_invalid_token():
    # Invalid token must raise
    with pytest.raises(ValueError):
        _parse_ucs_tokens("U+ZZZZ")

def test_parse_ucs_tokens_out_of_range():
    # Out-of-range code point must raise
    with pytest.raises(ValueError):
        _parse_ucs_tokens("U+110000")

def test_parse_ucs_tokens_empty_error():
    # Empty input must raise
    with pytest.raises(ValueError):
        _parse_ucs_tokens("")

