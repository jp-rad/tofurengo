"""
Unicode Code Point (UCS) sequence and native glyph conversion utilities.

This module provides bidirectional conversion functions between native Unicode glyph
strings (including base characters and variation selectors) and formatted UCS code point
sequences (e.g., 'U+845B U+E0103').
"""

import re

UCS_CODEPOINT_PATTERN: re.Pattern[str] = re.compile(
    r"(?:U\+)?([0-9A-Fa-f]{4,6})",
    re.IGNORECASE,
)

# Variation Selector code point ranges (VS1-VS16, IVS / MVS / Emoji VS)
VS_RANGE: range = range(0xFE00, 0xFE0F + 1)
IVS_RANGE: range = range(0xE0100, 0xE01EF + 1)


def _validate_glyph(glyph: str) -> list[int]:
    """
    Validate that an input string represents a single valid Unicode glyph sequence.

    Args:
        glyph: Input native Unicode character or sequence.

    Returns:
        list[int]: List of integer Unicode code points.

    Raises:
        ValueError: If glyph is empty or contains multiple independent base characters.
    """
    if not glyph:
        raise ValueError("glyph_to_ucs: empty glyph is not allowed")

    codepoints = [ord(ch) for ch in glyph]

    base = codepoints[0]
    for cp in codepoints[1:]:
        if cp not in VS_RANGE and cp not in IVS_RANGE:
            raise ValueError(
                f"glyph_to_ucs: multiple independent characters detected: {glyph!r}"
            )

    return codepoints


def _parse_ucs_tokens(ucs_seq: str) -> list[int]:
    """
    Parse and validate a UCS code point sequence string.

    Args:
        ucs_seq: Formatted string containing space-separated UCS code point tokens.

    Returns:
        list[int]: List of parsed integer code points.

    Raises:
        ValueError: If sequence is empty, contains invalid hex, or is out of range.
    """
    if not ucs_seq or not ucs_seq.strip():
        raise ValueError("ucs_to_glyph: empty UCS sequence")

    tokens = ucs_seq.split()
    if not tokens:
        raise ValueError("ucs_to_glyph: no code points found")

    code_points: list[int] = []
    for token in tokens:
        match = UCS_CODEPOINT_PATTERN.fullmatch(token)
        if not match:
            raise ValueError(f"ucs_to_glyph: invalid token: {token!r}")

        hex_value = match.group(1)
        try:
            cp = int(hex_value, 16)
        except ValueError:
            raise ValueError(
                f"ucs_to_glyph: invalid hex value: {hex_value!r}"
            )

        if cp < 0 or cp > 0x10FFFF:
            raise ValueError(
                f"ucs_to_glyph: code point out of range: U+{cp:X}"
            )

        code_points.append(cp)

    return code_points


def glyph_to_ucs(glyph: str) -> str:
    """
    Convert a native Unicode glyph string into a standardized UCS code point sequence.

    Args:
        glyph: Native character string.

    Returns:
        str: Space-separated UCS code point string in 'U+XXXX' format.
    """
    codepoints = _validate_glyph(glyph)
    return " ".join(f"U+{cp:X}" for cp in codepoints)


def ucs_to_glyph(ucs_seq: str) -> str:
    """
    Convert a standardized UCS code point sequence into a native Unicode glyph string.

    Args:
        ucs_seq: Space-separated UCS sequence string.

    Returns:
        str: Native Unicode glyph string combining base character and variation selectors.
    """
    code_points = _parse_ucs_tokens(ucs_seq)
    return "".join(chr(cp) for cp in code_points)

